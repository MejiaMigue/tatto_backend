from flask import Blueprint, request, jsonify
from models import db, Tatuador

tatuadores_bp = Blueprint("tatuadores", __name__)

@tatuadores_bp.route("/", methods=["GET"])
def listar_tatuadores():
    tatuadores = Tatuador.query.all()
    return jsonify([t.to_dict() for t in tatuadores])  # ✅ Usa to_dict()

@tatuadores_bp.route("/", methods=["POST"])
def crear_tatuador():
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400

    data = request.get_json()
    if not data.get("nombre"):
        return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400

    tatuador = Tatuador(nombre=data["nombre"], estilo=data.get("estilo"))
    db.session.add(tatuador)
    db.session.commit()
    return jsonify({"mensaje": "Tatuador creado", "tatuador": tatuador.to_dict()}), 201  # ✅ Devuelve objeto completo

@tatuadores_bp.route("/<int:id>", methods=["PUT"])
def actualizar_tatuador(id):
    tatuador = Tatuador.query.get_or_404(id)
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400

    data = request.get_json()
    tatuador.nombre = data.get("nombre", tatuador.nombre)
    tatuador.estilo = data.get("estilo", tatuador.estilo)
    db.session.commit()
    return jsonify({"mensaje": "Tatuador actualizado", "tatuador": tatuador.to_dict()})  # ✅ Devuelve actualizado

@tatuadores_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_tatuador(id):
    tatuador = Tatuador.query.get_or_404(id)
    db.session.delete(tatuador)
    db.session.commit()
    return jsonify({"mensaje": "Tatuador eliminado", "id": id})  # ✅ Devuelve ID eliminado
