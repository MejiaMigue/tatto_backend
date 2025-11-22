from flask import Blueprint, request, jsonify, Response
from models import db, Cita
from datetime import datetime
import xml.etree.ElementTree as ET

citas_bp = Blueprint("citas", __name__)

@citas_bp.get("")
def listar_citas():
    citas = Cita.query.all()
    return jsonify([
        {
            "id": c.id,
            "cliente_id": c.cliente_id,
            "cliente": {"id": c.cliente.id, "nombre": c.cliente.nombre} if c.cliente else None,
            "tatuador_id": c.tatuador_id,
            "tatuador": {"id": c.tatuador.id, "nombre": c.tatuador.nombre, "estilo": c.tatuador.estilo} if c.tatuador else None,
            "fecha": c.fecha.isoformat(),
            "hora_inicio": c.hora_inicio.strftime("%H:%M"),
            "hora_fin": c.hora_fin.strftime("%H:%M"),
            "descripcion": c.descripcion,
            "imagen_url": c.imagen_url
        } for c in citas
    ])

@citas_bp.post("")
def crear_cita():
    data = request.get_json()
    fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
    hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
    hora_fin = datetime.strptime(data["hora_fin"], "%H:%M").time()

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
    return jsonify({"mensaje": "Cita creada", "id": cita.id}), 201

@citas_bp.put("<int:id>")
def actualizar_cita(id):
    cita = Cita.query.get_or_404(id)
    data = request.get_json()

    if "fecha" in data:
        cita.fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
    if "hora_inicio" in data:
        cita.hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
    if "hora_fin" in data:
        cita.hora_fin = datetime.strptime(data["hora_fin"], "%H:%M").time()

    cita.descripcion = data.get("descripcion", cita.descripcion)
    cita.imagen_url = data.get("imagen_url", cita.imagen_url)
    db.session.commit()
    return jsonify({"mensaje": "Cita actualizada"})

@citas_bp.delete("<int:id>")
def eliminar_cita(id):
    cita = Cita.query.get_or_404(id)
    db.session.delete(cita)
    db.session.commit()
    return jsonify({"mensaje": "Cita eliminada"})


# 🚀 Nuevo endpoint: Exportar citas en XML agrupadas por tatuador con totales y porcentajes
@citas_bp.get("xml")
def exportar_citas_xml():
    tatuadores_dict = {}

    citas = Cita.query.all()
    total_general = len(citas)  # 🔹 total de citas en el sistema

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

    # 🔹 Nodo global con total general
    resumen_el = ET.SubElement(root, "resumen")
    ET.SubElement(resumen_el, "total_general").text = str(total_general)

    # 🔹 Nodos por tatuador
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
