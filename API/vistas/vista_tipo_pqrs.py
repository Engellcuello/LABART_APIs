from flask_restful import Resource
from flask import request
from ..modelos import db, Tipo_PQRS, Tipo_PQRSSchema

tipo_pqrsschema = Tipo_PQRSSchema()

class Vistatipo_pqrs_All(Resource):
    def get(self):
        tipo_pqrss = Tipo_PQRS.query.all()
        return [tipo_pqrsschema.dump(tipo_pqrs) for tipo_pqrs in tipo_pqrss], 200
    
    def post(self):
        data = request.get_json()
        nuevo_tipo = Tipo_PQRS(**data)
        db.session.add(nuevo_tipo)
        db.session.commit()
        return tipo_pqrsschema.dump(nuevo_tipo), 200

class Vistatipo_pqrs(Resource):
    def get(self, id):
        tipo_pqrs = Tipo_PQRS.query.get_or_404(id)
        return tipo_pqrsschema.dump(tipo_pqrs), 200

    def put(self, id):
        tipo_pqrs = Tipo_PQRS.query.get_or_404(id)

        tipo_pqrs.ID_tipo_pqrs = request.json.get('ID_tipo_pqrs', tipo_pqrs.ID_tipo_pqrs)
        tipo_pqrs.Nombre_tipo = request.json.get('Nombre_tipo', tipo_pqrs.Nombre_tipo)
        tipo_pqrs.Descripcion_tipo = request.json.get('Descripcion_tipo', tipo_pqrs.Descripcion_tipo)

        db.session.commit()
        return tipo_pqrsschema.dump(tipo_pqrs), 200

    def delete(self, id):
        tipo_pqrs = Tipo_PQRS.query.get_or_404(id)
        db.session.delete(tipo_pqrs)
        db.session.commit()
        return {'message': 'Tipo PQRS eliminado correctamente', 'deleted_tipo_pqrs': tipo_pqrsschema.dump(tipo_pqrs)}, 200
