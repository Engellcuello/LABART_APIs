from flask_restful import Resource
from flask import request  # ✅ Importación correcta
from ..modelos import db, Sexo, SexoSchema

sexoschema = SexoSchema()

class VistaSexo_All(Resource):
    def get(self):
        sexos = Sexo.query.all()
        return [sexoschema.dump(sexo) for sexo in sexos], 200
    
    def post(self):
        data = request.get_json()  # ✅ Ahora `request` está correctamente importado
        nuevo_sexo = Sexo(**data)
        db.session.add(nuevo_sexo)
        db.session.commit()
        return sexoschema.dump(nuevo_sexo), 201

class VistaSexo(Resource):
    
    def get(self, id=None):
        if id:
            sexo = Sexo.query.get_or_404(id)  # ✅ get_or_404 evita un `None`
            return sexoschema.dump(sexo), 200
        else:
            sexos = Sexo.query.all()
            return [sexoschema.dump(sexo) for sexo in sexos], 200

    def put(self, id):
        sexo = Sexo.query.get_or_404(id)  # ✅ get_or_404 simplifica la validación
        
        data = request.get_json()
        for key, value in data.items():
            setattr(sexo, key, value)
        db.session.commit()
        return sexoschema.dump(sexo), 200

    def delete(self, id):
        sexo = Sexo.query.get_or_404(id)  # ✅ get_or_404 simplifica la validación

        db.session.delete(sexo)
        db.session.commit()
        return {'message': 'Sexo eliminado correctamente', 'deleted_sexo': sexoschema.dump(sexo)}, 200
