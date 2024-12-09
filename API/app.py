from flask import Flask, jsonify, request
from API import create_app
from API.modelos.modelos import Asistente, Estado, Sexo, Reaccion, Usuario, PQRS, Tipo_PQRS, Rol, Comentario, Publicacion, Categoria, Notificaciones, PublicacionGuardada, Publicacion_Reaccion, Usuario_Reaccion, Publicacion_Categoria
from .modelos import db
from flask_restful import Api
from .vistas import VistaAsistente, VistaAsistente_All, VistaEstado, VistaEstado_All, VistaSexo, VistaSexo_All, VistaReaccion, VistaReaccion_All, VistaUsuario,VistaUsuario_All, VistaLogin, VistaSignin
from flask_jwt_extended import JWTManager
from flask_cors import CORS

app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()

# Configuración de CORS para permitir solicitudes desde localhost:5173
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

jwt = JWTManager(app)

api = Api(app)
api.add_resource(VistaAsistente_All, '/asistente')
api.add_resource(VistaAsistente, '/asistente/<int:id>')
api.add_resource(VistaEstado, '/estado/<int:id>')
api.add_resource(VistaEstado_All, '/estado')
api.add_resource(VistaSexo, '/sexo/<int:id>')
api.add_resource(VistaSexo_All, '/sexo')
api.add_resource(VistaReaccion, '/reaccion/<int:id>')
api.add_resource(VistaReaccion_All, '/reaccion')
api.add_resource(VistaUsuario_All, '/usuario')
api.add_resource(VistaUsuario, '/usuario/<int:id>')
api.add_resource(VistaSignin, '/signin')
api.add_resource(VistaLogin, '/login')

@app.before_request
def before_request():
    if request.method == "OPTIONS":
        response = jsonify({"message": "Preflight response"})
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"  
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        return response

