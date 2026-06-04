from app.routes.auth import auth_bp
from app.routes.detect import detect_bp
from app.routes.records import records_bp
from app.routes.statistics import statistics_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(detect_bp, url_prefix="/api/v1/detect")
    app.register_blueprint(records_bp, url_prefix="/api/v1/records")
    app.register_blueprint(statistics_bp, url_prefix="/api/v1/statistics")
