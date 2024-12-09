from flask_restful import Resource
from requests import request
from ..modelos import db, Sexo, SexoSchema

sexoschema = SexoSchema()

class VistaSexo_All(Resource):
    def get(self):
        sexos = Sexo.query.all()
        return [sexoschema.dump(sexo) for sexo in sexos], 200

class VistaSexo(Resource):
    
    def get(self, id=None):
        if id:
            sexo = Sexo.query.get(id)
            return sexoschema.dump(sexo) if sexo else {'message': 'Sexo no encontrado'}, 404
        else:
            sexos = Sexo.query.all()
            return [sexoschema.dump(sexo) for sexo in sexos], 200
    
    def post(self):
        data = request.get_json()
        nuevo_sexo = Sexo(**data)
        db.session.add(nuevo_sexo)
        db.session.commit()
        return sexoschema.dump(nuevo_sexo), 201

    def put(self, id):
        sexo = Sexo.query.get(id)
        if not sexo:
            return {'message': 'Sexo no encontrado'}, 404
        
        data = request.get_json()
        for key, value in data.items():
            setattr(sexo, key, value)
        db.session.commit()
        return sexoschema.dump(sexo), 200

    def delete(self, id):
        sexo = Sexo.query.get(id)
        if not sexo:
            return {'message': 'Sexo no encontrado'}, 400

        db.session.delete(sexo)
        db.session.commit()
        return {'message': 'Sexo eliminado correctamente'}, 200