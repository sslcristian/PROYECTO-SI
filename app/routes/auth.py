from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, bcrypt
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.auditoria import Auditoria

auth_bp = Blueprint('auth', __name__)

def registrar_auditoria(accion, modulo, descripcion, usuario_id=None):
    try:
        a = Auditoria(
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            direccion_ip=request.remote_addr,
            usuario_id=usuario_id
        )
        db.session.add(a)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error auditoria: {e}")

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        u_input = request.form.get('usuario')
        p_input = request.form.get('contrasena')

        usuario = Usuario.query.filter(
            (Usuario.nombre_usuario == u_input) | (Usuario.correo == u_input)
        ).first()

        if usuario and bcrypt.check_password_hash(usuario.contrasena, p_input):
            if usuario.estado != 'ACTIVO':
                flash('Usuario inactivo. Contacte al administrador.', 'danger')
                return redirect(url_for('auth.login'))

            login_user(usuario)
            registrar_auditoria('LOGIN', 'Autenticación',
                                f'Inicio de sesión de {usuario.nombre_usuario}',
                                usuario.id)
            flash(f'Bienvenido, {usuario.nombres}', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Credenciales incorrectas.', 'danger')
            registrar_auditoria('LOGIN_FALLIDO', 'Autenticación',
                                f'Intento fallido con: {u_input}')

    return render_template('auth/login.html')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        datos = request.form

        if Usuario.query.filter_by(correo=datos.get('correo')).first():
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('auth.registro'))

        if Usuario.query.filter_by(nombre_usuario=datos.get('nombre_usuario')).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('auth.registro'))

        nuevo = Usuario(
            nombres=datos.get('nombres'),
            apellidos=datos.get('apellidos'),
            documento=datos.get('documento'),
            correo=datos.get('correo'),
            telefono=datos.get('telefono'),
            nombre_usuario=datos.get('nombre_usuario'),
            contrasena=bcrypt.generate_password_hash(datos.get('contrasena')).decode('utf-8'),
            estado='ACTIVO',
            rol_id=int(datos.get('rol_id', 4))
        )
        db.session.add(nuevo)
        db.session.commit()

        registrar_auditoria('REGISTRO', 'Usuarios',
                            f'Usuario registrado: {nuevo.nombre_usuario}',
                            nuevo.id)

        flash('Usuario registrado exitosamente.', 'success')
        return redirect(url_for('auth.login'))

    roles = Rol.query.all()
    return render_template('auth/registro.html', roles=roles)

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/index.html', usuario=current_user)

@auth_bp.route('/logout')
@login_required
def logout():
    registrar_auditoria('LOGOUT', 'Autenticación',
                        f'Cierre de sesión de {current_user.nombre_usuario}',
                        current_user.id)
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))