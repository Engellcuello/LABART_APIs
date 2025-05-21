from flask_restful import Resource
from flask import request, jsonify
from ..modelos import db, Etiqueta_Publicacion, Etiqueta_PublicacionSchema, Publicacion

etiqueta_publicacion_schema = Etiqueta_PublicacionSchema()

class VistaEtiquetaPublicacion_All(Resource):
    def get(self):
        etiquetas = Etiqueta_Publicacion.query.all()
        return [etiqueta_publicacion_schema.dump(etiqueta) for etiqueta in etiquetas], 200
    
    def post(self):
        data = request.get_json()
        nueva_etiqueta = Etiqueta_Publicacion(**data)
        db.session.add(nueva_etiqueta)
        db.session.commit()
        return etiqueta_publicacion_schema.dump(nueva_etiqueta), 200

class VistaEtiquetaPublicacion(Resource):
    def get(self, id_etiqueta_publicacion):
        etiqueta = Etiqueta_Publicacion.query.get_or_404(id_etiqueta_publicacion)
        return etiqueta_publicacion_schema.dump(etiqueta), 200

    def put(self, id_etiqueta_publicacion):
        etiqueta = Etiqueta_Publicacion.query.get_or_404(id_etiqueta_publicacion)
        etiqueta.descripcion = request.json.get('descripcion', etiqueta.descripcion)
        etiqueta.score = request.json.get('score', etiqueta.score)
        etiqueta.topicality = request.json.get('topicality', etiqueta.topicality)
        etiqueta.ID_publicacion = request.json.get('ID_publicacion', etiqueta.ID_publicacion)
        etiqueta.ID_usuario = request.json.get('ID_usuario', etiqueta.ID_usuario)
        db.session.commit()
        return etiqueta_publicacion_schema.dump(etiqueta), 200

    def delete(self, id_etiqueta_publicacion):
        etiqueta = Etiqueta_Publicacion.query.get(id_etiqueta_publicacion)
        if not etiqueta:
            return {'message': 'Etiqueta de publicación no encontrada'}, 404
        db.session.delete(etiqueta)
        db.session.commit()
        return {'message': 'Etiqueta de publicación eliminada correctamente'}, 200
    

class VistaDescripcionesUnicas(Resource):
    def get(self):
        # Obtiene solo las descripciones distintas (únicas) de la tabla
        descripciones_unicas = db.session.query(Etiqueta_Publicacion.descripcion).distinct().all()
        # Convierte la lista de tuplas a una lista simple
        descripciones = [descripcion[0] for descripcion in descripciones_unicas]
        return descripciones, 200
    
class EtiquetasPublicacionResource(Resource):
    """Recurso para manejar las etiquetas de una publicación específica"""
    
    def get(self, publicacion_id):
        if not Publicacion.query.get(publicacion_id):
            return {'mensaje': 'Publicación no encontrada'}, 404
            
        etiquetas = Etiqueta_Publicacion.query.filter_by(
            ID_publicacion=publicacion_id
        ).all()
        
        return jsonify({
        'etiquetas': [{
            'ID_etiqueta_publicacion': etiqueta.ID_etiqueta_publicacion,
            'descripcion': etiqueta.descripcion,
            'score': etiqueta.score,
            'topicality': etiqueta.topicality,
            'ID_usuario': etiqueta.ID_usuario
        } for etiqueta in etiquetas] or []  
    })

class EtiquetasDisponiblesResource(Resource):
    def get(self):
        etiquetas = db.session.query(
            Etiqueta_Publicacion.descripcion
        ).distinct().all()
        
        return [etiqueta[0] for etiqueta in etiquetas], 200

class AsignarEtiquetaPublicacionResource(Resource):
    def post(self, publicacion_id):
        if not Publicacion.query.get(publicacion_id):
            return {'mensaje': 'Publicación no encontrada'}, 404
            
        datos = request.get_json()
        ID_usuario = datos['ID_usuario']
        descripcion = datos['descripcion']
        
        # Verificar si la etiqueta ya existe para esta publicación
        existe = Etiqueta_Publicacion.query.filter_by(
            ID_publicacion=publicacion_id,
            descripcion=descripcion
        ).first()
        
        if existe:
            return {'mensaje': 'Esta etiqueta ya está asignada a la publicación'}, 400
        
        # Crear nueva relación etiqueta-publicación
        nueva_relacion = Etiqueta_Publicacion(
            descripcion=descripcion,
            score=90.0,  # Valor por defecto
            topicality=85.0,  # Valor por defecto
            ID_publicacion=publicacion_id,
            ID_usuario=ID_usuario
        )
        
        db.session.add(nueva_relacion)
        db.session.commit()
        
        return etiqueta_publicacion_schema.dump(nueva_relacion), 201
    

