from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, bcrypt, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debes iniciar sesión para acceder.'
    login_manager.login_message_category = 'info'

    from app.models import rol, usuario, proyecto, tarea, avance, evidencia, historial_asignacion, auditoria

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app