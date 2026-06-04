from datetime import datetime

from app.extensions import db
from app.utils.security import check_password


ID_TYPE = db.BigInteger().with_variant(db.Integer, "sqlite")


class SysUser(db.Model):
    __tablename__ = "sys_user"

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(64))
    role = db.Column(db.String(32), nullable=False, default="user")
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def check_password(self, password):
        return check_password(password, self.password_hash)

    def to_public_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "role": self.role,
        }
