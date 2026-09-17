from app.extensions import db
from datetime import date

class Tarea(db.Model):
    __tablename__ = 'tarea'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.Date, default=date.today)
    fecha_inicio = db.Column(db.Date)
    fecha_vencimiento = db.Column(db.Date)
    estado = db.Column(db.String(30))
    prioridad = db.Column(db.String(20))
    porcentaje_avance = db.Column(db.Numeric(5, 2), default=0)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyecto.id'), nullable=False)
    responsable_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    avances = db.relationship('Avance', backref='tarea', lazy=True,
                               cascade='all, delete-orphan')
    historial = db.relationship('HistorialAsignacion', backref='tarea', lazy=True,
                                 cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Tarea {self.titulo}>'