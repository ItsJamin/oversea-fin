from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name="development"):
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    # app.secret_key = os.environ.get('SECRET_KEY', 'unsafe_default_dev_key')

    from . import models
    with app.app_context():
        db.create_all()

    # Register blueprints
    from .blueprints.main import main_bp
    app.register_blueprint(main_bp)

    return app
