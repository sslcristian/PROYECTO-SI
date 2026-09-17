from app.extensions import db
from datetime import date

class Evidencia(db.Model):
    __tablename__ = 'evidencia'

    id = db.Column(db.Integer, primary_key=True)
    archivo = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.Date, default=date.today)
    avance_id = db.Column(db.Integer, db.ForeignKey('avance.id'), nullable=False)

    def __repr__(self):
        return f'<Evidencia {self.archivo}>'