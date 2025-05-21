from flask_restful import Resource

from requests import request
from flask import request


from ..modelos import db, Reaccion, ReaccionSchema

reaccionschema = ReaccionSchema()

class VistaReaccion_All(Resource):
    def get(self):
        reacciones = Reaccion.query.all()
        return [reaccionschema.dump(reaccion) for reaccion in reacciones], 200
    def post(self):
        data = request.get_json()
        nueva_reaccion = Reaccion(**data)
        db.session.add(nueva_reaccion)
        db.session.commit()
        return reaccionschema.dump(nueva_reaccion), 201


class VistaReaccion(Resource):
    def get(self, id=None):
        if id:
            reaccion = Reaccion.query.get(id)
            return reaccionschema.dump(reaccion) if reaccion else {'message': 'Reaccion no encontrada'}, 404
        else:
            reacciones = Reaccion.query.all()
            return [reaccionschema.dump(reaccion) for reaccion in reacciones], 200


    def put(self, id):
        reaccion = Reaccion.query.get_or_404(id)
        reaccion.ID_reaccion = request.json.get('ID_reaccion', reaccion.ID_reaccion)
        reaccion.Nombre_reaccion = request.json.get('Nombre_reaccion', reaccion.Nombre_reaccion)
        reaccion.Img_reaccion = request.json.get('Img_reaccion', reaccion.Img_reaccion)
        reaccion.Descripcion_reaccion = request.json.get('Descripcion_reaccion', reaccion.Descripcion_reaccion)
        reaccion.ID_reaccion = request.json.get('ID_reaccion', reaccion.ID_reaccion)  # Actualizamos 'categoria_id'
        db.session.commit()
        return reaccionschema.dump(id), 200

    def delete(self, id):
        reaccion = Reaccion.query.get_or_404(id)  # Si no existe, lanza un error 404 automáticamente
        
        db.session.delete(reaccion)
        db.session.commit()
        
        return {'message': 'Reacción eliminada correctamente', 'deleted_reaction': reaccionschema.dump(reaccion)}, 200
