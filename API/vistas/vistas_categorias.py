from flask_restful import Resource
from flask import request
from ..modelos import db, Categorias, CategoriasSchema

categoria_schema = CategoriasSchema()
categorias_schema = CategoriasSchema(many=True)

class VistaCategorias(Resource):
    def get(self):
        categorias = Categorias.query.all()
        return categorias_schema.dump(categorias), 200

class VistaCategoria(Resource):
    def get(self, id):
        categoria = Categorias.query.get(id)
        if categoria:
            return categoria_schema.dump(categoria), 200
        return {'message': 'Categoría no encontrada'}, 404
    
    def post(self):
        data = request.get_json()
        nueva_categoria = Categorias(
            id_categoria=data['id_categoria'],
            nombre_categoria=data['nombre_categoria'],
            descripcion_categoria=data['descripcion_categoria'],
            id_publicacion=data['id_publicacion']
        )
        db.session.add(nueva_categoria)
        db.session.commit()
        return categoria_schema.dump(nueva_categoria), 201


    def put(self, id):
        categoria = Categorias.query.get(id)
        if categoria:
            data = request.get_json()
            categoria.id_categoria = data.get('id_categoria', categoria.id_categoria)
            categoria.nombre_categoria = data.get('nombre_categoria', categoria.nombre_categoria)
            categoria.descripcion_categoria = data.get('descripcion_categoria', categoria.descripcion_categoria)
            categoria.id_publicacion = data.get('id_publicacion', categoria.id_publicacion)

            db.session.commit()
            return categoria_schema.dump(categoria), 200
        return {'message': 'Categoría no encontrada'}, 404

    def delete(self, id):
        categoria = Categorias.query.get(id)
        if categoria:
            db.session.delete(categoria)
            db.session.commit()
            return {'message': 'Categoría eliminada correctamente'}, 200
        return {'message': 'Categoría no encontrada'}, 404
