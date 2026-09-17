from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db, bcrypt
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.auditoria import Auditoria
from app.utils.decorators import rol_requerido

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


def registrar_auditoria(accion, descripcion, usuario_id=None):
    try:
        a = Auditoria(
            accion=accion,
            modulo='Usuarios',
            descripcion=descripcion,
            direccion_ip=request.remote_addr,
            usuario_id=usuario_id or (current_user.id if current_user.is_authenticated else None)
        )
        db.session.add(a)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error auditoria: {e}")


@usuarios_bp.route('/')
@login_required
@rol_requerido('ADMINISTRADOR')
def index():
    usuarios = Usuario.query.order_by(Usuario.nombres).all()
    return render_template('usuarios/index.html', usuarios=usuarios)


@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_requerido('ADMINISTRADOR')
def nuevo():
    roles = Rol.query.all()

    if request.method == 'POST':
        datos = request.form

        if Usuario.query.filter_by(correo=datos.get('correo')).first():
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('usuarios.nuevo'))

        if Usuario.query.filter_by(nombre_usuario=datos.get('nombre_usuario')).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('usuarios.nuevo'))

        if Usuario.query.filter_by(documento=datos.get('documento')).first():
            flash('El documento ya está registrado.', 'danger')
            return redirect(url_for('usuarios.nuevo'))

        nuevo_usuario = Usuario(
            nombres=datos.get('nombres'),
            apellidos=datos.get('apellidos'),
            documento=datos.get('documento'),
            correo=datos.get('correo'),
            telefono=datos.get('telefono'),
            nombre_usuario=datos.get('nombre_usuario'),
            contrasena=bcrypt.generate_password_hash(datos.get('contrasena')).decode('utf-8'),
            estado=datos.get('estado', 'ACTIVO'),
            rol_id=int(datos.get('rol_id'))
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        registrar_auditoria('CREAR_USUARIO',
                            f'Usuario creado: {nuevo_usuario.nombre_usuario}',
                            current_user.id)
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template('usuarios/form.html', usuario=None, roles=roles)


@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('ADMINISTRADOR')
def editar(id):
    usuario = Usuario.query.get_or_404(id)
    roles = Rol.query.all()

    if request.method == 'POST':
        datos = request.form

        existe_correo = Usuario.query.filter(
            Usuario.correo == datos.get('correo'),
            Usuario.id != id
        ).first()
        if existe_correo:
            flash('El correo ya está registrado por otro usuario.', 'danger')
            return redirect(url_for('usuarios.editar', id=id))

        existe_usuario = Usuario.query.filter(
            Usuario.nombre_usuario == datos.get('nombre_usuario'),
            Usuario.id != id
        ).first()
        if existe_usuario:
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('usuarios.editar', id=id))

        usuario.nombres = datos.get('nombres')
        usuario.apellidos = datos.get('apellidos')
        usuario.documento = datos.get('documento')
        usuario.correo = datos.get('correo')
        usuario.telefono = datos.get('telefono')
        usuario.nombre_usuario = datos.get('nombre_usuario')
        usuario.estado = datos.get('estado')
        usuario.rol_id = int(datos.get('rol_id'))

        nueva_contrasena = datos.get('contrasena')
        if nueva_contrasena:
            usuario.contrasena = bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')

        db.session.commit()
        registrar_auditoria('EDITAR_USUARIO',
                            f'Usuario editado: {usuario.nombre_usuario}',
                            current_user.id)
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template('usuarios/form.html', usuario=usuario, roles=roles)


@usuarios_bp.route('/desactivar/<int:id>', methods=['POST'])
@login_required
@rol_requerido('ADMINISTRADOR')
def desactivar(id):
    usuario = Usuario.query.get_or_404(id)

    if usuario.id == current_user.id:
        flash('No puedes desactivar tu propio usuario.', 'danger')
        return redirect(url_for('usuarios.index'))

    usuario.estado = 'INACTIVO'
    db.session.commit()
    registrar_auditoria('DESACTIVAR_USUARIO',
                        f'Usuario desactivado: {usuario.nombre_usuario}',
                        current_user.id)
    flash(f'Usuario {usuario.nombre_usuario} desactivado.', 'success')
    return redirect(url_for('usuarios.index'))


@usuarios_bp.route('/activar/<int:id>', methods=['POST'])
@login_required
@rol_requerido('ADMINISTRADOR')
def activar(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.estado = 'ACTIVO'
    db.session.commit()
    registrar_auditoria('ACTIVAR_USUARIO',
                        f'Usuario activado: {usuario.nombre_usuario}',
                        current_user.id)
    flash(f'Usuario {usuario.nombre_usuario} activado.', 'success')
    return redirect(url_for('usuarios.index'))