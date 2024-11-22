from flask import request
from flask_restful import Resource
from ..modelos import db, Usuario, UsuarioSchema
from flask_jwt_extended import jwt_required, create_access_token


usuarioschema = UsuarioSchema()

class VistaUsuario_All(Resource):
    def get(self):
        usuarios = Usuario.query.all()
        return [UsuarioSchema.dump(usuario) for usuario in usuarios], 200

class VistaUsuario(Resource):
    
    def get(self, id=None):
        if id:
            usuario = Usuario.query.get(id)
            return UsuarioSchema.dump(usuario) if usuario else {'message': 'Usuario no encontrado'}, 404
        else:
            usuarios = Usuario.query.all()
            return [UsuarioSchema.dump(usuario) for usuario in usuarios], 200
    
    def post(self):
        data = request.get_json()
        nuevo_usuario = Usuario(**data)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return UsuarioSchema.dump(nuevo_usuario), 201

    def put(self, id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return {'message': 'Usuario no encontrado'}, 404
        
        data = request.get_json()
        for key, value in data.items():
            setattr(usuario, key, value)
        db.session.commit()
        return UsuarioSchema.dump(usuario), 200

    def delete(self, id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return {'message': 'Usuario no encontrado'}, 400

        db.session.delete(usuario)
        db.session.commit()
        return {'message': 'Usuario eliminado correctamente'}, 200

class VistaLogin(Resource):
    def post(self):
     u_correo = request.json["correo_usuario"]
     u_contrasena = request.json["Contrasena"]
     usuario = Usuario.query.filter_by(correo_usuario=u_correo).first()
     if usuario and usuario.verificar_contrasena(u_contrasena): 
        return {'mensaje':'Inicio de sesion exitoso'}, 200
     else:
        return {'mensaje':'Nombre de usuario o contraseña incorrectos'}, 401

class VistaSignin(Resource):
    def post(self):
        nuevo_usuario = Usuario(
            correo_usuario=request.json["correo_usuario"],
            Nombre_usuario=request.json.get("Nombre_usuario"),
            ID_sexo=request.json["ID_sexo"],
            ID_rol=request.json["ID_rol"]
        )
        
        nuevo_usuario.contrasena = request.json["Contrasena"]

        token_de_acceso = create_access_token(identity=request.json["correo_usuario"])

        db.session.add(nuevo_usuario)
        db.session.commit()
        return {'mensaje': 'Usuario creado exitosamente', 'token_de_acceso': token_de_acceso}, 201

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
