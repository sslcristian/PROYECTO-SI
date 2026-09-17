from app.extensions import db
from datetime import datetime

class Auditoria(db.Model):
    __tablename__ = 'auditoria'

    id = db.Column(db.Integer, primary_key=True)
    accion = db.Column(db.String(100))
    modulo = db.Column(db.String(50))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    hora = db.Column(db.Time, default=lambda: datetime.utcnow().time())
    direccion_ip = db.Column(db.String(45))
    descripcion = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    def __repr__(self):
        return f'<Auditoria {self.accion}>'