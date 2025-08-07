from flask import request
from flask import Blueprint, jsonify
from config import db
from sqlalchemy import text
from datetime import datetime

# Create a Blueprint for all catalog-related routes
catalogo_bp = Blueprint('catalogo_bp', __name__)

# 📄 Route 1 (TESTED COMPLETELY WORKING FINALIZADO): Get activity records by person, activity type, and date
# - Endpoint: /actividades/tipoActividad
# - Method: GET
# - Input (query string): idPersona, idActividad, registro (yyyy-MM-dd)
# - Example: /actividades/tipoActividad?idPersona=8&idActividad=9&registro=2025-07-10
# - Description: Returns activity records from out_registro_actividad table filtered by person, activity type, and date

@catalogo_bp.route('/actividades/tipoActividad', methods=['GET'])
def get_actividad_tipo():
    try:
        id_actividad = request.args.get('idActividad')
        id_persona = request.args.get('idPersona')
        registro = request.args.get('registro')  # format: yyyy-MM-dd

        if not id_actividad or not id_persona or not registro:
            return jsonify({'error': 'Missing one or more required parameters'}), 400

        sql = text("""
            SELECT *
            FROM out_registro_actividad
            WHERE per_persona_id = :id_persona
              AND out_tipo_actividad_id = :id_actividad
              AND DATE(registro) = :registro_date
        """)

        result = db.session.execute(sql, {
            'id_persona': id_persona,
            'id_actividad': id_actividad,
            'registro_date': registro
        }).fetchall()

        data = [dict(row._mapping) for row in result]
        return jsonify(data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 📄 Route 2 (TESTED COMPLETELY WORKING FINALIZADO): Filter activity records by user, activity type, and date
# - Endpoint: /actividades/filter
# - Method: GET
# - Parameters (query string):
#     • idPersona (e.g. 8)   → maps to column `per_persona_id`
#     • idActividad (e.g. 9) → maps to column `out_tipo_actividad_id`
#     • registro (yyyy-MM-dd) → maps to column `registro` (timestamp)
# - Description: Returns a list of activity records matching the filters
#   from the table `out_registro_actividad`.

@catalogo_bp.route('/actividades/filter', methods=['GET'])
def filter_actividades():
    try:
        id_persona = request.args.get('idPersona')
        id_actividad = request.args.get('idActividad')
        registro = request.args.get('registro')

        if not id_persona or not id_actividad or not registro:
            return jsonify({'error': 'Missing one or more required parameters'}), 400

        # No need to convert registro to date – use string as-is
        sql = text("""
            SELECT *
            FROM out_registro_actividad
            WHERE per_persona_id = :id_persona
              AND out_tipo_actividad_id = :id_actividad
              AND DATE(registro) = :registro_date
        """)

        result = db.session.execute(sql, {
            'id_persona': id_persona,
            'id_actividad': id_actividad,
            'registro_date': registro
        }).fetchall()

        data = [dict(row._mapping) for row in result]
        return jsonify(data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 📄 Route 3 (TESTED COMPLETELY WORKING FINALIZADO): Create a new activity record
# - Endpoint: /actividades/create
# - Method: POST
# - Parameters (query string):
#     • personalId (e.g. 8)         → maps to column `per_persona_id`
#     • idTipoAct (e.g. 1)          → maps to column `out_tipo_actividad_id`
#     • hora (HH:MM, e.g. 14:00)    → combined with fecha to form timestamp
#     • fecha (YYYY-MM-DD, e.g. 2025-07-10) → saved to column `fecha`
#     • createUser (e.g. bsayan)    → maps to column `create_user`
#     • detalle (optional)          → maps to column `detalle`
# - Description: Creates a new activity record for a given person and activity type.
# - Expected Response: {"mensaje": "Actividad creada correctamente."}

@catalogo_bp.route('/actividades/create', methods=['POST'])
def create_actividad():
    try:
        # Required query params
        persona_id = request.args.get('personalId')
        tipo_actividad_id = request.args.get('idTipoAct')
        hora = request.args.get('hora')  # format: HH:MM
        fecha = request.args.get('fecha')  # format: YYYY-MM-DD
        create_user = request.args.get('createUser')

        # Optional param
        detalle = request.args.get('detalle') or "Detalle no proporcionado"

        # Validate required params
        if not all([persona_id, tipo_actividad_id, hora, fecha, create_user]):
            return jsonify({'error': 'Faltan parámetros obligatorios'}), 400

        # Combine fecha and hora into timestamp
        registro_str = f"{fecha} {hora}:00"
        registro = datetime.strptime(registro_str, "%Y-%m-%d %H:%M:%S")

        # ✅ INSERT including fecha column
        sql = text("""
            INSERT INTO out_registro_actividad (
                per_persona_id,
                out_tipo_actividad_id,
                fecha,
                registro,
                detalle,
                create_user,
                create_date
            )
            VALUES (
                :persona_id,
                :tipo_actividad_id,
                :fecha,
                :registro,
                :detalle,
                :create_user,
                NOW()
            )
        """)

        db.session.execute(sql, {
            'persona_id': persona_id,
            'tipo_actividad_id': tipo_actividad_id,
            'fecha': fecha,  # ✅ Include this
            'registro': registro,
            'detalle': detalle,
            'create_user': create_user
        })

        db.session.commit()

        return jsonify({'mensaje': 'Actividad creada correctamente.'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 📄 Route 4 (TESTED COMPLETELY WORKING FINALIZADO): Filter hour records by person, status, and date range
# - Endpoint: /registro-horas/index
# - Method: GET
# - Query Parameters:
#     • idPersona     → maps to column `id_persona`
#     • estado        → maps to column `estado`
#     • fechaIniciof  → maps to column `dia` (start of range)
#     • fechaFin      → maps to column `dia` (end of range)
# - Description: Returns records from `out_registro_horas` table based on person, state, and date range

@catalogo_bp.route('/registro-horas/index', methods=['GET'])
def get_registro_horas_filtrado():
    try:
        id_persona = request.args.get('idPersona')
        estado = request.args.get('estado')
        fecha_inicio = request.args.get('fechaIniciof')
        fecha_fin = request.args.get('fechaFin')

        if not id_persona or not estado or not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Faltan parámetros requeridos'}), 400

        sql = text("""
            SELECT *
            FROM out_registro_horas
            WHERE id_persona = :id_persona
              AND estado = :estado
              AND dia BETWEEN :fecha_inicio AND :fecha_fin
        """)

        result = db.session.execute(sql, {
            'id_persona': id_persona,
            'estado': estado,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }).fetchall()

        data = [dict(row._mapping) for row in result]
        return jsonify(data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 📄 Route 5 (TESTED COMPLETELY WORKING FINALIZADO): Create hour records for a person and project
# - Endpoint: /registro-horas/create
# - Method: POST
# - Body (JSON):
# {
#     "idProyecto": 280,
#     "idPersona": 8,
#     "detalle": [
#         {"actividad": "test", "horas": "1"},
#         {"actividad": "test 2", "horas": "2"}
#     ],
#     "dia": "2025-07-10",
#     "createUser": "bsayan"
# }
# - Description: Creates multiple hour records in the table `out_registro_horas`
#   for the given person and project on the specified date.

@catalogo_bp.route('/registro-horas/create', methods=['POST'])
def create_registro_horas():
    try:
        data = request.get_json()

        id_proyecto = data.get('idProyecto')
        id_persona = data.get('idPersona')
        detalle = data.get('detalle')  # This should be a list of dicts
        dia = data.get('dia')
        create_user = data.get('createUser')

        # Basic validation
        if not id_proyecto or not id_persona or not detalle or not dia or not create_user:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        for item in detalle:
            actividad = item.get('actividad')
            horas = item.get('horas')

            if not actividad or not horas:
                return jsonify({'error': 'Cada detalle debe incluir actividad y horas'}), 400

            sql = text("""
                INSERT INTO out_registro_horas (
                    id_proyecto, id_persona, actividad, horas, dia, estado, create_user, create_date
                ) VALUES (
                    :id_proyecto, :id_persona, :actividad, :horas, :dia, :estado, :create_user, NOW()
                )
            """)

            db.session.execute(sql, {
                'id_proyecto': id_proyecto,
                'id_persona': id_persona,
                'actividad': actividad,
                'horas': horas,
                'dia': dia,
                'estado': 1,
                'create_user': create_user
            })

        db.session.commit()
        return jsonify({'mensaje': 'Registros creados correctamente.'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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
