from flask import request
from flask import Blueprint, jsonify
from config import db
from sqlalchemy import text

# Create a Blueprint for all catalog-related routes
catalogo_bp = Blueprint('catalogo_bp', __name__)

# 📄 Route 21: Read all catalog services by area
# - GET /ticket/catalogo/ReadAllCatalogoServicio/<id_area>
# - Returns all services (nombre_servicio) for a specific area from the `catalogo_servicio` table.
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


# 📄 Route 23 (TESTED): Listar Tipo Usuario
# - Endpoint: /catalogo/ReadAllTipoUsuario
# - Method: GET
# - Input: None
# - Function: Returns all user types from `sec_tipo_usuario` including fields like descripcion, ingreso/mod info.
@catalogo_bp.route('/catalogo/ReadAllTipoUsuario', methods=['GET'])
def read_all_tipo_usuario():
    try:
        connection = db.engine.raw_connection()
        cursor = connection.cursor()

        query = """
            SELECT 
                ID_TIPO_USUARIO, DSC_TIPO_USUARIO, USR_INGRESO, 
                FEC_INGRESO, ESTADO, USR_ULT_MOD, FEC_ULT_MOD
            FROM sec_tipo_usuario
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "descripcion": row[1],
                "usuario_ingreso": row[2],
                "fecha_ingreso": row[3].isoformat() if row[3] else None,
                "estado": row[4],
                "usuario_modificacion": row[5],
                "fecha_modificacion": row[6].isoformat() if row[6] else None
            })

        cursor.close()
        connection.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📄 Route 25 (TESTED): Create new ticket activity record
# - Endpoint: /catalogo/SaveTicketCatalogoServicio
# - Method: POST
# - Function: Inserts a new record into the `out_registro_actividad` table.
# - Input: JSON body with required fields:
#     - out_tipo_actividad_id
#     - per_persona_id
#     - fecha
#     - detalle
#     - create_user
#     - create_date
# - Notes: The field `registro` is set automatically using NOW().
# - Response: Returns success message if insertion succeeds, otherwise returns error.
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


# 📄 Route 26 (TESTED): Actualizar Registro de Actividad
# - Endpoint: /catalogo/UpdateTicketCatalogoServicio
# - Method: PUT
# - Input (JSON): id, fecha, detalle, update_user
# - Function: Updates an existing activity record in 'out_registro_actividad' with new fecha, detalle,
#             update_user, and auto timestamp update_date.
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


# 📄 Route 27: Read all types of registro (record types)
# - Endpoint: /catalogo/ReadAllTipoRegistro
# - Method: GET
# - Function: Fetches all records from the `sis_tipo_registro` table.
# - Output: Returns a list of objects with:
#     - id_tipo_registro
#     - descripcion
# - Response: JSON list of types or error if query fails.
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


# 📄 Route 30 (TESTED): Read all areas (for tickets)
# - GET /ticket/generarTicket/read
# - Returns a full list of areas from `per_jur_area`, including metadata like creation/update info.
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
