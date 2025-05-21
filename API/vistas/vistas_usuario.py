from flask import request,jsonify
from flask_restful import Resource
from sqlalchemy import func

from API.modelos.modelos import Comentario, Historial, Publicacion, Publicacion_Reaccion
from API.vistas.resourses.cloudinary_uploader import upload_image_to_cloudinary
from ..modelos import db, Usuario, UsuarioSchema
from flask_jwt_extended import create_access_token

usuarioschema = UsuarioSchema()

class VistaUsuario_All(Resource):
    def get(self):
        usuarios = Usuario.query.all()
        return [usuarioschema.dump(usuario) for usuario in usuarios], 200
    
    def post(self):
        data = request.get_json()
        if "contrasena_hash" in data:
            nueva_contrasena = data.pop("contrasena_hash")
            nuevo_usuario = Usuario(**data)
            nuevo_usuario.contrasena = nueva_contrasena  # Usar el setter
        else:
            return {"mensaje": "La contraseña es requerida"}, 400
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuarioschema.dump(nuevo_usuario), 201

class VistaUsuario(Resource):
    def get(self, id):
        usuario = Usuario.query.get_or_404(id)
        return usuarioschema.dump(usuario), 200

    def put(self, id):
        try:
            usuario = Usuario.query.get_or_404(id)

            # Verificamos si es multipart (formulario con archivos)
            if request.content_type and request.content_type.startswith('multipart/form-data'):
                # Obtener imagen y subirla
                imagen = request.files.get('Img_usuario')
                img_url = upload_image_to_cloudinary(imagen) if imagen else None

                # Obtener otros datos del formulario
                data = request.form.to_dict()
                if img_url:
                    data['Img_usuario'] = img_url

            else:
                # Si es JSON
                data = request.get_json(force=True)

            # Verificar si se enviaron datos
            if not data:
                return {"mensaje": "No se proporcionaron datos para actualizar"}, 400

            # Asignar datos al usuario
            for key, value in data.items():
                setattr(usuario, key, value)

            db.session.commit()
            return usuarioschema.dump(usuario), 200

        except Exception as e:
            print("Error al actualizar el usuario:", e)
            db.session.rollback()
            return {"mensaje": "Ocurrió un error al actualizar el usuario"}, 500
        


    def delete(self, id):
        usuario = Usuario.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        return {'message': 'Usuario eliminado correctamente'}, 200

class VistaLogin(Resource):
    def post(self):
        data = request.get_json()
        correo = data.get("correo_usuario")
        contrasena = data.get("Contrasena")

        usuario = Usuario.query.filter_by(correo_usuario=correo).first()
        if usuario and usuario.verificar_contrasena(contrasena):
            token_de_acceso = create_access_token(identity=correo)
            return {
                'mensaje': 'Inicio de sesión exitoso',
                'token_de_acceso': token_de_acceso,
                'ID_usuario': usuario.ID_usuario,  
                'Nombre_usuario': usuario.Nombre_usuario,  
                'Cont_Explicit': usuario.Cont_Explicit,
                'ID_rol': usuario.ID_rol 
            }, 200
        return {'mensaje': 'Credenciales incorrectas'}, 401
    
    

class VistaSignin(Resource):
    def post(self):
        data = request.get_json()
        nuevo_usuario = Usuario(**data)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return {'mensaje': 'Usuario creado exitosamente'}, 201

    def put(self, id):
        usuario = Usuario.query.get_or_404(id)
        data = request.get_json()
        for key, value in data.items():
            setattr(usuario, key, value)
        db.session.commit()
        return usuarioschema.dump(usuario), 200

    def delete(self, id):
        usuario = Usuario.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        return {'message': 'Usuario eliminado correctamente'}, 200
    

class VistaCheckEmail(Resource):
    def get(self):
        email = request.args.get('email')
        if not email:
            return {'error': 'Email parameter is required'}, 400
        
        usuario = Usuario.query.filter_by(correo_usuario=email).first()
        return {'exists': usuario is not None}, 200



class VistaUsuariosTop(Resource):
    def get(self):
        # Subconsultas individuales para cada métrica
        subq_publicaciones = db.session.query(
            Publicacion.ID_usuario,
            func.count(Publicacion.ID_publicacion).label("total_publicaciones")
        ).group_by(Publicacion.ID_usuario).subquery()

        subq_comentarios = db.session.query(
            Comentario.ID_usuario,
            func.count(Comentario.ID_comentario).label("total_comentarios")
        ).group_by(Comentario.ID_usuario).subquery()

        subq_reacciones = db.session.query(
            Publicacion_Reaccion.ID_usuario,
            func.count(Publicacion_Reaccion.ID_publicacion_reaccion).label("total_reacciones")
        ).group_by(Publicacion_Reaccion.ID_usuario).subquery()

        # Subconsulta para vistas: contar las vistas por publicación relacionada con el usuario
        subq_vistas = db.session.query(
            Publicacion.ID_usuario,
            func.count(Historial.ID_historial).label("total_vistas")
        ).join(Historial, Historial.ID_publicacion == Publicacion.ID_publicacion) \
         .group_by(Publicacion.ID_usuario).subquery()

        # Consulta principal
        usuarios = db.session.query(
            Usuario,
            func.coalesce(subq_publicaciones.c.total_publicaciones, 0),
            func.coalesce(subq_comentarios.c.total_comentarios, 0),
            func.coalesce(subq_reacciones.c.total_reacciones, 0),
            func.coalesce(subq_vistas.c.total_vistas, 0)
        ).outerjoin(subq_publicaciones, subq_publicaciones.c.ID_usuario == Usuario.ID_usuario) \
         .outerjoin(subq_comentarios, subq_comentarios.c.ID_usuario == Usuario.ID_usuario) \
         .outerjoin(subq_reacciones, subq_reacciones.c.ID_usuario == Usuario.ID_usuario) \
         .outerjoin(subq_vistas, subq_vistas.c.ID_usuario == Usuario.ID_usuario) \
         .order_by(
             subq_publicaciones.c.total_publicaciones.desc(),
             subq_reacciones.c.total_reacciones.desc(),
             subq_comentarios.c.total_comentarios.desc()
         ).all()

        # Formateo
        usuarios_formateados = []
        for usuario, publicaciones, comentarios, reacciones, vistas in usuarios:
            usuario_data = usuarioschema.dump(usuario)
            usuario_data['total_publicaciones'] = publicaciones
            usuario_data['total_comentarios'] = comentarios
            usuario_data['total_reacciones'] = reacciones
            usuario_data['total_vistas'] = vistas

            
            
            usuarios_formateados.append(usuario_data)

        return {
            'usuarios': usuarios_formateados,
            'mensaje': 'Usuarios ordenados por actividad'
        }, 200



class Vista_Buscador_usuarios(Resource):
    def get(self):
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify([])
        
        usuarios = Usuario.query.filter(
            Usuario.Nombre_usuario.ilike(f'%{query}%')
        ).limit(10).all()
        
        resultados = [{
            'ID_usuario': u.ID_usuario,
            'Nombre_usuario': u.Nombre_usuario,
            'Img_usuario': u.Img_usuario
        } for u in usuarios]
        
        return jsonify(resultados)
    
    
class VistaCheckUsername(Resource):
    def get(self, nombre_usuario):
        usuario = Usuario.query.filter_by(Nombre_usuario=nombre_usuario).first()
        if usuario:
            return {'exists': True}, 200
        else:
            return {'exists': False}, 200


