from app.extensions import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), unique=True, nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(20), default='ACTIVO')
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False)

    proyectos_liderados = db.relationship('Proyecto', backref='lider', lazy=True,
                                           foreign_keys='Proyecto.lider_id')
    tareas_asignadas = db.relationship('Tarea', backref='responsable', lazy=True,
                                        foreign_keys='Tarea.responsable_id')
    auditorias = db.relationship('Auditoria', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'