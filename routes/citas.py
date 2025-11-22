from flask import Blueprint, request, jsonify, Response
from models import db, Cita
from datetime import datetime
import xml.etree.ElementTree as ET

citas_bp = Blueprint("citas", __name__)

@citas_bp.route("/", methods=["GET"])
def listar_citas():
    citas = Cita.query.all()
    return jsonify([c.to_dict() for c in citas])  # ✅ Usa to_dict()

@citas_bp.route("/", methods=["POST"])
def crear_cita():
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400

    data = request.get_json()
    required = ["fecha", "hora_inicio", "hora_fin", "cliente_id", "tatuador_id"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": f"Faltan campos requeridos: {', '.join(missing)}"}), 400

    try:
        fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
        hora_fin = datetime.strptime(data["hora_fin"], "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Formato de fecha u hora inválido"}), 400

    # Validación de solapamiento
    solapada = Cita.query.filter_by(tatuador_id=data["tatuador_id"], fecha=fecha).filter(
        Cita.hora_inicio < hora_fin,
        Cita.hora_fin > hora_inicio
    ).first()

    if solapada:
        return jsonify({"error": "El tatuador ya tiene una cita en ese horario"}), 409

    cita = Cita(
        cliente_id=data["cliente_id"],
        tatuador_id=data["tatuador_id"],
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        descripcion=data.get("descripcion"),
        imagen_url=data.get("imagen_url")
    )
    db.session.add(cita)
    db.session.commit()
    return jsonify({"mensaje": "Cita creada", "cita": cita.to_dict()}), 201  # ✅ Devuelve objeto completo

@citas_bp.route("/<int:id>", methods=["PUT"])
def actualizar_cita(id):
    cita = Cita.query.get_or_404(id)
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400

    data = request.get_json()

    try:
        if "fecha" in data:
            cita.fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        if "hora_inicio" in data:
            cita.hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
        if "hora_fin" in data:
            cita.hora_fin = datetime.strptime(data["hora_fin"], "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Formato de fecha u hora inválido"}), 400

    cita.descripcion = data.get("descripcion", cita.descripcion)
    cita.imagen_url = data.get("imagen_url", cita.imagen_url)
    db.session.commit()
    return jsonify({"mensaje": "Cita actualizada", "cita": cita.to_dict()})  # ✅ Devuelve actualizado

@citas_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_cita(id):
    cita = Cita.query.get_or_404(id)
    db.session.delete(cita)
    db.session.commit()
    return jsonify({"mensaje": "Cita eliminada", "id": id})  # ✅ Devuelve ID eliminado

@citas_bp.route("/xml", methods=["GET"])
def exportar_citas_xml():
    tatuadores_dict = {}
    citas = Cita.query.all()
    total_general = len(citas)

    for c in citas:
        t = c.tatuador
        if t.id not in tatuadores_dict:
            tatuadores_dict[t.id] = {
                "nombre": t.nombre,
                "estilo": t.estilo,
                "citas": []
            }
        tatuadores_dict[t.id]["citas"].append(c)

    root = ET.Element("reporte")
    resumen_el = ET.SubElement(root, "resumen")
    ET.SubElement(resumen_el, "total_general").text = str(total_general)

    for tid, data in tatuadores_dict.items():
        total_tatuador = len(data["citas"])
        porcentaje = (total_tatuador / total_general * 100) if total_general > 0 else 0

        tatuador_el = ET.SubElement(
            root,
            "tatuador",
            id=str(tid),
            nombre=data["nombre"],
            estilo=data["estilo"] or ""
        )

        ET.SubElement(tatuador_el, "total_citas").text = str(total_tatuador)
        ET.SubElement(tatuador_el, "porcentaje").text = f"{porcentaje:.2f}%"

        for c in data["citas"]:
            cita_el = ET.SubElement(tatuador_el, "cita", id=str(c.id))
            ET.SubElement(cita_el, "cliente_id").text = str(c.cliente_id)
            ET.SubElement(cita_el, "fecha").text = c.fecha.isoformat()
            ET.SubElement(cita_el, "hora_inicio").text = c.hora_inicio.strftime("%H:%M")
            ET.SubElement(cita_el, "hora_fin").text = c.hora_fin.strftime("%H:%M")
            ET.SubElement(cita_el, "descripcion").text = c.descripcion or ""

    xml_str = ET.tostring(root, encoding="utf-8", method="xml")
    return Response(xml_str, mimetype="application/xml")
