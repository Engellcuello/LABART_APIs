from datetime import datetime
from flask_restful import Resource
from flask import request

from API.modelos.modelos import Notificaciones, Publicacion
from ..modelos import db, Comentario, ComentarioSchema

comentarioschema = ComentarioSchema()

class VistaComentario_All(Resource):
    def get(self):
        comentarios = Comentario.query.all()
        return [comentarioschema.dump(comentario) for comentario in comentarios], 200
    
    def post(self):
        data = request.get_json()
        
        # Obtener la publicación relacionada
        publicacion = Publicacion.query.get(data['ID_publicacion'])
        
        # Crear nuevo comentario
        nuevo_comentario = Comentario(**data)
        db.session.add(nuevo_comentario)
        
        # Crear notificación solo si no es el propio usuario
        if publicacion.ID_usuario != data['ID_usuario']:
            nueva_notificacion = Notificaciones(
                Leido=False,
                Fecha_notificacion=datetime.now(),
                ID_usuario=publicacion.ID_usuario,
                ID_usuario_accion=data['ID_usuario'],
                ID_tipo_notificacion=3,  # 6 = Tipo de notificación para comentarios
                ID_publicacion=data['ID_publicacion'],
            )
            db.session.add(nueva_notificacion)
        
        db.session.commit()
        return comentarioschema.dump(nuevo_comentario), 200

class VistaComentario(Resource):
    def delete(self, id_comentario):
        comentario = Comentario.query.get_or_404(id_comentario)
        
        # Eliminar notificaciones relacionadas con este comentario
        Notificaciones.query.filter_by(
            ID_comentario=id_comentario
        ).delete()
        
        db.session.delete(comentario)
        db.session.commit()
        return '', 204

class VistaComentario(Resource):
    def get(self, id=None):
        if id:
            comentario = Comentario.query.get(id)
            if comentario:
                return comentarioschema.dump(comentario), 200
            else:
                return {'message': 'Comentario no encontrado'}, 404
        else:
            comentarios = Comentario.query.all()
            return [comentarioschema.dump(comentario) for comentario in comentarios], 200

    def put(self, id):
        comentario = Comentario.query.get_or_404(id)
        comentario.ID_comentario = request.json.get('ID_comentario', comentario.ID_comentario)
        comentario.Contenido_comentario = request.json.get('Contenido_comentario', comentario.Contenido_comentario)
        comentario.Fecha_comentario = request.json.get('Fecha_comentario', comentario.Fecha_comentario)
        comentario.ID_usuario = request.json.get('ID_usuario', comentario.ID_usuario)
        comentario.ID_publicacion = request.json.get('ID_publicacion', comentario.ID_publicacion)
        db.session.commit()
        return comentarioschema.dump(comentario), 200

    def delete(self, id):
        comentario = Comentario.query.get(id)
        if not comentario:
            return {'message': 'Comentario no encontrado'}, 400
        db.session.delete(comentario)
        db.session.commit()
        return {'message': 'Comentario eliminado correctamente'}, 200
