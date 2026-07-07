import bcrypt
from backend.src.models.auth import User
from backend.src.services.jwt_service import create_access_token


class AuthService:

    def register(self, db, data):

        user = User(
            username=data.username,
            email=data.email,
            full_name=data.full_name
        )

        user.set_password(data.password)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def login(self, db, data):

        user = db.query(User).filter(User.email == data.email).first()

        if not user:
            return None

        if not user.check_password(data.password):
            return None

        token = create_access_token(
            {"sub": str(user.id)}
        )

        return token