from flask_restful import Resource
from flask import jsonify, request
from flask import Response
import json
from API.modelos.modelos import Publicacion
from ..modelos import db, Publicacion_Guardada, PublicacionGuardadaSchema

publicacion_guardadaschema = PublicacionGuardadaSchema()

class VistaPublicacionGuardada_All(Resource):
    def get(self):
        publicacion_guardadas = Publicacion_Guardada.query.all()
        return [publicacion_guardadaschema.dump(publicacion_guardada) for publicacion_guardada in publicacion_guardadas], 200
    
    def post(self):
        data = request.get_json()
        nueva_publicacion_guardada = Publicacion_Guardada(**data)
        db.session.add(nueva_publicacion_guardada)
        db.session.commit()
        return publicacion_guardadaschema.dump(nueva_publicacion_guardada), 200

class VistaPublicacionGuardada(Resource):
    def get(self, id=None):
        if id:
            publicacion_guardada = Publicacion_Guardada.query.get(id)
            return publicacion_guardadaschema.dump(publicacion_guardada) if publicacion_guardada else {'message': 'Publicacion Guardada no encontrada'}, 404
        else:
            publicacion_guardadas = Publicacion_Guardada.query.all()
            return [publicacion_guardadaschema.dump(publicacion_guardada) for publicacion_guardada in publicacion_guardadas], 200

    def put(self, id):
        publicacion_guardada = Publicacion_Guardada.query.get_or_404(id)

        publicacion_guardada.ID_publicacion_guardada = request.json.get('ID_publicacion_guardada', publicacion_guardada.ID_publicacion_guardada)
        publicacion_guardada.Fecha_guardado = request.json.get('Fecha_guardado', publicacion_guardada.Fecha_guardado)
        publicacion_guardada.ID_usuario = request.json.get('ID_usuario', publicacion_guardada.ID_usuario)
        publicacion_guardada.ID_publicacion = request.json.get('ID_publicacion', publicacion_guardada.ID_publicacion)

        db.session.commit()
        return publicacion_guardadaschema.dump(publicacion_guardada), 200

    def delete(self, id):
        publicacion_guardada = Publicacion_Guardada.query.get(id)
        if not publicacion_guardada:
            return {'message': 'Publicacion Guardada no encontrada'}, 400

        db.session.delete(publicacion_guardada)
        db.session.commit()
        return {'message': 'Publicacion Guardada eliminada correctamente'}, 200


class VistaPublicacionesGuardadasUsuario(Resource):
    def get(self, id_usuario):
        # Publicaciones creadas por el usuario
        publicaciones_creadas = (
            Publicacion.query
            .filter_by(ID_usuario=id_usuario)
            .order_by(Publicacion.Fecha_Publicacion.desc())
            .all()
        )

        # Publicaciones guardadas por el usuario
        publicaciones_guardadas = (
            db.session.query(Publicacion)
            .join(Publicacion_Guardada, Publicacion.ID_publicacion == Publicacion_Guardada.ID_publicacion)
            .filter(Publicacion_Guardada.ID_usuario == id_usuario)
            .order_by(Publicacion.Fecha_Publicacion.desc())
            .all()
        )

        # Función para formatear las publicaciones en el orden exacto
        def formatear_publicacion(pub):
            return {
                "ID_publicacion": pub.ID_publicacion,
                "Titulo_publicacion": pub.Titulo_publicacion,
                "Fecha_Publicacion": pub.Fecha_Publicacion.isoformat(),
                "Descripcion_publicacion": pub.Descripcion_publicacion,
                "Img_publicacion": pub.Img_publicacion,
                "Cont_Explicit_publi": pub.Cont_Explicit_publi,
                "ID_usuario": pub.ID_usuario
            }

        # Aplicar formato a las publicaciones
        publicaciones_creadas_data = [formatear_publicacion(pub) for pub in publicaciones_creadas]
        publicaciones_guardadas_data = [formatear_publicacion(pub) for pub in publicaciones_guardadas]

        # Crear el diccionario de respuesta
        respuesta = {
            "publicaciones_creadas": publicaciones_creadas_data,
            "publicaciones_guardadas": publicaciones_guardadas_data
        }

        # Convertir a JSON manteniendo el orden de las claves y sin escapado de Unicode
        json_str = json.dumps(respuesta, ensure_ascii=False, indent=2)

        # Crear una respuesta Flask con el tipo de contenido correcto
        return Response(
            response=json_str,
            status=200,
            mimetype='application/json'
        )