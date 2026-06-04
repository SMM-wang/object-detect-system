from pathlib import Path

from flask import Flask

from app.config import Config
from app.errors import register_error_handlers
from app.extensions import db
from app.inference.detector_manager import DetectorManager
from app.routes import register_blueprints
from app.seed import seed_defaults


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.config["UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    register_error_handlers(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()
        seed_defaults(app)
        app.detector_manager = DetectorManager(app.config)
        app.detector_manager.initialize()

    return app
