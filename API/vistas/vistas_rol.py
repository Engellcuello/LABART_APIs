from flask_restful import Resource
from flask import request
from ..modelos import db, Rol, RolSchema

rol_schema = RolSchema()
roles_schema = RolSchema(many=True)

class VistaRoles(Resource):
    def get(self):
        roles = Rol.query.all()
        return roles_schema.dump(roles), 200

class VistaRol(Resource):
    def get(self, id):
        rol = Rol.query.get(id)
        if rol:
            return rol_schema.dump(rol), 200
        return {'message': 'Rol no encontrado'}, 404
    
    def post(self):
        data = request.get_json()
        nuevo_rol = Rol(
            id_rol=data['id_rol'],
            nombre_rol=data['nombre_rol'],
            descripcion_rol=data['descripcion_rol'],
            id_estado=data['id_estado']
        )
        db.session.add(nuevo_rol)
        db.session.commit()
        return rol_schema.dump(nuevo_rol), 201

    def put(self, id):
        rol = Rol.query.get(id)
        if rol:
            data = request.get_json()
            rol.id_rol = data.get('id_rol', rol.id_rol)
            rol.nombre_rol = data.get('nombre_rol', rol.nombre_rol)
            rol.descripcion_rol = data.get('descripcion_rol', rol.descripcion_rol)
            rol.id_estado = data.get('id_estado', rol.id_estado)

            db.session.commit()
            return rol_schema.dump(rol), 200
        return {'message': 'Rol no encontrado'}, 404

    def delete(self, id):
        rol = Rol.query.get(id)
        if rol:
            db.session.delete(rol)
            db.session.commit()
            return {'message': 'Rol eliminado correctamente'}, 200
        return {'message': 'Rol no encontrado'}, 404

