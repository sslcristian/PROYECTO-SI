from app.extensions import db
from datetime import date

class HistorialAsignacion(db.Model):
    __tablename__ = 'historial_asignacion'

    id = db.Column(db.Integer, primary_key=True)
    fecha_asignacion = db.Column(db.Date, default=date.today)
    fecha_fin = db.Column(db.Date)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tarea.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def __repr__(self):
        return f'<HistorialAsignacion {self.id}>'