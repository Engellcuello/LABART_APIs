from flask_restful import Resource
from flask import request
from ..modelos import db, Estado, EstadoSchema

estadoschema = EstadoSchema()

class VistaEstado_All(Resource):
    def get(self):
        estados = Estado.query.all()
        return [estadoschema.dump(estado) for estado in estados], 200

    def post(self):
        data = request.get_json()
        nuevo_estado = Estado(**data)
        db.session.add(nuevo_estado)
        db.session.commit()
        return estadoschema.dump(nuevo_estado), 201


class VistaEstado(Resource):
    def get(self, id=None):
        if id:
            estado = Estado.query.get_or_404(id)
            return estadoschema.dump(estado), 200
        else:
            estados = Estado.query.all()
            return [estadoschema.dump(estado) for estado in estados], 200

    def put(self, id):
        estado = Estado.query.get_or_404(id)
        estado.Nombre_estado = request.json.get('Nombre_estado', estado.Nombre_estado)
        estado.Descripcion_estado = request.json.get('Descripcion_estado', estado.Descripcion_estado)
        db.session.commit()
        return estadoschema.dump(estado), 200

    def delete(self, id):
        estado = Estado.query.get_or_404(id)
        db.session.delete(estado)
        db.session.commit()
        return {'message': 'Estado eliminado correctamente', 'deleted_estado': estadoschema.dump(estado)}, 200