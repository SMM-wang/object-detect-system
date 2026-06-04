from datetime import datetime

from app.extensions import db


ID_TYPE = db.BigInteger().with_variant(db.Integer, "sqlite")


class DetectLog(db.Model):
    __tablename__ = "detect_log"

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    user_id = db.Column(ID_TYPE, db.ForeignKey("sys_user.id"), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(32), nullable=False)
    file_hash = db.Column(db.String(128), nullable=False)
    model_version = db.Column(db.String(64), nullable=False, index=True)
    confidence = db.Column(db.Numeric(4, 3), nullable=False)
    iou = db.Column(db.Numeric(4, 3), nullable=False)
    result_json = db.Column(db.JSON)
    analysis_text = db.Column(db.Text)
    object_count = db.Column(db.Integer, nullable=False, default=0)
    elapsed_ms = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(32), nullable=False, index=True)
    error_msg = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = db.relationship("SysUser", backref="detect_logs")
