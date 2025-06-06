from flask_restful import Resource
from flask import request
from ..modelos import db, PQRS, PQRSSchema

pqrs_schema = PQRSSchema()

class VistaPQRS_All(Resource):
    def get(self):
        pqrs_list = PQRS.query.all()
        return [pqrs_schema.dump(pqrs) for pqrs in pqrs_list], 200
    
    def post(self):
        data = request.get_json()
        nueva_pqrs = PQRS(**data)
        db.session.add(nueva_pqrs)
        db.session.commit()
        return pqrs_schema.dump(nueva_pqrs), 200

class VistaPQRS(Resource):
    def get(self, id):
        pqrs = PQRS.query.get(id)
        return pqrs_schema.dump(pqrs) if pqrs else {'message': 'PQRS no encontrada'}, 404
    
    def put(self, id):
        pqrs = PQRS.query.get_or_404(id)
        
        pqrs.Fecha_pqrs = request.json.get('Fecha_pqrs', pqrs.Fecha_pqrs)
        pqrs.Contenido_pqrs = request.json.get('Contenido_pqrs', pqrs.Contenido_pqrs)
        pqrs.ID_estado = request.json.get('ID_estado', pqrs.ID_estado)
        pqrs.ID_usuario = request.json.get('ID_usuario', pqrs.ID_usuario)
        pqrs.ID_tipo_pqrs = request.json.get('ID_tipo_pqrs', pqrs.ID_tipo_pqrs)
        
        db.session.commit()
        return pqrs_schema.dump(pqrs), 200
    
    def delete(self, id):
        pqrs = PQRS.query.get(id)
        if not pqrs:
            return {'message': 'PQRS no encontrada'}, 404
        
        db.session.delete(pqrs)
        db.session.commit()
        return {'message': 'PQRS eliminada correctamente'}, 200
