from app import create_app
from app.extensions import db, bcrypt
from app.models.rol import Rol
from app.models.usuario import Usuario

app = create_app()

def inicializar_datos():
    roles_data = [
        ('ADMINISTRADOR', 'Administra usuarios, roles y configuración'),
        ('GERENTE', 'Gestiona proyectos y consulta indicadores'),
        ('LIDER', 'Coordina tareas y responsables'),
        ('COLABORADOR', 'Ejecuta tareas y registra avances'),
    ]
    for nombre, desc in roles_data:
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre, descripcion=desc))
    db.session.commit()

    if not Usuario.query.filter_by(nombre_usuario='admin').first():
        admin_rol = Rol.query.filter_by(nombre='ADMINISTRADOR').first()
        admin = Usuario(
            nombres='Admin',
            apellidos='Sistema',
            documento='123456789',
            correo='admin@sistema.com',
            telefono='3001234567',
            nombre_usuario='admin',
            contrasena=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            estado='ACTIVO',
            rol_id=admin_rol.id
        )
        db.session.add(admin)
        db.session.commit()
        print(">>> Usuario admin creado: admin / admin123")

if __name__ == '__main__':
    with app.app_context():
        inicializar_datos()
        print(">>> Base de datos conectada a Neon")
        print(">>> Servidor en http://localhost:5000")
    app.run(debug=True, port=5000)