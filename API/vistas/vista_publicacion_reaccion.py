from datetime import datetime
from flask_restful import Resource
from flask import request
from sqlalchemy import and_

from API.modelos.modelos import Notificaciones, Publicacion
from ..modelos import db, Publicacion_Reaccion, Publicacion_ReaccionSchema

publicacion_reaccion_schema = Publicacion_ReaccionSchema()

class VistaPublicacionReaccion_All(Resource):
    def get(self):
        usuario_id = request.args.get('usuario')
        publicacion_id = request.args.get('publicacion')
        
        if usuario_id and publicacion_id:
            reaccion = Publicacion_Reaccion.query.filter(
                and_(
                    Publicacion_Reaccion.ID_usuario == usuario_id,
                    Publicacion_Reaccion.ID_publicacion == publicacion_id
                )
            ).first()
            
            if reaccion:
                return [publicacion_reaccion_schema.dump(reaccion)], 200
            else:
                return [], 200
        elif publicacion_id:
            reacciones = Publicacion_Reaccion.query.filter_by(
                ID_publicacion=publicacion_id
            ).all()
            return [publicacion_reaccion_schema.dump(r) for r in reacciones], 200
        else:
            reacciones = Publicacion_Reaccion.query.all()
            return [publicacion_reaccion_schema.dump(r) for r in reacciones], 200
    
    def post(self):
        data = request.get_json()
        
        # Obtener la reacción existente si existe
        reaccion_existente = Publicacion_Reaccion.query.filter_by(
            ID_usuario=data['ID_usuario'],
            ID_publicacion=data['ID_publicacion']
        ).first()
        
        # Obtener la publicación relacionada
        publicacion = Publicacion.query.get(data['ID_publicacion'])
        
        # Mapeo de reacción a tipo de notificación
        REACCION_A_NOTIFICACION = {
            1: 2,  # like -> notificación tipo 2
            2: 3,  # love -> notificación tipo 3
            3: 4,  # wow -> notificación tipo 4
            4: 5   # dislike -> notificación tipo 5
        }
        
        # Eliminar notificaciones anteriores relacionadas con esta reacción
        Notificaciones.query.filter(
            and_(
                Notificaciones.ID_usuario == publicacion.ID_usuario,
                Notificaciones.ID_usuario_accion == data['ID_usuario'],
                Notificaciones.ID_publicacion == data['ID_publicacion'],
                Notificaciones.ID_tipo_notificacion.in_(list(REACCION_A_NOTIFICACION.values()))
            )
        ).delete()

        if reaccion_existente:
            if reaccion_existente.ID_reaccion == data['ID_reaccion']:
                # Eliminar reacción existente
                db.session.delete(reaccion_existente)
                db.session.commit()
                return {'success': True, 'message': 'Reacción eliminada'}, 200
            else:
                # Actualizar reacción existente
                reaccion_existente.ID_reaccion = data['ID_reaccion']
        else:
            # Crear nueva reacción
            nueva_reaccion = Publicacion_Reaccion(
                ID_usuario=data['ID_usuario'],
                ID_publicacion=data['ID_publicacion'],
                ID_reaccion=data['ID_reaccion']
            )
            db.session.add(nueva_reaccion)
        
        # Crear nueva notificación solo si no es el propio usuario y hay una reacción
        if publicacion.ID_usuario != data['ID_usuario'] and data.get('ID_reaccion'):
            tipo_notificacion = REACCION_A_NOTIFICACION.get(data['ID_reaccion'], 2)  # Default a like (2) si no hay mapeo
            
            nueva_notificacion = Notificaciones(
                Leido=False,
                Fecha_notificacion=datetime.now(),
                ID_usuario=publicacion.ID_usuario,
                ID_usuario_accion=data['ID_usuario'],
                ID_tipo_notificacion=tipo_notificacion,
                ID_publicacion=data['ID_publicacion']
            )
            db.session.add(nueva_notificacion)
        
        db.session.commit()
        
        return publicacion_reaccion_schema.dump(reaccion_existente or nueva_reaccion), 200


class VistaPublicacionReaccion(Resource):
    def get(self, id):
        publicacion_reaccion = Publicacion_Reaccion.query.get(id)
        return publicacion_reaccion_schema.dump(publicacion_reaccion) if publicacion_reaccion else {'message': 'Publicacion Reaccion no encontrada'}, 404
    
    def delete(self, id):
        publicacion_reaccion = Publicacion_Reaccion.query.get(id)
        if not publicacion_reaccion:
            return {'message': 'Publicacion Reaccion no encontrada'}, 404
        
        db.session.delete(publicacion_reaccion)
        db.session.commit()
        return {'message': 'Publicacion Reaccion eliminada correctamente'}, 200