from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(30))

class Tatuador(db.Model):
    __tablename__ = 'tatuadores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    estilo = db.Column(db.String(200))

class Cita(db.Model):
    __tablename__ = 'citas'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    descripcion = db.Column(db.String(200))
    imagen_url = db.Column(db.String(200))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    tatuador_id = db.Column(db.Integer, db.ForeignKey('tatuadores.id'), nullable=False)

    cliente = db.relationship('Cliente', backref='citas')
    tatuador = db.relationship('Tatuador', backref='citas')

