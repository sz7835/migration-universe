from flask import Blueprint, jsonify, request
from config import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # ✅ Needed to wrap raw SQL queries

catalogo_routes = Blueprint("catalogo_routes", __name__)

@catalogo_routes.route("/catalogo/ReadAllCatalogoServicio", methods=["GET"])
@catalogo_routes.route("/catalogo/ReadAllCatalogoServicio/<int:id_area>", methods=["GET"])
def read_all_catalogo_servicio(id_area=None):
    try:
        if id_area is not None:
            sql = text("SELECT * FROM catalogo_servicio WHERE id_area = :id_area")
            result = db.session.execute(sql, {"id_area": id_area})
        else:
            sql = text("SELECT * FROM catalogo_servicio")
            result = db.session.execute(sql)

        catalogos = [dict(row) for row in result]
        return jsonify(catalogos), 200

    except SQLAlchemyError as e:
        return jsonify({
            "mensaje": "Error al obtener catalogos.",
            "error": str(e)
        }), 500
