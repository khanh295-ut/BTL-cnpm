from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.src.models.ai_service import AIService
from backend.src.models.contract import Contract
from backend.src.models.deliverable import Deliverable
from backend.src.models.enterprise import Enterprise
from backend.src.models.escrow import Escrow
from backend.src.models.expert import Expert
from backend.src.models.payment import Payment
from backend.src.models.service_order import ServiceOrder
from backend.src.models.wallet import Wallet
from backend.src.schemas.service_order import (
    ServiceOrderCancelRequest,
    ServiceOrderCompleteRequest,
    ServiceOrderConfirmRequest,
    ServiceOrderCreate,
    ServiceOrderDeliverRequest,
    ServiceOrderDisputeRequest,
    ServiceOrderStartRequest,
    ServiceOrderStatusUpdate,
    ServiceOrderUpdate,
)
from backend.src.services.escrow_service import (
    escrow_service,
)


logger = logging.getLogger(
    "AITasker.ServiceOrderService"
)


class ServiceOrderService:
    """
    Quản lý đơn đặt dịch vụ AI trên Marketplace.

    Luồng chính:

        PENDING
            ↓ confirm
        CONFIRMED
            ↓ start
        IN_PROGRESS
            ↓ deliver
        DELIVERED
            ↓ complete
        COMPLETED

    Luồng khác:

        PENDING / CONFIRMED
            ↓ cancel
        CANCELLED

        CONFIRMED / IN_PROGRESS / DELIVERED
            ↓ dispute
        DISPUTED
    """

    ALLOWED_STATUSES = {
        "PENDING",
        "CONFIRMED",
        "IN_PROGRESS",
        "DELIVERED",
        "COMPLETED",
        "DISPUTED",
        "CANCELLED",
        "REFUNDED",
    }

    FINAL_STATUSES = {
        "COMPLETED",
        "CANCELLED",
        "REFUNDED",
    }

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _decimal(value) -> Decimal:
        if value is None:
            return Decimal("0.00")

        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    @staticmethod
    def _normalize_status(
        value: str | None,
    ) -> str:
        return str(
            value or ""
        ).strip().upper()

    @staticmethod
    def _normalize_currency(
        value: str | None,
    ) -> str:
        normalized = str(
            value or "VND"
        ).strip().upper()

        return normalized or "VND"

    @staticmethod
    def _clean_text(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None

    @staticmethod
    def _append_note(
        current_note: str | None,
        new_note: str | None,
    ) -> str | None:
        new_value = ServiceOrderService._clean_text(
            new_note
        )

        if not new_value:
            return current_note

        current_value = ServiceOrderService._clean_text(
            current_note
        )

        if not current_value:
            return new_value

        return f"{current_value}\n{new_value}"

    # ======================================================
    # ENTITY HELPERS
    # ======================================================

    def _get_service(
        self,
        db: Session,
        service_id: UUID,
        *,
        for_update: bool = False,
    ) -> AIService:
        query = (
            db.query(AIService)
            .filter(AIService.id == service_id)
        )

        if for_update:
            query = query.with_for_update()

        service = query.first()

        if service is None:
            raise ValueError(
                "AI service not found."
            )

        return service

    def _get_enterprise(
        self,
        db: Session,
        enterprise_id: UUID,
    ) -> Enterprise:
        enterprise = (
            db.query(Enterprise)
            .filter(
                Enterprise.id == enterprise_id
            )
            .first()
        )

        if enterprise is None:
            raise ValueError(
                "Enterprise not found."
            )

        return enterprise

    def _get_expert(
        self,
        db: Session,
        expert_id: UUID,
    ) -> Expert:
        expert = (
            db.query(Expert)
            .filter(
                Expert.id == expert_id
            )
            .first()
        )

        if expert is None:
            raise ValueError(
                "Expert not found."
            )

        return expert

    def _get_order_for_update(
        self,
        db: Session,
        order_id: UUID,
    ) -> ServiceOrder:
        order = (
            db.query(ServiceOrder)
            .filter(
                ServiceOrder.id == order_id
            )
            .with_for_update()
            .first()
        )

        if order is None:
            raise ValueError(
                "Service order not found."
            )

        return order

    def _get_payment(
        self,
        db: Session,
        payment_id: UUID | None,
    ) -> Payment | None:
        if payment_id is None:
            return None

        payment = (
            db.query(Payment)
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

        if payment is None:
            raise ValueError(
                "Payment not found."
            )

        return payment

    def _get_wallet(
        self,
        db: Session,
        wallet_id: UUID | None,
    ) -> Wallet | None:
        if wallet_id is None:
            return None

        wallet = (
            db.query(Wallet)
            .filter(
                Wallet.id == wallet_id
            )
            .first()
        )

        if wallet is None:
            raise ValueError(
                "Wallet not found."
            )

        return wallet

    def _get_deliverable(
        self,
        db: Session,
        deliverable_id: UUID | None,
    ) -> Deliverable | None:
        if deliverable_id is None:
            return None

        deliverable = (
            db.query(Deliverable)
            .filter(
                Deliverable.id == deliverable_id
            )
            .first()
        )

        if deliverable is None:
            raise ValueError(
                "Deliverable not found."
            )

        return deliverable

    # ======================================================
    # VALIDATION
    # ======================================================

    def _ensure_status(
        self,
        order: ServiceOrder,
        allowed_statuses: set[str],
        message: str,
    ) -> None:
        current_status = self._normalize_status(
            order.status
        )

        if current_status not in allowed_statuses:
            raise ValueError(message)

    def _validate_service_for_order(
        self,
        service: AIService,
    ) -> None:
        status = self._normalize_status(
            service.status
        )

        if status != "PUBLISHED":
            raise ValueError(
                "Only published AI services can be ordered."
            )

        if self._decimal(
            service.price
        ) < Decimal("0"):
            raise ValueError(
                "AI service price is invalid."
            )

        if int(
            service.delivery_days or 0
        ) <= 0:
            raise ValueError(
                "AI service delivery days are invalid."
            )

    def _link_existing_contract_and_escrow(
        self,
        db: Session,
        *,
        order: ServiceOrder,
        payment: Payment | None,
        payer_wallet: Wallet | None,
    ) -> None:
        """
        Liên kết Payment → Contract → Escrow đã tồn tại.

        Model Contract hiện bắt buộc có project_id, trong khi
        ServiceOrder chưa có project_id. Vì vậy service này
        không tự tạo Contract giả. Nó chỉ liên kết Contract
        thông qua Payment nếu Payment đã tồn tại.
        """

        if payment is None:
            return

        contract_id = getattr(
            payment,
            "contract_id",
            None,
        )

        if contract_id is None:
            raise ValueError(
                "Payment is not linked to a contract."
            )

        contract = (
            db.query(Contract)
            .filter(
                Contract.id == contract_id
            )
            .first()
        )

        if contract is None:
            raise ValueError(
                "Contract linked to payment was not found."
            )

        if contract.expert_id != order.expert_id:
            raise ValueError(
                "Contract expert does not match order expert."
            )

        order.contract_id = contract.id

        escrow = (
            db.query(Escrow)
            .filter(
                Escrow.contract_id == contract.id
            )
            .first()
        )

        if escrow is None:
            return

        if (
            payer_wallet is not None
            and escrow.payer_wallet_id
            != payer_wallet.id
        ):
            raise ValueError(
                "Payer wallet does not match escrow payer wallet."
            )

        order.escrow_id = escrow.id

    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[ServiceOrder]:
        return (
            db.query(ServiceOrder)
            .options(
                joinedload(
                    ServiceOrder.service
                ),
                joinedload(
                    ServiceOrder.enterprise
                ),
                joinedload(
                    ServiceOrder.expert
                ),
            )
            .order_by(
                ServiceOrder.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        order_id: UUID,
    ) -> ServiceOrder | None:
        return (
            db.query(ServiceOrder)
            .options(
                joinedload(
                    ServiceOrder.service
                ),
                joinedload(
                    ServiceOrder.enterprise
                ),
                joinedload(
                    ServiceOrder.expert
                ),
                joinedload(
                    ServiceOrder.contract
                ),
                joinedload(
                    ServiceOrder.escrow
                ),
            )
            .filter(
                ServiceOrder.id == order_id
            )
            .first()
        )

    # ======================================================
    # GET BY ENTERPRISE
    # ======================================================

    def get_by_enterprise(
        self,
        db: Session,
        enterprise_id: UUID,
    ) -> list[ServiceOrder]:
        return (
            db.query(ServiceOrder)
            .filter(
                ServiceOrder.enterprise_id
                == enterprise_id
            )
            .order_by(
                ServiceOrder.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY EXPERT
    # ======================================================

    def get_by_expert(
        self,
        db: Session,
        expert_id: UUID,
    ) -> list[ServiceOrder]:
        return (
            db.query(ServiceOrder)
            .filter(
                ServiceOrder.expert_id
                == expert_id
            )
            .order_by(
                ServiceOrder.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY SERVICE
    # ======================================================

    def get_by_service(
        self,
        db: Session,
        service_id: UUID,
    ) -> list[ServiceOrder]:
        return (
            db.query(ServiceOrder)
            .filter(
                ServiceOrder.service_id
                == service_id
            )
            .order_by(
                ServiceOrder.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY STATUS
    # ======================================================

    def get_by_status(
        self,
        db: Session,
        status: str,
    ) -> list[ServiceOrder]:
        normalized_status = self._normalize_status(
            status
        )

        if normalized_status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "Invalid service order status."
            )

        return (
            db.query(ServiceOrder)
            .filter(
                ServiceOrder.status
                == normalized_status
            )
            .order_by(
                ServiceOrder.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: ServiceOrderCreate,
    ) -> ServiceOrder:
        try:
            service = self._get_service(
                db=db,
                service_id=data.service_id,
                for_update=True,
            )

            self._validate_service_for_order(
                service
            )

            enterprise = self._get_enterprise(
                db=db,
                enterprise_id=data.enterprise_id,
            )

            expert = self._get_expert(
                db=db,
                expert_id=service.expert_id,
            )

            now = datetime.utcnow()

            order = ServiceOrder(
                service_id=service.id,
                enterprise_id=enterprise.id,
                expert_id=expert.id,
                contract_id=None,
                escrow_id=None,
                service_title=service.title,
                price=self._decimal(
                    service.price
                ),
                currency=self._normalize_currency(
                    service.currency
                ),
                delivery_days=int(
                    service.delivery_days
                ),
                revision_count=int(
                    service.revision_count or 0
                ),
                requirements=self._clean_text(
                    data.requirements
                ),
                note=self._clean_text(
                    data.note
                ),
                cancellation_reason=None,
                status="PENDING",
                created_at=now,
                updated_at=now,
            )

            db.add(order)
            db.commit()
            db.refresh(order)

            logger.info(
                "Service order %s created for AI service %s.",
                order.id,
                service.id,
            )

            return order

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo service order."
            )

            raise

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        order_id: UUID,
        data: ServiceOrderUpdate,
    ) -> ServiceOrder | None:
        order = self.get_by_id(
            db=db,
            order_id=order_id,
        )

        if order is None:
            return None

        try:
            self._ensure_status(
                order,
                {"PENDING"},
                "Only pending orders can be updated.",
            )

            update_data = data.model_dump(
                exclude_unset=True
            )

            if "requirements" in update_data:
                order.requirements = self._clean_text(
                    update_data["requirements"]
                )

            if "note" in update_data:
                order.note = self._clean_text(
                    update_data["note"]
                )

            order.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(order)

            return order

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật service order %s.",
                order_id,
            )

            raise

    # ======================================================
    # CONFIRM
    # ======================================================

    def confirm(
        self,
        db: Session,
        order_id: UUID,
        data: ServiceOrderConfirmRequest,
    ) -> ServiceOrder:
        try:
            order = self._get_order_for_update(
                db=db,
                order_id=order_id,
            )

            self._ensure_status(
                order,
                {"PENDING"},
                "Only pending orders can be confirmed.",
            )

            payment = self._get_payment(
                db=db,
                payment_id=data.payment_id,
            )

            payer_wallet = self._get_wallet(
                db=db,
                wallet_id=data.payer_wallet_id,
            )

            self._link_existing_contract_and_escrow(
                db=db,
                order=order,
                payment=payment,
                payer_wallet=payer_wallet,
            )

            now = datetime.utcnow()

            order.status = "CONFIRMED"
            order.confirmed_at = now
            order.updated_at = now
            order.note = self._append_note(
                order.note,
                data.note,
            )

            db.commit()
            db.refresh(order)

            logger.info(
                "Service order %s confirmed.",
                order.id,
            )

            return order

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xác nhận service order %s.",
                order_id,
            )

            raise

    # ======================================================
    # START
    # ======================================================

    def start(
        self,
        db: Session,
        order_id: UUID,
        data: ServiceOrderStartRequest,
    ) -> ServiceOrder:
        try:
            order = self._get_order_for_update(
                db=db,
                order_id=order_id,
            )

            self._ensure_status(
                order,
                {"CONFIRMED"},
                "Only confirmed orders can be started.",
            )

            now = datetime.utcnow()

            order.status = "IN_PROGRESS"
            order.started_at = now
            order.updated_at = now
            order.note = self._append_note(
                order.note,
                data.note,
            )

            db.commit()
            db.refresh(order)

            return order

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể bắt đầu service order %s.",
                order_id,
            )

            raise

    # ======================================================
    # DELIVER
    # ======================================================

    def deliver(
        self,
        db: Session,
        order_id: UUID,
        data: ServiceOrderDeliverRequest,
    ) -> ServiceOrder:
        try:
            order = self._get_order_for_update(
                db=db,
                order_id=order_id,
            )

            self._ensure_status(
                order,
                {"IN_PROGRESS"},
                "Only in-progress orders can be delivered.",
            )

            deliverable = self._get_deliverable(
                db=db,
                deliverable_id=data.deliverable_id,
            )

            note = data.note

            if deliverable is not None:
                deliverable_note = (
                    f"Deliverable ID: {deliverable.id}"
                )

                note = self._append_note(
                    note,
                    deliverable_note,
                )

            now = datetime.utcnow()

            order.status = "DELIVERED"
            order.delivered_at = now
            order.updated_at = now
            order.note = self._append_note(
                order.note,
                note,
            )

            db.commit()
            db.refresh(order)

            return order

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể giao service order %s.",
                order_id,
            )

            raise

    # ======================================================
    # COMPLETE
    # ======================================================

    def complete(
        self,
        db: Session,
        order_id: UUID,
        data: ServiceOrderCompleteRequest,
    ) -> ServiceOrder:
        order = self.get_by_id(
            db=db,
            order_id=order_id,
        )

        if order is None:
            raise ValueError(
                "Service order not found."
            )

        self._ensure_status(
            order,
            {"DELIVERED"},
            "Only delivered orders can be completed.",
        )

        try:
            if (
                data.release_escrow
                and order.escrow_id is not None
            ):
                escrow_service.release_all(
                    db=db,
                    escrow_id=order.escrow_id,
                    note=(
                        data.note
                        or (
                            "Giải ngân khi hoàn thành "
                            f"service order {order.id}."
                        )
                    ),
                )

            order = self._get_order_for_update(
                db=db,
                order_id=order_id,
            )

            service = self._get_service(
                db=db,
                service_id=order.service_id,
                for_update=True,
            )

            now = datetime.utcnow()

            order.status = "COMPLETED"
            order.completed_at = now
            order.updated_at = now
            order.note = self._append_note(
                order.note,
                data.note,
            )

            service.order_count = int(
                service.order_count or 0
            ) + 1

            service.updated_at = now

            db.commit()
            db.refresh(order)

            logger.info(
                "Service order %s completed.",
                order.id,
            )

            return order

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể hoàn thành service order %s.",
                order_id,
            )

            raise

    # ======================================================
    # CANCEL
    # ======================================================

    def cancel(
        self,
        db: Session,
        order_id: UUID,
        data: ServiceOrderCancelRequest,
    ) -> ServiceOrder:
        order = self.get_by_id(
            db=db,
            order_id=order_id,
        )

        if order is None:
            raise ValueError(
                "Service order not found."
            )

        self._ensure_status(
            order,
            {
                "PENDING",
                "CONFIRMED",
                "IN_PROGRESS",
            },
            (
                "Only pending, confirmed, or in-progress "
                "orders can be cancelled."
            ),
        )

        try:
            refunded = False

            if (
                data.refund_escrow
                and order.escrow_id is not None
            ):
                escrow_service.refund_all(
                    db=db,
                    escrow_id=order.escrow_id,
                    note=data.cancellation_reason,
                )

                refunded = True

            order = self._get_order_for_update(
                db=db,
                order_id=order_id,
            )

            now = datetime.utcnow()

            order.status = (
                "REFUNDED"
                if refunded
                else "CANCELLED"
            )

            order.cancellation_reason = (
                data.cancellation_reason
            )

            order.cancelled_at = now
            order.updated_at = now

            db.commit()
            db.refresh(order)

            return order

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể hủy service order %s.",
                order_id,
            )

            raise

    # ======================================================
    # DISPUTE
    # ======================================================

    def dispute(
        self,
        db: Session,
        order_id: UUID,
        data: ServiceOrderDisputeRequest,
    ) -> ServiceOrder:
        order = self.get_by_id(
            db=db,
            order_id=order_id,
        )

        if order is None:
            raise ValueError(
                "Service order not found."
            )

        self._ensure_status(
            order,
            {
                "CONFIRMED",
                "IN_PROGRESS",
                "DELIVERED",
            },
            (
                "Only confirmed, in-progress, or delivered "
                "orders can be disputed."
            ),
        )

        try:
            if order.escrow_id is not None:
                escrow_service.update_status(
                    db=db,
                    escrow_id=order.escrow_id,
                    status="DISPUTED",
                    note=data.description,
                )

            order = self._get_order_for_update(
                db=db,
                order_id=order_id,
            )

            dispute_note = (
                f"Dispute reason: {data.reason}\n"
                f"Description: {data.description}"
            )

            if data.evidence_url:
                dispute_note += (
                    f"\nEvidence: {data.evidence_url}"
                )

            order.status = "DISPUTED"
            order.note = self._append_note(
                order.note,
                dispute_note,
            )
            order.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(order)

            return order

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể mở tranh chấp cho order %s.",
                order_id,
            )

            raise

    # ======================================================
    # UPDATE STATUS
    # ======================================================

    def update_status(
        self,
        db: Session,
        order_id: UUID,
        data: ServiceOrderStatusUpdate,
    ) -> ServiceOrder:
        order = self.get_by_id(
            db=db,
            order_id=order_id,
        )

        if order is None:
            raise ValueError(
                "Service order not found."
            )

        new_status = self._normalize_status(
            data.status
        )

        if new_status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "Invalid service order status."
            )

        current_status = self._normalize_status(
            order.status
        )

        allowed_transitions = {
            "PENDING": {
                "CONFIRMED",
                "CANCELLED",
            },
            "CONFIRMED": {
                "IN_PROGRESS",
                "DISPUTED",
                "CANCELLED",
            },
            "IN_PROGRESS": {
                "DELIVERED",
                "DISPUTED",
                "CANCELLED",
            },
            "DELIVERED": {
                "COMPLETED",
                "DISPUTED",
            },
            "DISPUTED": {
                "IN_PROGRESS",
                "COMPLETED",
                "REFUNDED",
                "CANCELLED",
            },
            "COMPLETED": set(),
            "CANCELLED": set(),
            "REFUNDED": set(),
        }

        if (
            new_status != current_status
            and new_status
            not in allowed_transitions.get(
                current_status,
                set(),
            )
        ):
            raise ValueError(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}."
            )

        try:
            now = datetime.utcnow()

            order.status = new_status
            order.updated_at = now
            order.note = self._append_note(
                order.note,
                data.note,
            )

            if new_status == "CONFIRMED":
                order.confirmed_at = (
                    order.confirmed_at or now
                )

            elif new_status == "IN_PROGRESS":
                order.started_at = (
                    order.started_at or now
                )

            elif new_status == "DELIVERED":
                order.delivered_at = (
                    order.delivered_at or now
                )

            elif new_status == "COMPLETED":
                order.completed_at = (
                    order.completed_at or now
                )

            elif new_status in {
                "CANCELLED",
                "REFUNDED",
            }:
                order.cancelled_at = (
                    order.cancelled_at or now
                )

            db.commit()
            db.refresh(order)

            return order

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật trạng thái order %s.",
                order_id,
            )

            raise

    # ======================================================
    # SUMMARY
    # ======================================================

    def summary(
        self,
        db: Session,
    ) -> dict:
        rows = (
            db.query(
                ServiceOrder.status,
                func.count(
                    ServiceOrder.id
                ).label("total"),
            )
            .group_by(
                ServiceOrder.status
            )
            .all()
        )

        counts = {
            self._normalize_status(status): int(
                total or 0
            )
            for status, total in rows
        }

        total_orders = sum(
            counts.values()
        )

        total_order_value = (
            db.query(
                func.coalesce(
                    func.sum(
                        ServiceOrder.price
                    ),
                    0,
                )
            )
            .scalar()
        )

        return {
            "total_orders": total_orders,
            "pending_orders": counts.get(
                "PENDING",
                0,
            ),
            "confirmed_orders": counts.get(
                "CONFIRMED",
                0,
            ),
            "in_progress_orders": counts.get(
                "IN_PROGRESS",
                0,
            ),
            "delivered_orders": counts.get(
                "DELIVERED",
                0,
            ),
            "completed_orders": counts.get(
                "COMPLETED",
                0,
            ),
            "disputed_orders": counts.get(
                "DISPUTED",
                0,
            ),
            "cancelled_orders": counts.get(
                "CANCELLED",
                0,
            ),
            "refunded_orders": counts.get(
                "REFUNDED",
                0,
            ),
            "total_order_value": self._decimal(
                total_order_value
            ),
        }

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        order_id: UUID,
    ) -> bool:
        order = self.get_by_id(
            db=db,
            order_id=order_id,
        )

        if order is None:
            return False

        try:
            current_status = self._normalize_status(
                order.status
            )

            if current_status not in {
                "PENDING",
                "CANCELLED",
            }:
                raise ValueError(
                    "Only pending or cancelled orders "
                    "can be deleted."
                )

            if (
                order.contract_id is not None
                or order.escrow_id is not None
            ):
                raise ValueError(
                    "Order linked to contract or escrow "
                    "cannot be deleted."
                )

            db.delete(order)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa service order %s.",
                order_id,
            )

            raise


service_order_service = ServiceOrderService()