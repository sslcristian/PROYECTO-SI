from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models.proyecto import Proyecto
from app.models.usuario import Usuario
from app.models.tarea import Tarea
from app.models.auditoria import Auditoria
from app.utils.decorators import rol_requerido

proyectos_bp = Blueprint('proyectos', __name__, url_prefix='/proyectos')


def registrar_auditoria(accion, descripcion):
    try:
        a = Auditoria(
            accion=accion,
            modulo='Proyectos',
            descripcion=descripcion,
            direccion_ip=request.remote_addr,
            usuario_id=current_user.id
        )
        db.session.add(a)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error auditoria: {e}")


@proyectos_bp.route('/')
@login_required
def index():
    if current_user.rol.nombre in ['ADMINISTRADOR', 'GERENTE']:
        proyectos = Proyecto.query.order_by(Proyecto.id.desc()).all()
    elif current_user.rol.nombre == 'LIDER':
        proyectos = Proyecto.query.filter(
            (Proyecto.lider_id == current_user.id) |
            (Proyecto.tareas.any(Tarea.responsable_id == current_user.id))
        ).distinct().all()
    else:
        proyectos = Proyecto.query.filter(
            Proyecto.tareas.any(Tarea.responsable_id == current_user.id)
        ).distinct().all()

    return render_template('proyectos/index.html', proyectos=proyectos)


@proyectos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_requerido('ADMINISTRADOR', 'GERENTE')
def nuevo():
    lideres = Usuario.query.filter(
        Usuario.rol.has(nombre='LIDER'),
        Usuario.estado == 'ACTIVO'
    ).all()

    if request.method == 'POST':
        datos = request.form

        if Proyecto.query.filter_by(nombre=datos.get('nombre')).first():
            flash('Ya existe un proyecto con ese nombre.', 'danger')
            return redirect(url_for('proyectos.nuevo'))

        proyecto = Proyecto(
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion'),
            objetivo=datos.get('objetivo'),
            fecha_inicio=datetime.strptime(datos.get('fecha_inicio'), '%Y-%m-%d').date() if datos.get('fecha_inicio') else None,
            fecha_fin_estimada=datetime.strptime(datos.get('fecha_fin_estimada'), '%Y-%m-%d').date() if datos.get('fecha_fin_estimada') else None,
            estado=datos.get('estado', 'PLANEADO'),
            prioridad=datos.get('prioridad', 'MEDIA'),
            porcentaje_avance=0,
            lider_id=int(datos.get('lider_id')) if datos.get('lider_id') else None
        )
        db.session.add(proyecto)
        db.session.commit()

        registrar_auditoria('CREAR_PROYECTO', f'Proyecto creado: {proyecto.nombre}')
        flash('Proyecto creado exitosamente.', 'success')
        return redirect(url_for('proyectos.index'))

    return render_template('proyectos/form.html', proyecto=None, lideres=lideres)


@proyectos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('ADMINISTRADOR', 'GERENTE')
def editar(id):
    proyecto = Proyecto.query.get_or_404(id)
    lideres = Usuario.query.filter(
        Usuario.rol.has(nombre='LIDER'),
        Usuario.estado == 'ACTIVO'
    ).all()

    if request.method == 'POST':
        datos = request.form

        existe = Proyecto.query.filter(
            Proyecto.nombre == datos.get('nombre'),
            Proyecto.id != id
        ).first()
        if existe:
            flash('Ya existe otro proyecto con ese nombre.', 'danger')
            return redirect(url_for('proyectos.editar', id=id))

        proyecto.nombre = datos.get('nombre')
        proyecto.descripcion = datos.get('descripcion')
        proyecto.objetivo = datos.get('objetivo')
        proyecto.fecha_inicio = datetime.strptime(datos.get('fecha_inicio'), '%Y-%m-%d').date() if datos.get('fecha_inicio') else None
        proyecto.fecha_fin_estimada = datetime.strptime(datos.get('fecha_fin_estimada'), '%Y-%m-%d').date() if datos.get('fecha_fin_estimada') else None
        proyecto.estado = datos.get('estado')
        proyecto.prioridad = datos.get('prioridad')
        proyecto.lider_id = int(datos.get('lider_id')) if datos.get('lider_id') else None

        db.session.commit()
        registrar_auditoria('EDITAR_PROYECTO', f'Proyecto editado: {proyecto.nombre}')
        flash('Proyecto actualizado exitosamente.', 'success')
        return redirect(url_for('proyectos.index'))

    return render_template('proyectos/form.html', proyecto=proyecto, lideres=lideres)


@proyectos_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    proyecto = Proyecto.query.get_or_404(id)
    return render_template('proyectos/ver.html', proyecto=proyecto)


@proyectos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@rol_requerido('ADMINISTRADOR', 'GERENTE')
def eliminar(id):
    proyecto = Proyecto.query.get_or_404(id)

    if proyecto.tareas:
        flash('No se puede eliminar un proyecto que tiene tareas asociadas.', 'danger')
        return redirect(url_for('proyectos.index'))

    nombre = proyecto.nombre
    db.session.delete(proyecto)
    db.session.commit()
    registrar_auditoria('ELIMINAR_PROYECTO', f'Proyecto eliminado: {nombre}')
    flash('Proyecto eliminado exitosamente.', 'success')
    return redirect(url_for('proyectos.index'))