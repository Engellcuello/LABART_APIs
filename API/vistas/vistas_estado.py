from flask_restful import Resource

from requests import request

from ..modelos import db, Estado, EstadoSchema

estadoschema = EstadoSchema()

class VistaEstado_All(Resource):
    def get(self):
        estados = Estado.query.all()
        return [estadoschema.dump(estado) for estado in estados], 200
    
class VistaEstado(Resource):
    def get(self, id=None):
        if id:
            estado = Estado.query.get(id)
            return estadoschema.dump(estado) if estado else {'message': 'Estado no encontrado'}, 404
        else:
            estados = Estado.query.all()
            return [estadoschema.dump(estado) for estado in estados], 200

    def post(self):
        data = request.get_json()
        nuevo_estado = Estado(**data)
        db.session.add(nuevo_estado)
        db.session.commit()
        return estadoschema.dump(nuevo_estado), 201
    
    def put(self, id):
        estado = Estado.query.get(id)
        if not estado:
            return {'message': 'Estado no encontrado'}, 404
        
        data = request.get_json()
        for key, value in data.items():
            setattr(estado, key, value)
        db.session.commit()
        return estadoschema.dump(estado), 200
    
    def delete(self, id):
        estado = Estado.query.get(id)
        if not estado:
            return {'message': 'Estado no encontrado'}, 404

        db.session.delete(estado)
        db.session.commit()
        return {'message': 'Estado eliminado correctamente'}, 200
