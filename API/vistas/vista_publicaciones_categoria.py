from flask_restful import Resource
from flask import request
from ..modelos import db, Publicacion, PublicacionSchema, Publicacion_Categoria, Publicacion_CategoriaSchema

publicacion_schema = PublicacionSchema()
publicaciones_schema = PublicacionSchema(many=True)

class VistaPublicacionesPorCategoria(Resource):
    def get(self, id_categoria):
        publicaciones = (
            db.session.query(Publicacion)
            .join(Publicacion_Categoria, Publicacion.ID_publicacion == Publicacion_Categoria.ID_publicacion)
            .filter(Publicacion_Categoria.ID_categoria == id_categoria)
            .all()
        )
        return publicaciones_schema.dump(publicaciones), 200
    