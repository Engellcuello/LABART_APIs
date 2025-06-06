from flask_restful import Resource
from flask import request
from ..modelos import db, Historial, HistoriaSchema


historial_schema = HistoriaSchema()

class VistaHistorial_All(Resource):
    def get(self):
        historiales = Historial.query.all()
        return [historial_schema.dump(historial) for historial in historiales], 200
    
    def post(self):
        data = request.get_json()
        nuevo_historial = Historial(**data)
        db.session.add(nuevo_historial)
        db.session.commit()
        return historial_schema.dump(nuevo_historial), 200

class VistaHistorial(Resource):
    def get(self, id):
        historial = Historial.query.get_or_404(id)
        return historial_schema.dump(historial), 200

    def put(self, id):
        historial = Historial.query.get_or_404(id)
        historial.Fecha_visto = request.json.get('Fecha_visto', historial.Fecha_visto)
        historial.ID_usuario = request.json.get('ID_usuario', historial.ID_usuario)
        historial.ID_publicacion = request.json.get('ID_publicacion', historial.ID_publicacion)
        db.session.commit()
        return historial_schema.dump(historial), 200

    def delete(self, id):
        historial = Historial.query.get(id)
        if not historial:
            return {'message': 'Registro de historial no encontrado'}, 404
        db.session.delete(historial)
        db.session.commit()
        return {'message': 'Registro de historial eliminado correctamente'}, 200
    

