from flask import Blueprint, request, jsonify
from models import db, Tatuador

tatuadores_bp = Blueprint("tatuadores", __name__)

@tatuadores_bp.get("")
def listar_tatuadores():
    tatuadores = Tatuador.query.all()
    return jsonify([{"id": t.id, "nombre": t.nombre, "estilo": t.estilo} for t in tatuadores])

@tatuadores_bp.post("")
def crear_tatuador():
    data = request.get_json()
    tatuador = Tatuador(nombre=data["nombre"], estilo=data.get("estilo"))
    db.session.add(tatuador)
    db.session.commit()
    return jsonify({"mensaje": "Tatuador creado", "id": tatuador.id}), 201

@tatuadores_bp.put("<int:id>")
def actualizar_tatuador(id):
    tatuador = Tatuador.query.get_or_404(id)
    data = request.get_json()
    tatuador.nombre = data.get("nombre", tatuador.nombre)
    tatuador.estilo = data.get("estilo", tatuador.estilo)
    db.session.commit()
    return jsonify({"mensaje": "Tatuador actualizado"})

@tatuadores_bp.delete("<int:id>")
def eliminar_tatuador(id):
    tatuador = Tatuador.query.get_or_404(id)
    db.session.delete(tatuador)
    db.session.commit()
    return jsonify({"mensaje": "Tatuador eliminado"})

