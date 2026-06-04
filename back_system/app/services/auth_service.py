from app.errors import UnauthorizedError, ValidationError
from app.models.user import SysUser
from app.utils.security import create_token


def login(data):
    username = (data or {}).get("username", "").strip()
    password = (data or {}).get("password", "")
    if not username or not password:
        raise ValidationError("账号和密码不能为空")

    user = SysUser.query.filter_by(username=username, status=1).first()
    if not user or not user.check_password(password):
        raise UnauthorizedError("账号或密码错误")

    return {"token": create_token(user), "user": user.to_public_dict()}
