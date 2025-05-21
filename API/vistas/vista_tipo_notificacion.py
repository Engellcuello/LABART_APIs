from flask_restful import Resource
from flask import request
from ..modelos import db, TipoNotificacion, TipoNotificacionSchema

tipo_notificacion_schema = TipoNotificacionSchema()

class VistaTipoNotificacion_All(Resource):
    def get(self):
        tipos_notificacion = TipoNotificacion.query.all()
        return [tipo_notificacion_schema.dump(tipo) for tipo in tipos_notificacion], 200

    def post(self):
        data = request.get_json()
        nuevo_tipo = TipoNotificacion(
            Nombre=data['Nombre'],
            Mensaje_base=data.get('Mensaje_base', '')
        )
        db.session.add(nuevo_tipo)
        db.session.commit()
        return tipo_notificacion_schema.dump(nuevo_tipo), 201


class VistaTipoNotificacion(Resource):
    def get(self, id=None):
        if id:
            tipo = TipoNotificacion.query.get(id)
            if tipo:
                return tipo_notificacion_schema.dump(tipo), 200
            else:
                return {'message': 'Tipo de notificación no encontrado'}, 404
        else:
            tipos = TipoNotificacion.query.all()
            return [tipo_notificacion_schema.dump(tipo) for tipo in tipos], 200

    def put(self, id):
        tipo = TipoNotificacion.query.get_or_404(id)

        tipo.Nombre = request.json.get('Nombre', tipo.Nombre)
        tipo.Mensaje_base = request.json.get('Mensaje_base', tipo.Mensaje_base)

        db.session.commit()
        return tipo_notificacion_schema.dump(tipo), 200


    def delete(self, id):
        tipo = TipoNotificacion.query.get_or_404(id)

        if tipo.notificaciones:
            return {'message': 'No se puede eliminar, hay notificaciones asociadas a este tipo'}, 400

        db.session.delete(tipo)
        db.session.commit()
        return {
            'message': 'Tipo de notificación eliminado correctamente',
            'deleted_type': tipo_notificacion_schema.dump(tipo)
        }, 200
