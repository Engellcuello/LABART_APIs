from flask_restful import Resource
from flask import request

from API.modelos.modelos import db,Color_Publicacion, Color_PublicacionSchema


color_publicacion_schema = Color_PublicacionSchema()

class VistaColorPublicacion_All(Resource):
    def get(self):
        colores = Color_Publicacion.query.all()
        return [color_publicacion_schema.dump(color) for color in colores], 200
    
    def post(self):
        data = request.get_json()
        nuevo_color = Color_Publicacion(**data)
        db.session.add(nuevo_color)
        db.session.commit()
        return color_publicacion_schema.dump(nuevo_color), 200

class VistaColorPublicacion(Resource):
    def get(self, id_color_publicacion):
        color = Color_Publicacion.query.get_or_404(id_color_publicacion)
        return color_publicacion_schema.dump(color), 200

    def put(self, id_color_publicacion):
        color = Color_Publicacion.query.get_or_404(id_color_publicacion)
        color.red = request.json.get('red', color.red)
        color.green = request.json.get('green', color.green)
        color.blue = request.json.get('blue', color.blue)
        color.pixel_fraction = request.json.get('pixel_fraction', color.pixel_fraction)
        color.score = request.json.get('score', color.score)
        color.ID_publicacion = request.json.get('ID_publicacion', color.ID_publicacion)
        color.ID_usuario = request.json.get('ID_usuario', color.ID_usuario)
        db.session.commit()
        return color_publicacion_schema.dump(color), 200

    def delete(self, id_color_publicacion):
        color = Color_Publicacion.query.get(id_color_publicacion)
        if not color:
            return {'message': 'Color de publicación no encontrado'}, 404
        db.session.delete(color)
        db.session.commit()
        return {'message': 'Color de publicación eliminado correctamente'}, 200