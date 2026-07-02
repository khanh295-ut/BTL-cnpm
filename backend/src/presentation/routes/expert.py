from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session


from backend.src.config.database import get_db

from backend.src.schemas.expert import (
    ExpertCreate,
    ExpertUpdate,
    ExpertResponse
)

from backend.src.services import expert_service



router = APIRouter(
    prefix="/experts",
    tags=["Expert Management"]
)



# =========================
# CREATE EXPERT PROFILE
# =========================

@router.post(
    "/",
    response_model=ExpertResponse
)
def create_expert(
    data: ExpertCreate,
    db: Session = Depends(get_db)
):

    return expert_service.create_expert(
        db,
        data
    )



# =========================
# GET ALL EXPERTS
# =========================

@router.get(
    "/",
    response_model=list[ExpertResponse]
)
def get_experts(
    db: Session = Depends(get_db)
):

    return expert_service.get_all_experts(
        db
    )



# =========================
# SEARCH EXPERT
# =========================

@router.get(
    "/search",
    response_model=list[ExpertResponse]
)
def search_experts(
    keyword:str = Query(...),
    db:Session = Depends(get_db)
):

    return expert_service.search_expert(
        db,
        keyword
    )



# =========================
# GET DETAIL
# =========================

@router.get(
    "/{expert_id}",
    response_model=ExpertResponse
)
def get_detail(
    expert_id:int,
    db:Session=Depends(get_db)
):

    expert = expert_service.get_expert(
        db,
        expert_id
    )


    if not expert:

        raise HTTPException(
            status_code=404,
            detail="Expert not found"
        )


    return expert



# =========================
# UPDATE PROFILE
# =========================

@router.put(
    "/{expert_id}",
    response_model=ExpertResponse
)
def update_expert(
    expert_id:int,
    data:ExpertUpdate,
    db:Session=Depends(get_db)
):

    expert = expert_service.update_expert(
        db,
        expert_id,
        data
    )


    if not expert:

        raise HTTPException(
            status_code=404,
            detail="Expert not found"
        )


    return expert



# =========================
# DELETE EXPERT
# =========================

@router.delete(
    "/{expert_id}"
)
def delete_expert(
    expert_id:int,
    db:Session=Depends(get_db)
):

    expert = expert_service.delete_expert(
        db,
        expert_id
    )


    if not expert:

        raise HTTPException(
            status_code=404,
            detail="Expert not found"
        )


    return {
        "message":
        "Expert deleted successfully"
    }