from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.auth import User


class UserService:

    # ======================================
    # CREATE USER
    # ======================================
    def create_user(
        self,
        db: Session,
        username: str,
        email: str,
        password: str,
        full_name: str = None,
        bio: str = None,
    ):

        if db.query(User).filter(User.username == username).first():
            raise ValueError("Username already exists.")

        if db.query(User).filter(User.email == email).first():
            raise ValueError("Email already exists.")

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            bio=bio,
        )

        user.set_password(password)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    # ======================================
    # GET ALL USERS
    # ======================================
    def get_all_users(
        self,
        db: Session,
    ):

        return db.query(User).all()

    # ======================================
    # GET USER BY ID
    # ======================================
    def get_profile(
        self,
        db: Session,
        user_id: UUID,
    ):

        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    # ======================================
    # GET USER BY USERNAME
    # ======================================
    def get_by_username(
        self,
        db: Session,
        username: str,
    ):

        return (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

    # ======================================
    # GET USER BY EMAIL
    # ======================================
    def get_by_email(
        self,
        db: Session,
        email: str,
    ):

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    # ======================================
    # UPDATE PROFILE
    # ======================================
    def update_profile(
        self,
        db: Session,
        user_id: UUID,
        full_name: str = None,
        email: str = None,
        bio: str = None,
    ):

        user = self.get_profile(db, user_id)

        if not user:
            return None

        if email:

            exist = (
                db.query(User)
                .filter(
                    User.email == email,
                    User.id != user_id,
                )
                .first()
            )

            if exist:
                raise ValueError("Email already exists.")

            user.email = email

        if full_name is not None:
            user.full_name = full_name

        if bio is not None:
            user.bio = bio

        db.commit()
        db.refresh(user)

        return user

    # ======================================
    # CHANGE PASSWORD
    # ======================================
    def change_password(
        self,
        db: Session,
        user: User,
        new_password: str,
    ):

        user.set_password(new_password)

        db.commit()
        db.refresh(user)

        return True

    # ======================================
    # DELETE USER
    # ======================================
    def delete_user(
        self,
        db: Session,
        user_id: UUID,
    ):

        user = self.get_profile(db, user_id)

        if not user:
            return False

        db.delete(user)
        db.commit()

        return True

    # ======================================
    # SEARCH USER
    # ======================================
    def search_users(
        self,
        db: Session,
        keyword: str,
    ):

        return (
            db.query(User)
            .filter(
                User.username.ilike(f"%{keyword}%")
            )
            .all()
        )