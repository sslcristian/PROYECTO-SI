from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def rol_requerido(*roles_permitidos):
    """Decorador que restringe el acceso según el rol del usuario."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.rol.nombre not in roles_permitidos:
                flash('No tienes permisos para acceder a este módulo.', 'danger')
                return redirect(url_for('auth.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator