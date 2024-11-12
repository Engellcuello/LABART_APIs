from flask_restful import Resource
from flask import request
from ..modelos import db, Usuario, UsuarioSchema

usuario_schema = UsuarioSchema()


class VistaUsuarios(Resource):
    def get(self):
        usuarios = Usuario.query.all()
        return usuario_schema.dump(usuarios), 200


class VistaUsuario(Resource):
    def get(self, id):
        usuario = Usuario.query.get(id)
        if usuario:
            return usuario_schema.dump(usuario), 200
        return {'message': 'Usuario no encontrado'}, 404
    
    def post(self):
        data = request.get_json()
        nuevo_usuario = Usuario(
            id_usuario=data['id_usuario'],
            nombre_usuario=data['nombre_usuario'],
            contrasena=data['contrasena'],
            correo_usuario=data['correo_usuario'],
            fecha_usuario=data['contrasena'],
            notificaciones=data['contrasena'],
            img_usuario=data['contrasena'],
            cont_explicit=data['contrasena'],
            id_sexo=data['contrasena'],
            id_rol=data['contrasena'],
            id_reaccion=data['contrasena'],
            
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuario_schema.dump(nuevo_usuario), 201

    def put(self, id):
        usuario = Usuario.query.get(id)
        if usuario:
            data = request.get_json()
            usuario.id_usuario = data.get('id_usuario', usuario.id_usuario)
            usuario.nombre_usuario = data.get('nombre_usuario', usuario.nombre_usuario)
            usuario.contrasena = data.get('contrasena', usuario.contrasena)
            usuario.correo_usuario = data.get('correo_usuario', usuario.correo_usuario)
            usuario.fecha_usuario = data.get('fecha_usuario', usuario.fecha_usuario)
            usuario.notificaciones = data.get('notificaciones', usuario.notificaciones)
            usuario.img_usuario = data.get('img_usuario', usuario.img_usuario)
            usuario.cont_explicit = data.get('cont_explicit', usuario.cont_explicit)
            usuario.id_sexo = data.get('id_sexo', usuario.id_sexo)
            usuario.id_rol = data.get('id_rol', usuario.id_rol)
            usuario.id_reaccion = data.get('id_reaccion', usuario.id_reaccion)

            db.session.commit()
            return usuario_schema.dump(usuario), 200
        return {'message': 'Usuario no encontrado'}, 404


    def delete(self, id):
        usuario = Usuario.query.get(id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            return {'message': 'Usuario eliminado correctamente'}, 200
        return {'message': 'Usuario no encontrado'}, 404
