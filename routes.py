from flask import Blueprint, jsonify

catalogo_routes = Blueprint('catalogo_routes', __name__)

# Simulated data (fake DB)
FAKE_CATALOGOS = [
    {"id": 1, "nombre": "Soporte Técnico", "area": {"id": 2, "nombre": "TI"}},
    {"id": 2, "nombre": "Mantenimiento", "area": {"id": 2, "nombre": "TI"}}
]

FAKE_AREA = {
    "2": {"id": 2, "nombre": "TI"}
}

@catalogo_routes.route('/ticket/catalogo/ReadAllCatalogoServicio', defaults={'id_area': None}, methods=['GET'])
@catalogo_routes.route('/ticket/catalogo/ReadAllCatalogoServicio/<id_area>', methods=['GET'])
def get_catalogo_servicio(id_area):
    response = {}

    try:
        if id_area:
            area = FAKE_AREA.get(id_area)
            if not area:
                response["mensaje"] = "No se encontró el área."
                return jsonify(response), 404
            catalogos = [cat for cat in FAKE_CATALOGOS if cat["area"]["id"] == int(id_area)]
        else:
            catalogos = FAKE_CATALOGOS

        if not catalogos:
            response["mensaje"] = "No se encontraron catálogos para el área requerida."
            return jsonify(response), 404

        for cat in catalogos:
            if cat.get("area"):
                cat["area"]["puestos"] = None
                cat["area"]["gerencia"] = None

        response["mensaje"] = "Se obtuvo el listado de catálogos."
        response["catalogos"] = catalogos
        return jsonify(response), 200

    except Exception as e:
        response["mensaje"] = "Error al obtener catálogos."
        response["error"] = str(e)
        return jsonify(response), 500
