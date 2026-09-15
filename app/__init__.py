import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import Config


load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name="development"):
    app = Flask(__name__)

    app.config.from_object(Config)

    # app.secret_key = os.environ.get('SECRET_KEY', 'unsafe_default_dev_key')

    os.makedirs(app.config['DATA_DIR'], exist_ok=True)

    from . import models
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    with app.app_context():
        db.create_all()

    # Register blueprints
    from .blueprints.main import main_bp
    app.register_blueprint(main_bp)
    from .blueprints.server_manager import server_bp
    app.register_blueprint(server_bp)

    return app
