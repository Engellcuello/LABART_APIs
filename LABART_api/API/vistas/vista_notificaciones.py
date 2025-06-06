from flask_restful import Resource
from flask import request 
from sqlalchemy import desc

from API.modelos.modelos import Publicacion, PublicacionSchema, TipoNotificacion, Usuario
from ..modelos import db, Notificaciones, NotificacionesSchema

notificacionschema = NotificacionesSchema()
publicacion_schema = PublicacionSchema()
class VistaNotificacion_All(Resource):
    def get(self):
        notificaciones = Notificaciones.query.all()
        return [notificacionschema.dump(notificacion) for notificacion in notificaciones], 200
    
    def post(self):
        data = request.get_json()
        nueva_notificacion = Notificaciones(**data)
        db.session.add(nueva_notificacion)
        db.session.commit()
        return notificacionschema.dump(nueva_notificacion), 200

class VistaNotificacion(Resource):
    def get(self, id=None):
        if id:
            notificacion = Notificaciones.query.get(id)
            return notificacionschema.dump(notificacion) if notificacion else {'message': 'Notificacion no encontrada'}, 404
        else:
            notificaciones = Notificaciones.query.all()
            return [notificacionschema.dump(notificacion) for notificacion in notificaciones], 200

    def put(self, id):
        notificacion = Notificaciones.query.get_or_404(id)

        if 'leido' in request.json:
            notificacion.Leido = request.json['leido']
            db.session.commit()
            return notificacionschema.dump(notificacion), 200

        notificacion.ID_notificaciones = request.json.get('ID_notificaciones', notificacion.ID_notificaciones)
        notificacion.Leido = request.json.get('Leido', notificacion.Leido)
        notificacion.Fecha_notificacion = request.json.get('Fecha_notificacion', notificacion.Fecha_notificacion)
        notificacion.ID_usuario = request.json.get('ID_usuario', notificacion.ID_usuario)
        notificacion.ID_usuario_accion = request.json.get('ID_usuario_accion', notificacion.ID_usuario_accion)
        notificacion.ID_tipo_notificacion = request.json.get('ID_tipo_notificacion', notificacion.ID_tipo_notificacion)


        db.session.commit()
        return notificacionschema.dump(notificacion), 200


    def delete(self, id):
        notificacion = Notificaciones.query.get(id)
        if not notificacion:
            return {'message': 'Notificacion no encontrada'}, 400

        db.session.delete(notificacion)
        db.session.commit()
        return {'message': 'Notificacion eliminado correctamente'}, 200


class VistaNotificacionesUsuario(Resource):
    def get(self, id_usuario):
        """
        Obtiene todas las notificaciones de un usuario organizadas en 2 categorías:
        1. Comentarios (tipo notificación 6)
        2. Reacciones (tipos 2, 3, 4, 5)
        
        Cada categoría ordenada:
        - Primero las no leídas
        - Luego por fecha (más recientes primero)
        """
        
        notificaciones = db.session.query(
            Notificaciones,
            TipoNotificacion.Nombre.label('tipo_notificacion'),
            TipoNotificacion.Mensaje_base,
            TipoNotificacion.ID_tipo_notificacion.label('id_tipo'),
            Usuario.Nombre_usuario.label('nombre_usuario_accion'),
            Usuario.Img_usuario.label('imagen_usuario_accion'),
            Publicacion.Img_publicacion.label('imagen_publicacion'),
            Publicacion.ID_publicacion.label('id_publicacion_publicacion')
        ).join(
            TipoNotificacion, Notificaciones.ID_tipo_notificacion == TipoNotificacion.ID_tipo_notificacion
        ).join(
            Usuario, Notificaciones.ID_usuario_accion == Usuario.ID_usuario
        ).outerjoin(
            Publicacion, Notificaciones.ID_publicacion == Publicacion.ID_publicacion
        ).filter(
            Notificaciones.ID_usuario == id_usuario,
            Notificaciones.ID_tipo_notificacion.in_([2, 3, 4, 5, 6]) 
        ).order_by(
            Notificaciones.Leido.asc(),
            desc(Notificaciones.Fecha_notificacion)
        ).all()

        comentarios = []
        reacciones = []

        for notif in notificaciones:
            notificacion_data = {
                'id': notif.Notificaciones.ID_notificaciones,
                'leida': notif.Notificaciones.Leido,
                'fecha': notif.Notificaciones.Fecha_notificacion.isoformat(),
                'tipo': notif.tipo_notificacion,
                'id_tipo': notif.id_tipo,
                'mensaje': notif.Mensaje_base,
                'usuario_accion': {
                    'id': notif.Notificaciones.ID_usuario_accion,
                    'nombre': notif.nombre_usuario_accion,
                    'imagen': notif.imagen_usuario_accion
                },
                'imagen_publicacion': notif.imagen_publicacion,
                'id_publicacion': notif.id_publicacion_publicacion
            }

            if notif.id_tipo == 6: 
                comentarios.append(notificacion_data)
            elif notif.id_tipo in [2, 3, 4, 5]:  
                reacciones.append(notificacion_data)

        # Estructura de respuesta final
        respuesta = {
            'comentarios': comentarios,
            'reacciones': reacciones
        }

        return respuesta, 200
    
