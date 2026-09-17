from app.extensions import db

class Proyecto(db.Model):
    __tablename__ = 'proyecto'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    objetivo = db.Column(db.Text)
    fecha_inicio = db.Column(db.Date)
    fecha_fin_estimada = db.Column(db.Date)
    estado = db.Column(db.String(30))
    prioridad = db.Column(db.String(20))
    porcentaje_avance = db.Column(db.Numeric(5, 2), default=0)
    lider_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    tareas = db.relationship('Tarea', backref='proyecto', lazy=True,
                              cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Proyecto {self.nombre}>'