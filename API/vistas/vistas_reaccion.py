from flask_restful import Resource

from requests import request

from ..modelos import db, Reaccion, ReaccionSchema

reaccionschema = ReaccionSchema()

class VistaReaccion_All(Resource):
    def get(self):
        reacciones = Reaccion.query.all()
        return [reaccionschema.dump(reaccion) for reaccion in reacciones], 200


class VistaReaccion(Resource):
    def get(self, id=None):
        if id:
            reaccion = Reaccion.query.get(id)
            return reaccionschema.dump(reaccion) if reaccion else {'message': 'Reaccion no encontrada'}, 404
        else:
            reacciones = Reaccion.query.all()
            return [reaccionschema.dump(reaccion) for reaccion in reacciones], 200
    
    def post(self):
        data = request.get_json()
        nueva_reaccion = Reaccion(**data)
        db.session.add(nueva_reaccion)
        db.session.commit()
        return reaccionschema.dump(nueva_reaccion), 201

    def put(self, id):
        reaccion = Reaccion.query.get(id)
        if not reaccion:
            return {'message': 'Asistente no encontrado'}, 404

        data = request.get_json()
        for key, value in data.items():
            setattr(reaccion, key, value)
        db.session.commit()
        return reaccionschema.dump(reaccion), 200

    def delete(self, id):
        reaccion = Reaccion.query.get(id)
        if not reaccion:
            return {'message': 'Asistente no encontrado'}, 400

        db.session.delete(reaccion)
        db.session.commit()
        return {'message': 'Asistente eliminado correctamente'}, 200