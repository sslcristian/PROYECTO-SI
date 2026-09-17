from app.extensions import db
from datetime import datetime

class Avance(db.Model):
    __tablename__ = 'avance'

    id = db.Column(db.Integer, primary_key=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    comentario = db.Column(db.Text)
    porcentaje_progreso = db.Column(db.Numeric(5, 2))
    tarea_id = db.Column(db.Integer, db.ForeignKey('tarea.id'), nullable=False)

    evidencias = db.relationship('Evidencia', backref='avance', lazy=True,
                                  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Avance {self.id}>'