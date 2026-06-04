from functools import wraps

import jwt
from flask import g, request

from app.errors import ForbiddenError, UnauthorizedError
from app.models.user import SysUser
from app.utils.security import decode_token


def _extract_bearer_token():
    value = request.headers.get("Authorization", "")
    if not value.startswith("Bearer "):
        raise UnauthorizedError()
    token = value.removeprefix("Bearer ").strip()
    if not token:
        raise UnauthorizedError()
    return token


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        try:
            payload = decode_token(_extract_bearer_token())
        except jwt.PyJWTError as exc:
            raise UnauthorizedError() from exc
        try:
            user_id = int(payload.get("sub"))
        except (TypeError, ValueError) as exc:
            raise UnauthorizedError() from exc
        user = SysUser.query.get(user_id)
        if not user or user.status != 1:
            raise UnauthorizedError()
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.current_user.role not in roles:
                raise ForbiddenError()
            return view(*args, **kwargs)

        return wrapped

    return decorator


def current_user():
    return getattr(g, "current_user", None)
