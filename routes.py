from flask import request
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


# ◆ ROUTE 2 (TESTED): Get all areas from per_jur_area with more details
# This route returns all area IDs, descriptions, and metadata (used for dropdowns, audits, etc.)

@catalogo_bp.route('/ticket/generarTicket/read', methods=['GET'])
def read_all_areas():
    try:
        sql = text("""
            SELECT id_area, id_per_jur, descripcion, estado, 
                   create_user, create_date, update_user, update_date
            FROM per_jur_area
        """)
        result = db.session.execute(sql).fetchall()

        areas = [
            {
                "id_area": row[0],
                "id_per_jur": row[1],
                "descripcion": row[2],
                "estado": row[3],
                "create_user": row[4],
                "create_date": row[5].isoformat() if row[5] else None,
                "update_user": row[6],
                "update_date": row[7].isoformat() if row[7] else None
            }
            for row in result
        ]

        return jsonify(areas)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "❌ Error al obtener áreas"
        }), 500



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

# ✅ ROUTE 4 (TESTED): Save a Ticket Activity Record
# This route inserts a new ticket log into the 'out_registro_actividad' table.
# It expects full data from the frontend, performs validation, and inserts with automatic timestamping.

@catalogo_bp.route('/catalogo/SaveTicketCatalogoServicio', methods=['POST'])
def save_ticket_catalogo_servicio():
    try:
        data = request.get_json()

        # List of all required fields based on table structure
        required_fields = [
            'out_tipo_actividad_id',
            'per_persona_id',
            'fecha',
            'detalle',
            'create_user',
            'create_date'
        ]

        # Loop through and verify that no required field is missing or empty
        for field in required_fields:
            if field not in data or data[field] in [None, ""]:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Prepare SQL insert using NOW() for automatic current timestamp on 'registro'
        sql = text("""
            INSERT INTO out_registro_actividad 
                (out_tipo_actividad_id, per_persona_id, fecha, detalle, registro, create_user, create_date)
            VALUES 
                (:out_tipo_actividad_id, :per_persona_id, :fecha, :detalle, NOW(), :create_user, :create_date)
        """)

        # Execute SQL with provided data
        db.session.execute(sql, {
            "out_tipo_actividad_id": data['out_tipo_actividad_id'],
            "per_persona_id": data['per_persona_id'],
            "fecha": data['fecha'],
            "detalle": data['detalle'],
            "create_user": data['create_user'],
            "create_date": data['create_date']
        })

        # Finalize transaction
        db.session.commit()
        return jsonify({"message": "✅ Registro de actividad guardado exitosamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": str(e),
            "message": "❌ Error al guardar el registro de actividad"
        }), 500


# 🔧 ROUTE 5: Update a ticket activity in out_registro_actividad
# This route updates fields like fecha, detalle, update_user, and update_date
@catalogo_bp.route('/catalogo/UpdateTicketCatalogoServicio', methods=['PUT'])
def update_ticket_catalogo_servicio():
    try:
        data = request.get_json()

        # 🔒 Validate required fields
        required_fields = ['id', 'fecha', 'detalle', 'update_user']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        sql = text("""
            UPDATE out_registro_actividad
            SET
                fecha = :fecha,
                detalle = :detalle,
                update_user = :update_user,
                update_date = NOW()
            WHERE id = :id
        """)

        db.session.execute(sql, {
            "id": data['id'],
            "fecha": data['fecha'],
            "detalle": data['detalle'],
            "update_user": data['update_user']
        })
        db.session.commit()

        return jsonify({"message": "✔ Ticket actualizado correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "message": "❌ Error al actualizar ticket"}), 500
