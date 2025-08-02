from flask import Blueprint, jsonify
from config import db

catalogo_bp = Blueprint('catalogo_bp', __name__, url_prefix='/ticket/catalogo')

@catalogo_bp.route('/ReadAllCatalogoServicio/<int:id_area>', methods=['GET'])
def read_all_catalogo_servicio(id_area):
    try:
        query = f"""
            SELECT id_catalogo_servicio, nombre
            FROM catalogo_servicio
            WHERE id_area = {id_area}
        """
        result = db.session.execute(query)
        data = [
            {"id_catalogo_servicio": row[0], "nombre": row[1]}
            for row in result.fetchall()
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "message": "❌ Error al obtener servicios"}), 500
