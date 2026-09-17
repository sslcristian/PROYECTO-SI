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

    # Importar modelos para que SQLAlchemy los registre
    from app.models import rol, usuario, proyecto, tarea, avance, evidencia, historial_asignacion, auditoria

    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.proyectos import proyectos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(proyectos_bp)

    # Filtros de Jinja2 útiles
    @app.template_filter('fecha')
    def formato_fecha(value):
        if value:
            return value.strftime('%d/%m/%Y')
        return ''

    return app