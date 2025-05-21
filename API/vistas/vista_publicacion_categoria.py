from flask_restful import Resource
from flask import request
from sqlalchemy import desc
from ..modelos import db, Publicacion_Categoria, Publicacion_CategoriaSchema, PublicacionSchema, Publicacion

publicacion_categoria_schema = Publicacion_CategoriaSchema()
publicacion_schema = PublicacionSchema()


class VistaPublicacionCategoria_All(Resource):
    def get(self):
        publicacion_categorias = Publicacion_Categoria.query.all()
        return [publicacion_categoria_schema.dump(publicacion_categoria) for publicacion_categoria in publicacion_categorias], 200
    
    def post(self):
        data = request.get_json()
        nueva_publicacion_categoria = Publicacion_Categoria(**data)
        db.session.add(nueva_publicacion_categoria)
        db.session.commit()
        return publicacion_categoria_schema.dump(nueva_publicacion_categoria), 200

class VistaPublicacionCategoria(Resource):
    def get(self, id):
        publicacion_categoria = Publicacion_Categoria.query.get(id)
        return publicacion_categoria_schema.dump(publicacion_categoria) if publicacion_categoria else {'message': 'Publicacion Categoria no encontrada'}, 404
    
    def put(self, id):
        publicacion_categoria = Publicacion_Categoria.query.get_or_404(id)
        
        publicacion_categoria.ID_publicacion = request.json.get('ID_publicacion', publicacion_categoria.ID_publicacion)
        publicacion_categoria.ID_categoria = request.json.get('ID_categoria', publicacion_categoria.ID_categoria)
        
        db.session.commit()
        return publicacion_categoria_schema.dump(publicacion_categoria), 200
    
    def delete(self, id):
        publicacion_categoria = Publicacion_Categoria.query.get(id)
        if not publicacion_categoria:
            return {'message': 'Publicacion Categoria no encontrada'}, 404
        
        db.session.delete(publicacion_categoria)
        db.session.commit()
        return {'message': 'Publicacion Categoria eliminada correctamente'}, 200


class VistaPublicacionesPorCategoria(Resource):
    def get(self, id_categoria):
        try:
            publicaciones = self.obtener_publicaciones_por_categoria(id_categoria)
            
            if not publicaciones:
                return {'message': 'No se encontraron publicaciones para esta categoría'}, 404
                
            return [publicacion_schema.dump(pub) for pub in publicaciones], 200
            
        except Exception as e:
            return {'message': f'Error al obtener publicaciones: {str(e)}'}, 500

    def obtener_publicaciones_por_categoria(self, id_categoria):
        return Publicacion.query\
            .join(Publicacion_Categoria, Publicacion.ID_publicacion == Publicacion_Categoria.ID_publicacion)\
            .filter(Publicacion_Categoria.ID_categoria == id_categoria)\
            .order_by(desc(Publicacion.Fecha_Publicacion))\
            .all()
            
            

class VistaCategoriasDePublicacion(Resource):
    def get(self, id_publicacion):
        try:
            # Obtener todas las relaciones Publicacion_Categoria para esta publicación
            relaciones = Publicacion_Categoria.query.filter_by(ID_publicacion=id_publicacion).all()
            
            if not relaciones:
                return {'message': 'No se encontraron categorías para esta publicación'}, 404
            
            # Extraer las categorías completas
            categorias = [rel.categoria for rel in relaciones]
            
            # Usar el schema de Categoria (asegúrate de importarlo)
            from ..modelos import CategoriaSchema
            return CategoriaSchema(many=True).dump(categorias), 200
            
        except Exception as e:
            return {'message': f'Error al obtener categorías: {str(e)}'}, 500
        
    def delete(self,id_publicacion):
        try:
            Publicacion_Categoria.query.filter_by(ID_publicacion=id_publicacion).delete()
            db.session.commit()
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
        
    def post():
        data = request.get_json()
        nueva_relacion = Publicacion_Categoria(
            ID_publicacion=data['ID_publicacion'],
            ID_categoria=data['ID_categoria']
        )
        db.session.add(nueva_relacion)
        db.session.commit()
        return jsonify({'status': 'success'})

    
