from flask_restful import Resource
from flask import request
from ..modelos import db, Asistente, AsistenteSchema

asistenteschema = AsistenteSchema()

class VistaAsistente_All(Resource):
    def get(self):
        asistentes = Asistente.query.all()
        return [asistenteschema.dump(asistente) for asistente in asistentes], 200
    
    def post(self):
        data = request.get_json()
        nuevo_asistente = Asistente(**data)
        db.session.add(nuevo_asistente)
        db.session.commit()
        return asistenteschema.dump(nuevo_asistente), 201

class VistaAsistente(Resource):
    def get(self, id):
        asistente = Asistente.query.get_or_404(id)
        return asistenteschema.dump(asistente), 200

    def put(self, id):
        asistente = Asistente.query.get_or_404(id)
        asistente.ID_asistente = request.json.get('ID_asistente', asistente.ID_asistente)
        asistente.Fecha_peticion = request.json.get('Fecha_peticion', asistente.Fecha_peticion)
        asistente.Detalle_asistente = request.json.get('Detalle_asistente', asistente.Detalle_asistente)
        asistente.ID_estado = request.json.get('ID_estado', asistente.ID_estado)
        asistente.ID_usuario = request.json.get('ID_usuario', asistente.ID_usuario)
        
        db.session.commit()
        return asistenteschema.dump(asistente), 200

    def delete(self, id):
        asistente = Asistente.query.get_or_404(id)
        db.session.delete(asistente)
        db.session.commit()
        return {'message': 'Asistente eliminado correctamente', 'deleted_asistente': asistenteschema.dump(asistente)}, 200
