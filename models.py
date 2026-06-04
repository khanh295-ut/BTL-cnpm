from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="User")
    full_name = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.String(500), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "Admin"


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("reset_tokens", lazy=True))

    def is_valid(self):
        return datetime.utcnow() < self.expires_at

    @classmethod
    def create_for_user(cls, user, token, expires_in_minutes=30):
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        return cls(user_id=user.id, token=token, expires_at=expires_at)
