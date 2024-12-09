from flask import request
from flask_restful import Resource
from ..modelos import db, Usuario, UsuarioSchema
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

usuarioschema = UsuarioSchema()

class VistaUsuario_All(Resource):
    def get(self):
        usuarios = Usuario.query.all()
        return [usuarioschema.dump(usuario) for usuario in usuarios], 200

class VistaUsuario(Resource):
    def get(self, id=None):
        if id:
            usuario = Usuario.query.get(id)
            return usuarioschema.dump(usuario) if usuario else {'message': 'Usuario no encontrado'}, 404
        else:
            usuarios = Usuario.query.all()
            return [usuarioschema.dump(usuario) for usuario in usuarios], 200

    def post(self):
        data = request.get_json()
        nuevo_usuario = Usuario(**data)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuarioschema.dump(nuevo_usuario), 201

    def put(self, id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return {'message': 'Usuario no encontrado'}, 404

        data = request.get_json()
        for key, value in data.items():
            setattr(usuario, key, value)
        db.session.commit()
        return usuarioschema.dump(usuario), 200

    def delete(self, id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return {'message': 'Usuario no encontrado'}, 400

        db.session.delete(usuario)
        db.session.commit()
        return {'message': 'Usuario eliminado correctamente'}, 200


class VistaLogin(Resource):
    def post(self):
        correo = request.json.get("correo_usuario")
        contrasena = request.json.get("Contrasena")

        usuario = Usuario.query.filter_by(correo_usuario=correo).first()

        if usuario:
            
            if usuario.verificar_contrasena(contrasena):
                token_de_acceso = create_access_token(identity=correo)
                return {
                    'mensaje': 'Inicio de sesión exitoso',
                    'token_de_acceso': token_de_acceso
                }, 200
            else:
                return {'mensaje': 'Contraseña incorrecta'}, 401
        else:
            return {'mensaje': 'Correo no registrado'}, 404


        
        
class VistaSignin(Resource):
    def post(self):
        nuevo_usuario = Usuario(
            correo_usuario=request.json["correo_usuario"],
            Nombre_usuario=request.json.get("Nombre_usuario"),
            ID_sexo=request.json["ID_sexo"],
            ID_rol=request.json["ID_rol"]
        )
        
        nuevo_usuario.contrasena = request.json["Contrasena"]

        db.session.add(nuevo_usuario)
        db.session.commit()
        return {'mensaje': 'Usuario creado exitosamente'}, 201

    def put(self, ID_usuario):
        usuario = Usuario.query.get_or_404(ID_usuario)
        if "Contrasena" in request.json:
            usuario.Contrasena = request.json["Contrasena"]
        db.session.commit()
        return UsuarioSchema.dump(usuario), 200

    def delete(self, ID_usuario):
        usuario = Usuario.query.get_or_404(ID_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204

