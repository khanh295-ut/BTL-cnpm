from datetime import datetime, timedelta

from jose import jwt



SECRET_KEY = "your-secret-key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60



def create_access_token(data: dict):

    payload = data.copy()


    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )


    payload["exp"] = expire


    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )