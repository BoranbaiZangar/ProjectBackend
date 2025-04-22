from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # ← Вот правильный способ

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Регистрация маршрутов
    from routes.auth import auth
    from routes.character import character
    from routes.projects import projects

    app.register_blueprint(auth)
    app.register_blueprint(character)
    app.register_blueprint(projects)

    return app
