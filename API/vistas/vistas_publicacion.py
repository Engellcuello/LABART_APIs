from flask_restful import Resource
from flask import request
from ..modelos import db, Publicacion, PublicacionSchema

publicacion_schema = PublicacionSchema()
publicaciones_schema = PublicacionSchema(many=True)

class VistaPublicaciones(Resource):
    def get(self):
        publicaciones = Publicacion.query.all()
        return publicaciones_schema.dump(publicaciones), 200

class VistaPublicacion(Resource):
    def get(self, id):
        publicacion = Publicacion.query.get(id)
        if publicacion:
            return publicacion_schema.dump(publicacion), 200
        return {'message': 'Publicación no encontrada'}, 404
    
    def post(self):
        data = request.get_json()
        nueva_publicacion = Publicacion(
            id_publicacion=data['id_publicacion'],
            fecha_publicacion=data['fecha_publicacion'],
            descripcion_publicacion=data['descripcion_publicacion'],
            img_publicacion=data['img_publicacion'],
            cont_explicit_public=data['cont_explicit_public'],
            id_usuario=data['id_usuario'],
            id_reaccion=data['id_reaccion'],
            id_categoria=data['id_categoria']
        )
        db.session.add(nueva_publicacion)
        db.session.commit()
        return publicacion_schema.dump(nueva_publicacion), 201

    def put(self, id):
        publicacion = Publicacion.query.get(id)
        if publicacion:
            data = request.get_json()
            publicacion.id_publicacion = data.get('id_publicacion', publicacion.id_publicacion)
            publicacion.fecha_publicacion = data.get('fecha_publicacion', publicacion.fecha_publicacion)
            publicacion.descripcion_publicacion = data.get('descripcion_publicacion', publicacion.descripcion_publicacion)
            publicacion.img_publicacion = data.get('img_publicacion', publicacion.img_publicacion)
            publicacion.cont_explicit_public = data.get('cont_explicit_public', publicacion.cont_explicit_public)
            publicacion.id_usuario = data.get('id_usuario', publicacion.id_usuario)
            publicacion.id_reaccion = data.get('id_reaccion', publicacion.id_reaccion)
            publicacion.id_categoria = data.get('id_categoria', publicacion.id_categoria)

            db.session.commit()
            return publicacion_schema.dump(publicacion), 200
        return {'message': 'Publicación no encontrada'}, 404

    def delete(self, id):
        publicacion = Publicacion.query.get(id)
        if publicacion:
            db.session.delete(publicacion)
            db.session.commit()
            return {'message': 'Publicación eliminada correctamente'}, 200
        return {'message': 'Publicación no encontrada'}, 404
