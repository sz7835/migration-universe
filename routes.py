from flask import Blueprint, jsonify
from config import db
from sqlalchemy import text

# Create a Blueprint for all catalog-related routes
catalogo_bp = Blueprint('catalogo_bp', __name__)

# 🔹 ROUTE 1: Get all services by area
# This route returns all catalog services that belong to a given area (based on id_area)
@catalogo_bp.route('/ticket/catalogo/ReadAllCatalogoServicio/<int:id_area>', methods=['GET'])
def read_all_catalogo_servicio(id_area):
    try:
        sql = text("""
            SELECT id_catalogo_servicio, nombre_servicio 
            FROM catalogo_servicio 
            WHERE id_area = :id_area
        """)
        result = db.session.execute(sql, {'id_area': id_area}).fetchall()

        servicios = [
            {"id_catalogo_servicio": row[0], "nombre_servicio": row[1]}
            for row in result
        ]
        return jsonify(servicios)

    except Exception as e:
        return jsonify({"error": str(e), "message": "❌ Error al obtener servicios"}), 500


# 🔹 ROUTE 2 (TESTED): Get all areas from per_jur_area
# This route returns all area IDs and descriptions (used to populate dropdowns, filters, etc.)
@catalogo_bp.route('/ticket/generarTicket/read', methods=['GET'])
def read_all_areas():
    try:
        sql = text("""
            SELECT id_area, descripcion
            FROM per_jur_area
        """)
        result = db.session.execute(sql).fetchall()

        areas = [
            {"id_area": row[0], "descripcion": row[1]}
            for row in result
        ]
        return jsonify(areas)

    except Exception as e:
        return jsonify({"error": str(e), "message": "❌ Error al obtener áreas"}), 500


# 🔹 ROUTE 3: Get all "Tipo de Registro" values from sis_tipo_registro
# This route returns all "tipo de registro" options (used for dropdowns like Entrada, Salida, etc.)
@catalogo_bp.route('/catalogo/ReadAllTipoRegistro', methods=['GET'])
def read_all_tipo_registro():
    try:
        sql = text("""
            SELECT id_tipo_registro, descripcion
            FROM sis_tipo_registro
        """)
        result = db.session.execute(sql).fetchall()

        tipos = [
            {"id_tipo_registro": row[0], "descripcion": row[1]}
            for row in result
        ]

        return jsonify(tipos)

    except Exception as e:
        return jsonify({"error": str(e), "message": "❌ Error al obtener tipos de registro"}), 500

