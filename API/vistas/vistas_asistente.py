from flask_restful import Resource
from requests import request
from ..modelos import db, Asistente, AsistenteSchema

asistenteschema = AsistenteSchema()

class VistaAsistente_All(Resource):
    def get(self):
        asistentes = Asistente.query.all()
        return [asistenteschema.dump(asistente) for asistente in asistentes], 200

class VistaAsistente(Resource):
    def get(self, id=None):
        if id:
            asistente = Asistente.query.get(id)
            return asistenteschema.dump(asistente) if asistente else {'message': 'Asistente no encontrado'}, 404
        else:
            asistentes = Asistente.query.all()
            return [asistenteschema.dump(asistente) for asistente in asistentes], 200
        
    def post(self):
        data = request.get_json()
        nuevo_asistente = Asistente(**data)
        db.session.add(nuevo_asistente)
        db.session.commit()
        return asistenteschema.dump(nuevo_asistente), 201


    def put(self, id):
        asistente = Asistente.query.get(id)
        if not asistente:
            return {'message': 'Asistente no encontrado'}, 404

        data = request.get_json()
        for key, value in data.items():
            setattr(asistente, key, value)
        db.session.commit()
        return asistenteschema.dump(asistente), 200

    def delete(self, id):
        asistente = Asistente.query.get(id)
        if not asistente:
            return {'message': 'Asistente no encontrado'}, 400

        db.session.delete(asistente)
        db.session.commit()
        return {'message': 'Asistente eliminado correctamente'}, 200