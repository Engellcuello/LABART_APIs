from flask_restful import Resource
from flask import request  # Solo importa request desde flask
from ..modelos import db, Rol, RolSchema

rolschema = RolSchema()

class VistaRol_All(Resource):
    def get(self):
        roles = Rol.query.all()
        return [rolschema.dump(rol) for rol in roles], 200
    
    def post(self):
        data = request.get_json()
        nuevo_rol = Rol(**data)
        db.session.add(nuevo_rol)
        db.session.commit()
        return rolschema.dump(nuevo_rol), 201

class VistaRol(Resource):
    def get(self, id=None):
        if id:
            rol = Rol.query.get(id)
            return rolschema.dump(rol) if rol else {'message': 'Rol no encontrado'}, 404
        else:
            roles = Rol.query.all()
            return [rolschema.dump(rol) for rol in roles], 200

    def put(self, id):
        rol = Rol.query.get_or_404(id)
        rol.Nombre_rol = request.json.get('Nombre_rol', rol.Nombre_rol)
        rol.Descripcion_rol = request.json.get('Descripcion_rol', rol.Descripcion_rol)
        db.session.commit()
        return rolschema.dump(rol), 200

    def delete(self, id):
        rol = Rol.query.get_or_404(id)  # Esto lanza 404 si no existe
        db.session.delete(rol)
        db.session.commit()
        return {'message': 'Rol eliminado correctamente', 'deleted_rol': rolschema.dump(rol)}, 200