@app.route("/")
def home():
    return jsonify({"mensaje": "API en funcionamiento"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



# with app.app_context():
#     # tabla Estado
#     estado1 = Estado(Nombre_estado='Activo', Descripcion_estado='Estado activo')
#     estado2 = Estado(Nombre_estado='Inactivo', Descripcion_estado='Estado inactivo')
#     estado3 = Estado(Nombre_estado='Pendiente', Descripcion_estado='Estado pendiente')
#     db.session.add_all([estado1, estado2, estado3])
#     db.session.commit()

#     # tabla Sexo
#     sexo1 = Sexo(Nombre_sexo='Masculino', Descripcion_sexo='Descripción Masculino')
#     sexo2 = Sexo(Nombre_sexo='Femenino', Descripcion_sexo='Descripción Femenino')
#     sexo3 = Sexo(Nombre_sexo='Otro', Descripcion_sexo='Descripción Otro')
#     db.session.add_all([sexo1, sexo2, sexo3])
#     db.session.commit()

#     # tabla Rol
#     rol1 = Rol(Nombre_rol='Admin', Descripcion_rol='Administrador')
#     rol2 = Rol(Nombre_rol='Usuario', Descripcion_rol='Usuario regular')
#     rol3 = Rol(Nombre_rol='Moderador', Descripcion_rol='Moderador de contenido')
#     db.session.add_all([rol1, rol2, rol3])
#     db.session.commit()

#     # tabla Usuario
#     usuario1 = Usuario(Nombre_usuario='usuario1', contrasena='pass1', correo_usuario='usuario1@mail.com', ID_sexo=1, ID_rol=1)
#     usuario2 = Usuario(Nombre_usuario='usuario2', contrasena='pass2', correo_usuario='usuario2@mail.com', ID_sexo=2, ID_rol=2)
#     usuario3 = Usuario(Nombre_usuario='usuario3', contrasena='pass3', correo_usuario='usuario3@mail.com', ID_sexo=3, ID_rol=3)
#     db.session.add_all([usuario1, usuario2, usuario3])
#     db.session.commit()

#     # Tipo_PQRS
#     tipo1 = Tipo_PQRS(Nombre_tipo='Tipo 1', Descripcion_tipo='Descripción del tipo 1')
#     tipo2 = Tipo_PQRS(Nombre_tipo='Tipo 2', Descripcion_tipo='Descripción del tipo 2')
#     tipo3 = Tipo_PQRS(Nombre_tipo='Tipo 3', Descripcion_tipo='Descripción del tipo 3')
#     db.session.add_all([tipo1, tipo2, tipo3])
#     db.session.commit()

#     # tabla PQRS
#     pqrs1 = PQRS(Fecha_pqrs='2024-11-28', Contenido_pqrs='Contenido 1', ID_estado=1, ID_usuario=1, ID_tipo_pqrs=1)
#     pqrs2 = PQRS(Fecha_pqrs='2024-11-28', Contenido_pqrs='Contenido 2', ID_estado=2, ID_usuario=2, ID_tipo_pqrs=2)
#     pqrs3 = PQRS(Fecha_pqrs='2024-11-28', Contenido_pqrs='Contenido 3', ID_estado=3, ID_usuario=3, ID_tipo_pqrs=3)
#     db.session.add_all([pqrs1, pqrs2, pqrs3])
#     db.session.commit()

#     # tabla Asistente
#     asistente1 = Asistente(Fecha_peticion='2024-11-28', Detalle_asistente='Detalle 1', ID_estado=1, ID_usuario=1)
#     asistente2 = Asistente(Fecha_peticion='2024-11-28', Detalle_asistente='Detalle 2', ID_estado=2, ID_usuario=2)
#     asistente3 = Asistente(Fecha_peticion='2024-11-28', Detalle_asistente='Detalle 3', ID_estado=3, ID_usuario=3)
#     db.session.add_all([asistente1, asistente2, asistente3])
#     db.session.commit()

#     # tabla Reaccion
#     reaccion1 = Reaccion(Nombre_reaccion='Like', Img_reaccion='like.png', Descripcion_reaccion='Me gusta')
#     reaccion2 = Reaccion(Nombre_reaccion='Love', Img_reaccion='love.png', Descripcion_reaccion='Me encanta')
#     reaccion3 = Reaccion(Nombre_reaccion='Wow', Img_reaccion='wow.png', Descripcion_reaccion='Me sorprende')
#     db.session.add_all([reaccion1, reaccion2, reaccion3])
#     db.session.commit()


#     # tabla Publicacion
#     publicacion1 = Publicacion(Descripcion_publicacion='Descripción 1', ID_usuario=1)
#     publicacion2 = Publicacion(Descripcion_publicacion='Descripción 2', ID_usuario=2)
#     publicacion3 = Publicacion(Descripcion_publicacion='Descripción 3', ID_usuario=3)
#     db.session.add_all([publicacion1, publicacion2, publicacion3])
#     db.session.commit()

#     # tabla Comentario
#     comentario1 = Comentario(Contenido_comentario='Comentario 1', ID_usuario=1, ID_publicacion=1)
#     comentario2 = Comentario(Contenido_comentario='Comentario 2', ID_usuario=2, ID_publicacion=2)
#     comentario3 = Comentario(Contenido_comentario='Comentario 3', ID_usuario=3, ID_publicacion=3)
#     db.session.add_all([comentario1, comentario2, comentario3])
#     db.session.commit()

#     # tabla Categoria
#     categoria1 = Categoria(Nombre_categoria='Categoria 1', Descripcion_categoria='Descripción 1')
#     categoria2 = Categoria(Nombre_categoria='Categoria 2', Descripcion_categoria='Descripción 2')
#     categoria3 = Categoria(Nombre_categoria='Categoria 3', Descripcion_categoria='Descripción 3')
#     db.session.add_all([categoria1, categoria2, categoria3])
#     db.session.commit()

#     # tabla Notificaciones
#     notificacion1 = Notificaciones(Mensaje='Notificación 1', Fecha_notificacion='2024-11-28', ID_usuario=1)
#     notificacion2 = Notificaciones(Mensaje='Notificación 2', Fecha_notificacion='2024-11-28', ID_usuario=2)
#     notificacion3 = Notificaciones(Mensaje='Notificación 3', Fecha_notificacion='2024-11-28', ID_usuario=3)
#     db.session.add_all([notificacion1, notificacion2, notificacion3])
#     db.session.commit()

#     # tabla PublicacionGuardada
#     pub_guardada1 = PublicacionGuardada(Fecha_guardado='2024-11-28', ID_usuario=1, ID_publicacion=1)
#     pub_guardada2 = PublicacionGuardada(Fecha_guardado='2024-11-28', ID_usuario=2, ID_publicacion=2)
#     pub_guardada3 = PublicacionGuardada(Fecha_guardado='2024-11-28', ID_usuario=3, ID_publicacion=3)
#     db.session.add_all([pub_guardada1, pub_guardada2, pub_guardada3])
#     db.session.commit()

#     # tabla Publicacion_Reaccion
#     pub_reaccion1 = Publicacion_Reaccion(ID_publicacion=1, ID_reaccion=1)
#     pub_reaccion2 = Publicacion_Reaccion(ID_publicacion=2, ID_reaccion=2)
#     pub_reaccion3 = Publicacion_Reaccion(ID_publicacion=3, ID_reaccion=3)
#     db.session.add_all([pub_reaccion1, pub_reaccion2, pub_reaccion3])
#     db.session.commit()

#     # tabla Usuario_Reaccion
#     usuario_reaccion1 = Usuario_Reaccion(ID_usuario=1, ID_reaccion=1)
#     usuario_reaccion2 = Usuario_Reaccion(ID_usuario=2, ID_reaccion=2)
#     usuario_reaccion3 = Usuario_Reaccion(ID_usuario=3, ID_reaccion=3)
#     db.session.add_all([usuario_reaccion1, usuario_reaccion2, usuario_reaccion3])
#     db.session.commit()

#     # tabla Publicacion_Categoria
#     pub_categoria1 = Publicacion_Categoria(ID_publicacion=1, ID_categoria=1)
#     pub_categoria2 = Publicacion_Categoria(ID_publicacion=2, ID_categoria=2)
#     pub_categoria3 = Publicacion_Categoria(ID_publicacion=3, ID_categoria=3)
#     db.session.add_all([pub_categoria1, pub_categoria2, pub_categoria3])
#     db.session.commit()
