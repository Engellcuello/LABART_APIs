from flask_restful import Resource
from flask import request
from ..modelos import db, Usuario_Reaccion, Usuario_ReaccionSchema

usuario_reaccion_schema = Usuario_ReaccionSchema()

class VistaUsuarioReaccion_All(Resource):
    def get(self):
        usuario_reacciones = Usuario_Reaccion.query.all()
        return [usuario_reaccion_schema.dump(usuario_reaccion) for usuario_reaccion in usuario_reacciones], 200
    
    def post(self):
        data = request.get_json()
        nueva_usuario_reaccion = Usuario_Reaccion(**data)
        db.session.add(nueva_usuario_reaccion)
        db.session.commit()
        return usuario_reaccion_schema.dump(nueva_usuario_reaccion), 200

class VistaUsuarioReaccion(Resource):
    def get(self, id):
        usuario_reaccion = Usuario_Reaccion.query.get(id)
        return usuario_reaccion_schema.dump(usuario_reaccion) if usuario_reaccion else {'message': 'Usuario Reaccion no encontrada'}, 404
    
    def put(self, id):
        usuario_reaccion = Usuario_Reaccion.query.get_or_404(id)
        
        usuario_reaccion.ID_usuario = request.json.get('ID_usuario', usuario_reaccion.ID_usuario)
        usuario_reaccion.ID_reaccion = request.json.get('ID_reaccion', usuario_reaccion.ID_reaccion)
        
        db.session.commit()
        return usuario_reaccion_schema.dump(usuario_reaccion), 200
    
    def delete(self, id):
        usuario_reaccion = Usuario_Reaccion.query.get(id)
        if not usuario_reaccion:
            return {'message': 'Usuario Reaccion no encontrada'}, 404
        
        db.session.delete(usuario_reaccion)
        db.session.commit()
        return {'message': 'Usuario Reaccion eliminada correctamente'}, 200
