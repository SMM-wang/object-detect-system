from app.extensions import db
from app.models.user import SysUser
from app.utils.security import hash_password


def seed_defaults(app):
    _seed_users()
    db.session.commit()


def _seed_users():
    users = [
        {"username": "admin", "password": "123456", "nickname": "管理员", "role": "admin"},
        {"username": "user", "password": "123456", "nickname": "普通用户", "role": "user"},
    ]
    for item in users:
        if SysUser.query.filter_by(username=item["username"]).first():
            continue
        db.session.add(
            SysUser(
                username=item["username"],
                password_hash=hash_password(item["password"]),
                nickname=item["nickname"],
                role=item["role"],
                status=1,
            )
        )