class VistaEliminarNotificacionesPorTipoYUsuario(Resource):
    def delete(self, id_usuario):
        """
        Elimina todas las notificaciones de un usuario con uno o varios tipos de notificación.
        Espera un JSON como:
        {
            "tipos": [2,3,4,5]
        }
        """
        # Verificar que la petición tenga contenido JSON
        if not request.is_json:
            return {
                'message': 'El cuerpo de la petición debe ser JSON',
                'success': False
            }, 400, {'Content-Type': 'application/json'}

        data = request.get_json(silent=True)
        if data is None:
            return {
                'message': 'JSON mal formado',
                'success': False
            }, 400, {'Content-Type': 'application/json'}

        tipos = data.get('tipos')

        if not tipos or not isinstance(tipos, list):
            return {
                'message': 'Debe proporcionar una lista de tipos de notificación válidos',
                'success': False
            }, 400, {'Content-Type': 'application/json'}

        # Usar delete() con synchronize_session=False para mejor performance
        try:
            num_eliminadas = Notificaciones.query.filter(
                Notificaciones.ID_usuario == id_usuario,
                Notificaciones.ID_tipo_notificacion.in_(tipos)
            ).delete(synchronize_session=False)
            
            db.session.commit()
            
            return {
                'message': f'Se eliminaron {num_eliminadas} notificaciones correctamente',
                'success': True,
                'count': num_eliminadas
            }, 200, {'Content-Type': 'application/json'}
            
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'Error al eliminar notificaciones: {str(e)}',
                'success': False
            }, 500, {'Content-Type': 'application/json'}
        
class VistaMarcarNotificacionesLeidas(Resource):
    def post(self, id_usuario):
        """
        Marca notificaciones como leídas para un usuario específico
        """
        try:
            # Verificar que la petición tiene datos JSON
            if not request.is_json:
                return {'message': 'El cuerpo debe ser JSON', 'success': False}, 400

            data = request.get_json()
            notification_ids = data.get('notificaciones', [])

            # Validación básica
            if not isinstance(notification_ids, list):
                return {'message': 'notificaciones debe ser una lista', 'success': False}, 400

            if not notification_ids:
                return {'message': 'La lista de notificaciones está vacía', 'success': False}, 400

            # Convertir IDs a enteros
            try:
                notification_ids = [int(nid) for nid in notification_ids]
            except ValueError:
                return {'message': 'IDs de notificación inválidos', 'success': False}, 400

            # DEBUG: Imprimir los IDs recibidos
            print(f"IDs recibidos para marcar como leídos: {notification_ids}")

            # Actualizar en la base de datos
            updated = db.session.query(Notificaciones).filter(
                Notificaciones.ID_notificaciones.in_(notification_ids),
                Notificaciones.ID_usuario == id_usuario
            ).update({'Leido': True}, synchronize_session=False)

            db.session.commit()

            # DEBUG: Imprimir resultado
            print(f"Notificaciones actualizadas: {updated}")

            return {
                'message': f'{updated} notificaciones marcadas como leídas',
                'success': True,
                'count': updated
            }, 200

        except Exception as e:
            db.session.rollback()
            print(f"Error en el endpoint: {str(e)}")
            return {
                'message': f'Error interno al marcar notificaciones: {str(e)}',
                'success': False
            }, 500
        

class VistaNotificacionesNoLeidas(Resource):
    def get(self, id_usuario):
        """
        Verifica si un usuario tiene notificaciones no leídas
        Retorna: 
        {
            "tiene_no_leidas": bool,
            "cantidad": int
        }
        """
        try:
            # Contar notificaciones no leídas
            cantidad = Notificaciones.query.filter(
                Notificaciones.ID_usuario == id_usuario,
                Notificaciones.Leido == False
            ).count()

            return {
                "tiene_no_leidas": cantidad > 0,
                "cantidad": cantidad
            }, 200

        except Exception as e:
            return {
                "message": f"Error al verificar notificaciones: {str(e)}",
                "success": False
            }, 500
            
class VistaMarcarNotificacionesComoLeidas(Resource):
    def put(self, id_usuario):
        notificaciones = Notificaciones.query.filter_by(ID_usuario=id_usuario, Leido=False).all()
        for notificacion in notificaciones:
            notificacion.Leido = True
        db.session.commit()
        return {'mensaje': 'Notificaciones marcadas como leídas'}, 200
            
