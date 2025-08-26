from flask import request

from flask import Blueprint, jsonify
from config import db
from sqlalchemy import text
from datetime import datetime

# Create a Blueprint for all catalog-related routes
catalogo_bp = Blueprint('catalogo_bp', __name__)

# 📄 Ruta 1 (PROBADA Y FUNCIONAL): Obtiene los registros de actividad filtrados por persona, tipo de actividad y fecha.  
# Devuelve los datos desde la tabla 'out_registro_actividad' usando los parámetros idPersona, idActividad y registro.
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

# 📄 Ruta 2 (PROBADA Y FUNCIONAL): Filtra los registros de actividad por persona, tipo de actividad y fecha.  
# Devuelve una lista de resultados desde la tabla 'out_registro_actividad' que coincidan con los parámetros recibidos.
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

# 📄 Ruta 3 (PROBADA Y FUNCIONAL): Crea un nuevo registro de actividad para una persona y un tipo de actividad específico.  
# Recibe los datos por parámetros y guarda la información en la tabla 'out_registro_actividad'.
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

# 📄 Ruta 4 (PROBADA Y FUNCIONAL): Filtra los registros de horas por persona, estado y rango de fechas.  
# Devuelve los datos desde la tabla 'out_registro_horas' que coincidan con los parámetros especificados.
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

# 📄 Ruta 5 (PROBADA Y FUNCIONAL): Crea múltiples registros de horas para una persona y un proyecto en una fecha determinada.  
# Los datos se guardan en la tabla 'out_registro_horas' a partir del cuerpo JSON recibido.
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

