import uuid
from decimal import Decimal


def generate_uuid():
    return str(uuid.uuid4())


def to_float(value):

    if isinstance(value, Decimal):
        return float(value)

    return value


def success_response(
    message,
    data=None,
):

    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message,
):

    return {
        "success": False,
        "message": message,
    }