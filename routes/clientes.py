from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, Cliente

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "clientes ok"})

@clientes_bp.route("/", methods=["GET"])
def listar_clientes():
    clientes = Cliente.query.all()
    return jsonify([c.to_dict() for c in clientes])  # ✅ Usa to_dict()

@clientes_bp.route("/", methods=["POST"])
def crear_cliente():
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400

    data = request.get_json()
    missing = [k for k in ["nombre", "email"] if not data.get(k)]
    if missing:
        return jsonify({"error": f"Faltan campos requeridos: {', '.join(missing)}"}), 400

    try:
        cliente = Cliente(
            nombre=data["nombre"],
            email=data["email"],
            telefono=data.get("telefono")
        )
        db.session.add(cliente)
        db.session.commit()
        return jsonify({"mensaje": "Cliente creado", "cliente": cliente.to_dict()}), 201  # ✅ Devuelve el objeto completo
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email ya existe"}), 409

@clientes_bp.route("/<int:id>", methods=["PUT"])
def actualizar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400

    data = request.get_json()
    cliente.nombre = data.get("nombre", cliente.nombre)
    cliente.email = data.get("email", cliente.email)
    cliente.telefono = data.get("telefono", cliente.telefono)
    try:
        db.session.commit()
        return jsonify({"mensaje": "Cliente actualizado", "cliente": cliente.to_dict()})  # ✅ Devuelve actualizado
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email ya existe"}), 409

@clientes_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    return jsonify({"mensaje": "Cliente eliminado", "id": id})  # ✅ Devuelve el ID eliminado