# 📄 Ruta 6 (PROBADA Y FUNCIONAL): Lista Proyectos (mostrarProyecto)
# Retorna los proyectos de la tabla 'out_registro_proyecto' asociados al idPersona indicado.
@catalogo_bp.route('/registro-horas/mostrarProyecto', methods=['POST'])
def mostrar_proyecto():
    try:
        id_persona = request.args.get('idPersona')

        if not id_persona:
            return jsonify({"error": "Missing 'idPersona' parameter"}), 400

        sql = text("""
            SELECT
                id,
                id_persona,
                codigo,
                descripcion,
                estado,
                create_user,
                DATE_FORMAT(create_date, '%Y-%m-%d %H:%i:%s') AS create_date,
                update_user,
                DATE_FORMAT(update_date, '%Y-%m-%d %H:%i:%s') AS update_date
            FROM out_registro_proyecto
            WHERE id_persona = :id_persona
            ORDER BY id DESC
        """)

        rows = db.session.execute(sql, {"id_persona": id_persona}).fetchall()
        data = [dict(r._mapping) for r in rows]

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📄 Ruta 7 (PROBADA Y FUNCIONAL): Eliminar Registro de Horas (delete)
# Elimina un registro de horas desde la tabla 'out_registro_horas' usando el id indicado.
@catalogo_bp.route('/registro-horas/delete', methods=['DELETE'])
def delete_registro_horas():
    try:
        # Obtener ID desde query string o JSON body
        id_param = request.args.get('id')
        if not id_param:
            body_data = request.get_json(silent=True)
            if body_data and 'id' in body_data:
                id_param = body_data['id']

        if not id_param:
            return jsonify({"error": "Missing 'id' parameter"}), 400

        sql = text("""
            DELETE FROM out_registro_horas
            WHERE id = :id
        """)

        result = db.session.execute(sql, {"id": id_param})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"message": f"No record found with id {id_param}"}), 404

        return jsonify({"message": f"Record with id {id_param} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📄 Ruta 8 (PROBADA Y FUNCIONAL): Actualizar Registro de Horas (update)
# Actualiza los campos 'actividad', 'horas' y 'update_user' de un registro en 'out_registro_horas' usando el id indicado.
@catalogo_bp.route('/registro-horas/update', methods=['POST'])
def update_registro_horas():
    try:
        id_param = request.args.get('id')
        actividad = request.args.get('actividad')
        horas = request.args.get('horas')
        update_user = request.args.get('update_user')

        if not id_param or not actividad or not horas or not update_user:
            return jsonify({"error": "Missing required parameters"}), 400

        sql = text("""
            UPDATE out_registro_horas
            SET actividad = :actividad,
                horas = :horas,
                update_user = :update_user,
                update_date = NOW()
            WHERE id = :id
        """)

        result = db.session.execute(sql, {
            "id": id_param,
            "actividad": actividad,
            "horas": horas,
            "update_user": update_user
        })
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"message": f"No record found with id {id_param}"}), 404

        return jsonify({"message": f"Record with id {id_param} updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📄 Ruta 9 (PROBADA Y FUNCIONAL): Activa uno o varios registros de horas (estado=1) y actualiza usuario/fecha.
# Recibe {"registro":[{"id":...}], "updateUser":"..."} y devuelve cuántos registros se activaron.
@catalogo_bp.route('/registro-horas/activate', methods=['POST'])
def activate_registro_horas():
    try:
        data = request.get_json()
        if not data or 'registro' not in data or 'updateUser' not in data:
            return jsonify({"error": "Faltan parámetros requeridos"}), 400

        ids = [item.get('id') for item in data['registro'] if item.get('id')]
        if not ids:
            return jsonify({"error": "Cada registro debe tener un 'id'"}), 400

        updated = 0
        sql = text("""
            UPDATE out_registro_horas
               SET estado = 1,
                   update_user = :update_user,
                   update_date = NOW()
             WHERE id = :id
        """)
        for _id in ids:
            res = db.session.execute(sql, {"update_user": data['updateUser'], "id": _id})
            updated += res.rowcount or 0

        db.session.commit()
        return jsonify({"message": f"{updated} registro(s) activados correctamente.", "ids": ids}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Route 10 (PROBADA Y FUNCIONAL): Filter projects by consultant (idConsultor), optional description, and status.
# GET /registro-proyecto/index?idConsultor=8&proyectoDescripcion=foo&estado=9
@catalogo_bp.route('/registro-proyecto/index', methods=['GET'])
def filter_projects():
    try:
        id_persona = request.args.get('idConsultor')
        descripcion = request.args.get('proyectoDescripcion')
        estado = request.args.get('estado')
        if not id_persona or not estado:
            return jsonify({'error': 'Missing required params: idConsultor and estado'}), 400

        sql = """
            SELECT id, id_persona, descripcion, estado
            FROM out_registro_proyecto
            WHERE id_persona = :id_persona
              AND estado = :estado
        """
        params = {'id_persona': id_persona, 'estado': estado}
        if descripcion:
            sql += " AND descripcion LIKE :descripcion"
            params['descripcion'] = f"%{descripcion}%"
        sql += " ORDER BY id DESC"

        rows = db.session.execute(text(sql), params).fetchall()
        return jsonify([dict(r._mapping) for r in rows]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route 11 (CREAR PROYECTO): Crea un registro para un consultor con código único por consultor.
# POST /registro-proyecto/save?idConsultor=8&codigo=SMF-003&proyectoDescripcion=Test&createUser=bsayan
@catalogo_bp.route('/registro-proyecto/save', methods=['POST'])
def create_project():
    try:
        id_persona  = request.args.get('idConsultor')
        codigo      = request.args.get('codigo')
        descripcion = request.args.get('proyectoDescripcion')
        create_user = request.args.get('createUser')

        # Validación mínima (mismo patrón que Route 10)
        if not id_persona or not codigo or not descripcion or not create_user:
            return jsonify({'error': 'Missing required params: idConsultor, codigo, proyectoDescripcion, createUser'}), 400

        # Evitar duplicados por (id_persona + codigo)
        dup_sql = """
            SELECT id
            FROM out_registro_proyecto
            WHERE id_persona = :id_persona
              AND codigo = :codigo
            LIMIT 1
        """
        dup = db.session.execute(text(dup_sql), {
            'id_persona': id_persona,
            'codigo': codigo
        }).fetchone()
        if dup:
            return jsonify({'error': 'Proyecto ya existe para ese consultor y código'}), 409

        # Insert usando columnas REALES de la tabla (create_date existe en tu schema)
        insert_sql = """
            INSERT INTO out_registro_proyecto
                (id_persona, codigo, descripcion, estado, create_user, create_date)
            VALUES
                (:id_persona, :codigo, :descripcion, :estado, :create_user, NOW())
        """
        params_insert = {
            'id_persona': id_persona,
            'codigo': codigo,
            'descripcion': descripcion,
            'estado': 1,          # activo por defecto
            'create_user': create_user
        }
        result = db.session.execute(text(insert_sql), params_insert)
        db.session.commit()

        new_id = result.lastrowid

        # Respuesta con MISMAS columnas que Route 10
        select_sql = """
            SELECT id, id_persona, descripcion, estado
            FROM out_registro_proyecto
            WHERE id = :id
        """
        # Si también quieres devolver 'codigo', usa este SELECT en su lugar:
        # select_sql = """
        #     SELECT id, id_persona, codigo, descripcion, estado
        #     FROM out_registro_proyecto
        #     WHERE id = :id
        # """

        row = db.session.execute(text(select_sql), {'id': new_id}).fetchone()
        return jsonify(dict(row._mapping) if row else {
            'id': new_id,
            'id_persona': id_persona,
            'descripcion': descripcion,
            'estado': 1
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route 12 (DELETE físico): elimina un proyecto y sus registros de horas asociados
# PUT /registro-proyecto/delete?idProyecto=269
@catalogo_bp.route('/registro-proyecto/delete', methods=['PUT'])
def delete_project():
    try:
        id_proyecto = request.args.get('idProyecto')

        if not id_proyecto:
            return jsonify({'error': 'Missing required param: idProyecto'}), 400

        # Verificar existencia
        row = db.session.execute(
            text("SELECT id FROM out_registro_proyecto WHERE id = :id LIMIT 1"),
            {'id': id_proyecto}
        ).fetchone()
        if not row:
            return jsonify({'error': f'Proyecto con id {id_proyecto} no existe'}), 404

        # Primero borrar registros hijos en out_registro_horas
        delete_horas_sql = """
            DELETE FROM out_registro_horas WHERE id_proyecto = :id
        """
        db.session.execute(text(delete_horas_sql), {'id': id_proyecto})

        # Luego borrar el proyecto en out_registro_proyecto
        delete_proyecto_sql = """
            DELETE FROM out_registro_proyecto WHERE id = :id
        """
        db.session.execute(text(delete_proyecto_sql), {'id': id_proyecto})

        db.session.commit()

        return jsonify({
            'message': f'Proyecto con id {id_proyecto} eliminado correctamente (DELETE físico)'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route 13 (UPDATE proyecto): Actualiza la información de un proyecto
# PUT /registro-proyecto/update?idPersona=8&idProyecto=280&proyectoDescripcion=TestV2&updateUser=bsayan
@catalogo_bp.route('/registro-proyecto/update', methods=['PUT'])
def update_project():
    try:
        id_persona   = request.args.get('idPersona')
        id_proyecto  = request.args.get('idProyecto')
        descripcion  = request.args.get('proyectoDescripcion')
        update_user  = request.args.get('updateUser')

        # Validación mínima
        if not id_persona or not id_proyecto or not descripcion or not update_user:
            return jsonify({'error': 'Missing required params: idPersona, idProyecto, proyectoDescripcion, updateUser'}), 400

        # Verificar existencia
        check_sql = """
            SELECT id FROM out_registro_proyecto
            WHERE id = :id AND id_persona = :id_persona
            LIMIT 1
        """
        exists = db.session.execute(text(check_sql), {
            'id': id_proyecto,
            'id_persona': id_persona
        }).fetchone()
        if not exists:
            return jsonify({'error': f'Proyecto con id {id_proyecto} no existe para consultor {id_persona}'}), 404

        # Actualizar registro
        update_sql = """
            UPDATE out_registro_proyecto
               SET descripcion = :descripcion,
                   update_user = :update_user,
                   update_date = NOW()
             WHERE id = :id AND id_persona = :id_persona
        """
        db.session.execute(text(update_sql), {
            'id': id_proyecto,
            'id_persona': id_persona,
            'descripcion': descripcion,
            'update_user': update_user
        })
        db.session.commit()

        # Devolver el registro actualizado
        select_sql = """
            SELECT id, id_persona, codigo, descripcion, estado, update_user, update_date
            FROM out_registro_proyecto
            WHERE id = :id
        """
        row = db.session.execute(text(select_sql), {'id': id_proyecto}).fetchone()

        return jsonify({
            'message': 'Proyecto actualizado correctamente',
            'data': dict(row._mapping) if row else {}
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route 14 (ACTIVAR proyectos): Activa uno o varios proyectos (estado=1)
# POST /registro-proyecto/activate
@catalogo_bp.route('/registro-proyecto/activate', methods=['POST'])
def activate_projects():
    try:
        update_user = request.form.get('updateUser') or (request.json or {}).get('updateUser')
        proyects    = request.form.getlist('proyects') or (request.json or {}).get('proyects')

        if not update_user or not proyects:
            return jsonify({'error': 'Missing required params: updateUser y proyects'}), 400

        # Si vienen como string separados por coma → convertir a lista
        if isinstance(proyects, str):
            proyects = [p.strip() for p in proyects.split(',') if p.strip()]

        # Actualizar estado a 1 (activo)
        update_sql = """
            UPDATE out_registro_proyecto
               SET estado = 1,
                   update_user = :update_user,
                   update_date = NOW()
             WHERE id IN :ids
        """
        db.session.execute(
            text(update_sql),
            {'update_user': update_user, 'ids': tuple(proyects)}
        )
        db.session.commit()

        return jsonify({
            'message': f'Proyectos {proyects} activados correctamente'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route 15: Incrementar estado cíclico (0→1→2→3→0)
# POST /registro-proyecto/changeStatus?idProyecto=268&updateUser=bsayan
@catalogo_bp.route('/registro-proyecto/changeStatus', methods=['POST'])
def change_project_status():
    try:
        id_proyecto = request.args.get('idProyecto')
        update_user = request.args.get('updateUser')
        if not id_proyecto or not update_user:
            return jsonify({'error': 'Missing required params: idProyecto, updateUser'}), 400

        # Leer estado actual
        row = db.session.execute(
            text("SELECT estado FROM out_registro_proyecto WHERE id = :id LIMIT 1"),
            {'id': id_proyecto}
        ).fetchone()
        if not row:
            return jsonify({'error': f'Proyecto {id_proyecto} no existe'}), 404

        try:
            estado_actual = int(row.estado)
        except (TypeError, ValueError):
            return jsonify({'error': f"Estado actual inválido: {row.estado}"}), 400

        # Ciclar de 0→1→2→3→0
        nuevo_estado = (estado_actual + 1) % 4

        db.session.execute(
            text("""
                UPDATE out_registro_proyecto
                   SET estado = :nuevo_estado,
                       update_user = :update_user,
                       update_date = NOW()
                 WHERE id = :id
            """),
            {'id': id_proyecto, 'update_user': update_user, 'nuevo_estado': nuevo_estado}
        )
        db.session.commit()

        return jsonify({
            'message': f'Estado del proyecto {id_proyecto} actualizado correctamente.',
            'estado_anterior': estado_actual,
            'estado_nuevo': nuevo_estado
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route 16: Editar Proyecto (compat: estado OR idPrioridad)
# Updates out_registro_proyecto: descripcion, estado, update_user, update_date

@catalogo_bp.route('/ticket/update/<int:id>', methods=['PUT'])
def update_ticket(id):
    try:
        usuario = request.args.get('usuario', type=str)

        # accept either ?estado= or legacy ?idPrioridad=
        estado = request.args.get('estado', type=int)
        if estado is None:
            estado = request.args.get('idPrioridad', type=int)

        descripcion = request.args.get('descripcion', type=str)

        if not usuario or estado is None or not descripcion:
            return jsonify({'error': 'Faltan parámetros requeridos: usuario, estado, descripcion'}), 400

        sql = text("""
            UPDATE out_registro_proyecto
            SET 
                estado = :estado,
                descripcion = :descripcion,
                update_user = :usuario,
                update_date = NOW()
            WHERE id = :id
        """)

        result = db.session.execute(sql, {
            'estado': estado,
            'descripcion': descripcion,
            'usuario': usuario,
            'id': id
        })
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({'error': 'Proyecto no encontrado'}), 404

        return jsonify({'message': 'Proyecto actualizado correctamente', 'id': id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Route 17: Derivar/Asignar Ticket (proyecto) a otro usuario
# Actualiza id_persona, update_user y update_date en out_registro_proyecto

@catalogo_bp.route('/ticket/usuario/asignar', methods=['POST'])
def asignar_ticket_usuario():
    try:
        usuario  = request.args.get('usuario', type=str)
        id_ticket = request.args.get('idTicket', type=int)
        asignar  = request.args.get('asignar', type=int)   # id de la persona a asignar

        if not usuario or id_ticket is None or asignar is None:
            return jsonify({'error': 'Faltan parámetros requeridos: usuario, idTicket, asignar'}), 400

        sql = text("""
            UPDATE out_registro_proyecto
            SET 
                id_persona   = :asignar,
                update_user  = :usuario,
                update_date  = NOW()
            WHERE id = :id_ticket
        """)

        result = db.session.execute(sql, {
            'asignar': asignar,
            'usuario': usuario,
            'id_ticket': id_ticket
        })
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({'error': 'Proyecto/Ticket no encontrado'}), 404

        return jsonify({'message': 'Ticket derivado correctamente', 'idTicket': id_ticket, 'asignadoA': asignar}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route 18: Reasignar Área (ajustado a tu DB real)
# Usa out_registro_proyecto: id_persona⇐idAreaDestino, codigo⇐idCatalogoServicio, update_user/update_date

@catalogo_bp.route('/ticket/reassign/<int:id>', methods=['POST'])
def reassign_area(id):
    try:
        id_area_destino      = request.form.get('idAreaDestino', type=int)   # ⇢ id_persona
        id_catalogo_servicio = request.form.get('idCatalogoServicio')        # ⇢ codigo (texto)
        usu_editado          = request.form.get('usuEditado', type=str)

        if id_area_destino is None or not id_catalogo_servicio or not usu_editado:
            return jsonify({'error': 'Faltan parámetros requeridos: idAreaDestino, idCatalogoServicio, usuEditado'}), 400

        sql = text("""
            UPDATE out_registro_proyecto
            SET 
                id_persona  = :id_area_destino,
                codigo      = :id_catalogo_servicio,
                update_user = :usu_editado,
                update_date = NOW()
            WHERE id = :id
        """)

        result = db.session.execute(sql, {
            'id_area_destino': id_area_destino,
            'id_catalogo_servicio': id_catalogo_servicio,
            'usu_editado': usu_editado,
            'id': id
        })
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({'error': 'Proyecto/Ticket no encontrado'}), 404

        return jsonify({'message': 'Ticket reasignado correctamente', 'idTicket': id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route 19: Reabrir Ticket (query params, método POST)
# Actualiza estado, descripcion, update_user y update_date en out_registro_proyecto

@catalogo_bp.route('/ticket/cerrar', methods=['POST'])
def reabrir_ticket():
    try:
        usuario     = request.args.get('usuario', type=str)
        id_ticket   = request.args.get('idTicket', type=int)
        estado_id   = request.args.get('estadoId', type=int)
        descripcion = request.args.get('descripcion', type=str)

        if not usuario or id_ticket is None or estado_id is None or not descripcion:
            return jsonify({'error': 'Faltan parámetros requeridos: usuario, idTicket, estadoId, descripcion'}), 400

        sql = text("""
            UPDATE out_registro_proyecto
            SET 
                estado      = :estado,
                descripcion = :descripcion,
                update_user = :usuario,
                update_date = NOW()
            WHERE id = :id
        """)
        result = db.session.execute(sql, {
            'estado': estado_id,
            'descripcion': descripcion,
            'usuario': usuario,
            'id': id_ticket
        })
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({'error': 'Proyecto/Ticket no encontrado'}), 404

        return jsonify({'message': 'Ticket reabierto correctamente', 'idTicket': id_ticket}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
