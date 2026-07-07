from sqlalchemy.orm import Session
from backend.src.models.auth import User


class UserService:

    def get_profile(self, db: Session, user_id: str):
        return db.query(User).filter(User.id == user_id).first()

    def update_profile(self, db: Session, user_id: str, full_name=None, email=None, bio=None):

        user = db.query(User).filter(User.id == user_id).first()

        if full_name:
            user.full_name = full_name

        if email:
            user.email = email

        if bio:
            user.bio = bio

        db.commit()
        db.refresh(user)

        return user

    def change_password(self, db: Session, user: User, new_password: str):

        user.set_password(new_password)
        db.commit()

        return True