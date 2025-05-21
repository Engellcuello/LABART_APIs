from flask import Flask, jsonify, request
from API import create_app
from API.modelos.modelos import db
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from sqlalchemy import text

from API.vistas.resourses.codeOTP import EmailSender, PasswordResetComplete, PasswordResetCompleteNoOTP, PasswordResetInit, PasswordResetVerify, VerifyCurrentPassword
from API.vistas.resourses.google_vision import AnalizarImagen
from API.vistas.vista_categorias import VistaRecomendacionesHome
from API.vistas.vista_etiqueta_publicacion import VistaEtiquetaPublicacion_All,VistaEtiquetaPublicacion,VistaDescripcionesUnicas, EtiquetasPublicacionResource,EtiquetasDisponiblesResource,AsignarEtiquetaPublicacionResource
from API.vistas.vista_historial import VistaHistorial,VistaHistorial_All
from API.vistas.vista_notificaciones import VistaEliminarNotificacionesPorTipoYUsuario, VistaMarcarNotificacionesLeidas, VistaNotificacionesNoLeidas, VistaNotificacionesUsuario,VistaMarcarNotificacionesComoLeidas
from API.vistas.vista_publicacion_categoria import VistaPublicacionesPorCategoria
from API.vistas.vista_publicacion_guardada import VistaPublicacionesGuardadasUsuario
from API.vistas.vista_publicaciones import VistaEstadisticasUsuario, VistaRecomendaciones, VistaRecomendacionesPublicacion,Vista_Busqueda_publicaciones
from API.vistas.vista_tipo_notificacion import VistaTipoNotificacion, VistaTipoNotificacion_All
from API.vistas.vistas_usuario import VistaUsuariosTop, Vista_Buscador_usuarios,VistaCheckEmail,VistaCheckUsername
from API.vistas.vista_color_publicacion import VistaColorPublicacion, VistaColorPublicacion_All
from .modelos import *
from .vistas import VistaAsistente, VistaAsistente_All, VistaEstado, VistaEstado_All, VistaSexo, VistaSexo_All, VistaReaccion, VistaReaccion_All, VistaUsuario,VistaUsuario_All, VistaLogin, VistaSignin, VistaPublicaciones_All, VistaPublicaciones,VistaRol,VistaRol_All,VistaCategoria,VistaCategoria_All,VistaComentario,VistaComentario_All,VistaNotificacion,VistaNotificacion_All,VistaPublicacionGuardada,VistaPublicacionGuardada_All,Vistatipo_pqrs,Vistatipo_pqrs_All,VistaPQRS,VistaPQRS_All,VistaPublicacionCategoria,VistaPublicacionCategoria_All,VistaPublicacionReaccion,VistaPublicacionReaccion_All,VistaUsuarioReaccion,VistaUsuarioReaccion_All,VistaCategoriasDePublicacion



app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()

@app.before_request
def override_method():
    if request.method == 'POST' and request.args.get('_method') == 'PUT':
        print("🔁 Método override a PUT")
        request.environ['REQUEST_METHOD'] = 'PUT'

CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

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
api.add_resource(VistaRol_All, '/rol')
api.add_resource(VistaRol, '/rol/<int:id>')
api.add_resource(VistaUsuario, '/usuario/<int:id>')
api.add_resource(VistaPublicaciones_All, '/publicacion')
api.add_resource(VistaPublicaciones, '/publicacion/<int:id>')
api.add_resource(VistaSignin, '/signin')
api.add_resource(VistaLogin, '/login')  
api.add_resource(VistaCategoria_All, '/categoria')
api.add_resource(VistaCategoria, '/categoria/<int:id>')
api.add_resource(VistaComentario_All, '/comentario')
api.add_resource(VistaComentario, '/comentario/<int:id>')
api.add_resource(VistaNotificacion_All, '/notificaciones')
api.add_resource(VistaNotificacion, '/notificaciones/<int:id>')
api.add_resource(VistaTipoNotificacion_All, '/tiponotificacion')
api.add_resource(VistaTipoNotificacion, '/tiponotificacion/<int:id>')
api.add_resource(VistaPublicacionGuardada_All, '/publicacion_guardada')
api.add_resource(VistaPublicacionGuardada, '/publicacion_guardada/<int:id>')
api.add_resource(Vistatipo_pqrs_All, '/tipo_pqrs')
api.add_resource(Vistatipo_pqrs, '/tipo_pqrs/<int:id>')
api.add_resource(VistaPQRS_All, '/pqrs')
api.add_resource(VistaPQRS, '/pqrs/<int:id>')
api.add_resource(VistaPublicacionCategoria_All, '/publicacion_categoria')
api.add_resource(VistaPublicacionCategoria, '/publicacion_categoria/<int:id>')
api.add_resource(VistaPublicacionReaccion_All, '/publicacion_reaccion')
api.add_resource(VistaPublicacionReaccion, '/publicacion_reaccion/<int:id>')
api.add_resource(VistaUsuarioReaccion_All, '/usuario_reaccion')
api.add_resource(VistaUsuarioReaccion, '/usuario_reaccion/<int:id>')
api.add_resource(VistaEtiquetaPublicacion_All, '/etiqueta_publicacion')
api.add_resource(VistaEtiquetaPublicacion, '/etiqueta_publicacion/<int:id>')
api.add_resource(VistaColorPublicacion_All, '/color_publicacion')
api.add_resource(VistaColorPublicacion, '/color_publicacion/<int:id>')
api.add_resource(Vista_Buscador_usuarios, ('/buscar_usuarios'))

#endpoint para enviar el mensaje de otp
api.add_resource(EmailSender, '/email')

#endpoint para verificar que la cuenta esta registrada ya
api.add_resource(VistaCheckEmail, '/usuario/check-email')

#endpoint para analizar la imagen y sacar los colores y etiquetas
api.add_resource(AnalizarImagen, '/analizar_imagen')

#endpoint para obtener las recomendaciones de la publicacion
api.add_resource(VistaRecomendacionesPublicacion, '/recomendaciones/publicacion/<int:id_publicacion>')

#endpoint para registrar el historial
api.add_resource(VistaHistorial_All, '/historial')
api.add_resource(VistaHistorial, '/historial/<int:id>')

#endpoint para traer todas las etiquetas
api.add_resource(VistaDescripcionesUnicas, '/etiquetas')

#enpoint para obtener las recomendaciones del usuario
api.add_resource(VistaRecomendaciones, '/recomendacioneshome/<int:user_id>')


#endpoint para obtener todas las publicaciones de una categoria
api.add_resource(VistaPublicacionesPorCategoria, '/publicacion_categoria/categoria/<int:id_categoria>')

#endpoint para obtener las estadisticas de las publicaciones y reacciones de un usuario
api.add_resource(VistaEstadisticasUsuario, '/estadisticas_usuario/<int:id_usuario>')

#endpoint para obtener las publicaciones propias y guardadas de un usuario
api.add_resource(VistaPublicacionesGuardadasUsuario, '/publicaciones_guardadas/<int:id_usuario>')

#endpoint para obtener las notificaciones propias de un usuario
api.add_resource(VistaNotificacionesUsuario, '/notificaciones_usuario/<int:id_usuario>')

#endpoint para eliminar notificaciones por tipo y usuario
api.add_resource(VistaEliminarNotificacionesPorTipoYUsuario, '/notificaciones/eliminar/<int:id_usuario>')

#enpoint para actualizar los "leidos" de notificaciones
api.add_resource(VistaMarcarNotificacionesLeidas, '/notificaciones/marcar_como_leidas/<int:id_usuario>')
api.add_resource(VistaMarcarNotificacionesComoLeidas, '/notificaciones/marcar_como_leidas/<int:id_usuario>')

#enpoint para ver si hay notificaciones no leidas y cuantas hay notificaciones
api.add_resource(VistaNotificacionesNoLeidas, '/notificaciones/tiene_no_leidas/<int:id_usuario>')

#enpoint para sacar la pagina de explorar
api.add_resource(VistaRecomendacionesHome, '/page_explorar/<int:id_usuario>')

#enpoint para sacar los usuarios mas destacados
api.add_resource(VistaUsuariosTop, '/usuarios/top')


#enpoint para obtener categorias por publicacion
api.add_resource(VistaCategoriasDePublicacion,'/publicaciones/<int:id_publicacion>/categorias')

#endpoint para verificar contrasena
api.add_resource(PasswordResetInit, '/password-reset/init')
api.add_resource(PasswordResetVerify, '/password-reset/verify')
api.add_resource(PasswordResetComplete, '/password-reset/complete')

api.add_resource(VerifyCurrentPassword, '/verify_current_password')
api.add_resource(PasswordResetCompleteNoOTP, '/change_password')

#endpoint para manejo de etiquetas
api.add_resource(EtiquetasPublicacionResource, '/publicaciones/<int:publicacion_id>/etiquetas'
)

api.add_resource(EtiquetasDisponiblesResource, '/etiquetas/disponibles')
api.add_resource(AsignarEtiquetaPublicacionResource, '/publicaciones/<int:publicacion_id>/etiquetas/asignar')


#Endpoint de busqueda exclusiva de publicaciones
api.add_resource(Vista_Busqueda_publicaciones, '/buscar_publicaciones')

#Endpoint de verificar nombre de usuario
api.add_resource(VistaCheckUsername, '/usuario/check-username/<string:nombre_usuario>')

@app.route("/")
def home():
    # return jsonify({"mensaje": "API en funcionamiento"})
    data_set = {'page':'home', 'title':'API'}
    return data_set

# Obtener todas las tablas de la base de datos
@app.route('/api/tables', methods=['GET'])
def get_tables():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    return jsonify(tables)

# CRUD dinámico: Obtener todos los registros de una tabla
@app.route('/api/<string:table_name>', methods=['GET'])
def get_table_data(table_name):
    try:
        result = db.session.execute(text(f"SELECT * FROM {table_name}"))
        columns = [col for col in result.keys()]
        data = [dict(zip(columns, row)) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# CRUD dinámico: Insertar datos en una tabla
@app.route('/api/<string:table_name>', methods=['POST'])
def insert_into_table(table_name):
    try:
        data = request.json
        columns = ', '.join(data.keys())
        values = ', '.join([f":{key}" for key in data.keys()])
        query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")
        db.session.execute(query, data)
        db.session.commit()
        return jsonify({"message": "Registro insertado correctamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# CRUD dinámico: Actualizar un registro
@app.route('/api/<string:table_name>/<int:id>', methods=['PUT'])
def update_table_entry(table_name, id):
    try:
        data = request.json
        update_str = ', '.join([f"{key} = :{key}" for key in data.keys()])
        query = text(f"UPDATE {table_name} SET {update_str} WHERE id = :id")
        data['id'] = id
        db.session.execute(query, data)
        db.session.commit()
        return jsonify({"message": "Registro actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# CRUD dinámico: Eliminar un registro
@app.route('/api/<string:table_name>/<int:id>', methods=['DELETE'])
def delete_table_entry(table_name, id):
    try:
        query = text(f"DELETE FROM {table_name} WHERE id = :id")
        db.session.execute(query, {"id": id})
        db.session.commit()
        return jsonify({"message": "Registro eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__': #5000
    app.run(host='0.0.0.0', port=5000, debug=True)


# Nuevo endpoint para obtener información de llaves foráneas
@app.route('/api/foreign-keys/<string:table_name>', methods=['GET'])
def get_foreign_keys(table_name):
    try:
        inspector = db.inspect(db.engine)
        foreign_keys = []
        
        # Mapeo de tablas a sus campos de visualización
        display_fields = {
            'sexo': 'Nombre_sexo',
            'rol': 'Nombre_rol',
            'estado': 'Nombre_estado',
            'tipo_pqrs': 'Nombre_tipo',
            'reaccion': 'Nombre_reaccion',
            'categoria': 'Nombre_categoria',
            'tiponotificacion': 'Nombre',
            'usuario': 'Nombre_usuario',
            'publicacion': 'Titulo_publicacion',
            'estado': 'Nombre_estado'
            # Agrega más mapeos según sea necesario
        }
        
        for fk in inspector.get_foreign_keys(table_name):
            local_column = fk['constrained_columns'][0]
            related_table = fk['referred_table']
            
            # Usar el campo de visualización mapeado o 'nombre' por defecto
            display_field = display_fields.get(related_table, 'nombre')
            
            foreign_keys.append({
                'column': local_column,
                'related_table': related_table,
                'display_field': display_field
            })
        
        return jsonify(foreign_keys)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# with app.app_context():
#     # tabla Estado
#     estado1 = Estado(Nombre_estado='Activo', Descripcion_estado='Estado activo')
#     estado2 = Estado(Nombre_estado='Inactivo', Descripcion_estado='Estado inactivo')
#     estado3 = Estado(Nombre_estado='Pendiente', Descripcion_estado='Estado pendiente')
#     db.session.add_all([estado1, estado2, estado3])
#     db.session.commit()

#     # tabla Sexo
#     sexo1 = Sexo(Nombre_sexo='No especificado', Descripcion_sexo='No especificado')
#     sexo2 = Sexo(Nombre_sexo='Masculino', Descripcion_sexo='Masculino')
#     sexo3 = Sexo(Nombre_sexo='Femenino', Descripcion_sexo='Femenino')
#     sexo4 = Sexo(Nombre_sexo='Otro', Descripcion_sexo=' Otro')
#     db.session.add_all([sexo1, sexo2, sexo3, sexo4])
#     db.session.commit()

#     # tabla Rol
#     rol1 = Rol(Nombre_rol='Admin', Descripcion_rol='Administrador')
#     rol2 = Rol(Nombre_rol='Usuario', Descripcion_rol='Usuario regular')
#     rol3 = Rol(Nombre_rol='Moderador', Descripcion_rol='Moderador de contenido')
#     db.session.add_all([rol1, rol2, rol3])
#     db.session.commit()

#     #tabla Usuario
#     usuario1 = Usuario(Nombre_usuario='usuario1', Descripcion_usuario='Descripcion usuario 1', contrasena='pass1', correo_usuario='usuario1@mail.com', ID_sexo=1, ID_rol=1)
#     usuario2 = Usuario(Nombre_usuario='usuario2', Descripcion_usuario='Descripcion usuario 2', contrasena='pass2', correo_usuario='usuario2@mail.com', ID_sexo=2, ID_rol=2)
#     usuario3 = Usuario(Nombre_usuario='usuario3', Descripcion_usuario='Descripcion usuario 2', contrasena='pass3', correo_usuario='usuario3@mail.com', ID_sexo=3, ID_rol=3)
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
#     reaccion3 = Reaccion(Nombre_reaccion='Dislike', Img_reaccion='dislike.png', Descripcion_reaccion='No me gusta')
#     db.session.add_all([reaccion1, reaccion2, reaccion3])
#     db.session.commit()

#     # Tabla Publicacion con fechas y horas diferentes
#     publicacion1 = Publicacion(Titulo_publicacion='Título 1', Fecha_Publicacion='2025-02-23 15:30:00', Descripcion_publicacion='Descripción 1', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701873/Publicaciones/ligrccsvji4qfn0hmfab.jpg', Cont_Explicit_publi=0, ID_usuario=1)
#     publicacion2 = Publicacion(Titulo_publicacion='Título 2', Fecha_Publicacion='2025-02-23 11:10:00', Descripcion_publicacion='Descripción 2', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701872/Publicaciones/g9z61ybxewxm3m3mzkut.jpg', Cont_Explicit_publi=0, ID_usuario=2)
#     publicacion3 = Publicacion(Titulo_publicacion='Título 3', Fecha_Publicacion='2025-02-22 20:05:00', Descripcion_publicacion='Descripción 3', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701871/Publicaciones/isaqzujr6rzhapytdxs7.jpg', Cont_Explicit_publi=0, ID_usuario=2)
#     publicacion4 = Publicacion(Titulo_publicacion='Título 4', Fecha_Publicacion='2025-02-22 09:45:00', Descripcion_publicacion='Descripción 4', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701870/Publicaciones/xompitw5qcan7knzc9lc.jpg', Cont_Explicit_publi=0, ID_usuario=1)
#     publicacion5 = Publicacion(Titulo_publicacion='Título 5', Fecha_Publicacion='2025-02-22 07:15:00', Descripcion_publicacion='Descripción 5', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701865/Publicaciones/btm0amd5pdapienwbddd.jpg', Cont_Explicit_publi=0, ID_usuario=2)
#     publicacion6 = Publicacion(Titulo_publicacion='Título 6', Fecha_Publicacion='2025-02-21 14:30:00', Descripcion_publicacion='Descripción 6', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701865/Publicaciones/nybj09jzdz8pgwx98hqd.jpg', Cont_Explicit_publi=0, ID_usuario=1)
#     publicacion7 = Publicacion(Titulo_publicacion='Título 7', Fecha_Publicacion='2025-02-21 10:15:00', Descripcion_publicacion='Descripción 7', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701865/Publicaciones/j4nrhf7bgvr0n6uuclfa.jpg', Cont_Explicit_publi=0, ID_usuario=2)
#     publicacion8 = Publicacion(Titulo_publicacion='Título 8', Fecha_Publicacion='2025-02-21 08:00:00', Descripcion_publicacion='Descripción 8', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701860/Publicaciones/xy0ko9e1fayjpi4nyhc5.jpg', Cont_Explicit_publi=0, ID_usuario=1)
#     publicacion9 = Publicacion(Titulo_publicacion='Título 9', Fecha_Publicacion='2025-02-20 18:20:00', Descripcion_publicacion='Descripción 9', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701860/Publicaciones/uhnkq80nkrskji3rjttr.jpg', Cont_Explicit_publi=0, ID_usuario=2)
#     publicacion10 = Publicacion(Titulo_publicacion='Título 10', Fecha_Publicacion='2025-02-20 12:00:00', Descripcion_publicacion='Descripción 10', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701856/Publicaciones/usosx7zsad33xjf7pwlm.jpg', Cont_Explicit_publi=0, ID_usuario=1)
#     publicacion11 = Publicacion(Titulo_publicacion='Título 11', Fecha_Publicacion='2025-02-19 16:40:00', Descripcion_publicacion='Descripción 11', Img_publicacion='https://res.cloudinary.com/dnssxeplk/image/upload/v1733701855/Publicaciones/fvr6tyxe9r5ctdhdxzo1.jpg', Cont_Explicit_publi=0, ID_usuario=2)
#     db.session.add_all([publicacion1, publicacion2, publicacion3, publicacion4, publicacion5, publicacion6, publicacion7, publicacion8, publicacion9, publicacion10, publicacion11])
#     db.session.commit()

#     # tabla Comentario
#     comentario1 = Comentario(Contenido_comentario='Comentario 1', ID_usuario=1, ID_publicacion=1)
#     comentario2 = Comentario(Contenido_comentario='Comentario 2', ID_usuario=2, ID_publicacion=2)
#     comentario3 = Comentario(Contenido_comentario='Comentario 3', ID_usuario=3, ID_publicacion=3)
#     db.session.add_all([comentario1, comentario2, comentario3])
#     db.session.commit()

#     #Tabla Categoria 
#     categoria1 = Categoria(Nombre_categoria='Arquitectura', Descripcion_categoria='Descripción 1', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790299/categoria_arquitecht_w0yola.jpg')
#     categoria2 = Categoria(Nombre_categoria='Impresionismo', Descripcion_categoria='Descripción 2', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790298/categorias1_rw0dro.jpg')
#     categoria3 = Categoria(Nombre_categoria='Neon', Descripcion_categoria='Descripción 3', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790297/categorias_wbjufi.jpg')
#     categoria4 = Categoria(Nombre_categoria='Universo', Descripcion_categoria='Descripción 4', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790296/categoria_universe_mvc2af.jpg')
#     categoria5 = Categoria(Nombre_categoria='Profesional', Descripcion_categoria='Descripción 5', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790295/categoria_fondos_xccym8.jpg')
#     categoria6 = Categoria(Nombre_categoria='Fotografia', Descripcion_categoria='Descripción 6', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790295/categoria_realismo_skbac0.webp')
#     categoria7 = Categoria(Nombre_categoria='Paisaje', Descripcion_categoria='Descripción 7', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790294/categoria_paisaje_kl6qgq.jpg')
#     categoria8 = Categoria(Nombre_categoria='Dibujo', Descripcion_categoria='Descripción 8', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790293/categoria_dibujo_ziroou.jpg')
#     categoria9 = Categoria(Nombre_categoria='Edicion', Descripcion_categoria='Descripción 9', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790293/categoria_fantacia_osj17w.jpg')
#     categoria10 = Categoria(Nombre_categoria='Anime', Descripcion_categoria='Descripción 10', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790293/categoria_anime_rac5jj.jpg')
#     categoria11 = Categoria(Nombre_categoria='Blanco y Negro', Descripcion_categoria='Descripción 11', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790292/categoria_black_and_white_scxy2b.jpg')
#     categoria12 = Categoria(Nombre_categoria='Cartoon', Descripcion_categoria='Descripción 12', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790292/categoria_cartoon_dflm2w.jpg')
#     categoria13 = Categoria(Nombre_categoria='Mozaico', Descripcion_categoria='Descripción 13', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790292/categoria_abstract_d2aqah.jpg')
#     categoria14 = Categoria(Nombre_categoria='Animales', Descripcion_categoria='Descripción 14', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790292/categoria_animales_eeh3nu.jpg')
#     categoria15 = Categoria(Nombre_categoria='Retro', Descripcion_categoria='Descripción 15', Img_categoria='https://res.cloudinary.com/dnssxeplk/image/upload/v1738790292/categoriasci-fi_tctt3a.jpg')
#     db.session.add_all([categoria1, categoria2, categoria3, categoria4, categoria5, categoria6, categoria7, categoria8, categoria9, categoria10, categoria11, categoria12, categoria13, categoria14, categoria15])
#     db.session.commit()

#     # tabla tipo notificaciones
#     tipo1 = TipoNotificacion(Nombre='Nuevo seguidor', Mensaje_base='¡{usuario} empezó a seguirte!')
#     tipo2 = TipoNotificacion(Nombre='Like publicación', Mensaje_base='A {usuario} le gustó tu publicación')
#     tipo3 = TipoNotificacion(Nombre='Nuevo comentario', Mensaje_base='{usuario} comentó en tu publicación')
#     db.session.add_all([tipo1, tipo2, tipo3])
#     db.session.commit()

#     # tabla PublicacionGuardada
#     pub_guardada1 = Publicacion_Guardada(Fecha_guardado='2024-11-28', ID_usuario=1, ID_publicacion=1)
#     pub_guardada2 = Publicacion_Guardada(Fecha_guardado='2024-11-28', ID_usuario=2, ID_publicacion=2)
#     pub_guardada3 = Publicacion_Guardada(Fecha_guardado='2024-11-28', ID_usuario=3, ID_publicacion=3)
#     db.session.add_all([pub_guardada1, pub_guardada2, pub_guardada3])
#     db.session.commit()

#     # tabla Publicacion_Reaccion
#     pub_reaccion1 = Publicacion_Reaccion(ID_usuario=1,ID_publicacion=1, ID_reaccion=1)
#     pub_reaccion2 = Publicacion_Reaccion(ID_usuario=2,ID_publicacion=2, ID_reaccion=2)
#     pub_reaccion3 = Publicacion_Reaccion(ID_usuario=3,ID_publicacion=3, ID_reaccion=3)
#     db.session.add_all([pub_reaccion1, pub_reaccion2, pub_reaccion3])
#     db.session.commit()

#     # tabla Usuario_Reaccion
#     usuario_reaccion1 = Usuario_Reaccion(ID_usuario=1, ID_publicacion=1, ID_reaccion=1)
#     usuario_reaccion2 = Usuario_Reaccion(ID_usuario=2, ID_publicacion=2, ID_reaccion=2)
#     usuario_reaccion3 = Usuario_Reaccion(ID_usuario=3, ID_publicacion=3, ID_reaccion=3)
#     db.session.add_all([usuario_reaccion1, usuario_reaccion2, usuario_reaccion3])
#     db.session.commit()

#     # tabla Publicacion_Categoria
#     pub_categoria1 = Publicacion_Categoria(ID_publicacion=1, ID_categoria=1)
#     pub_categoria2 = Publicacion_Categoria(ID_publicacion=2, ID_categoria=2)
#     pub_categoria3 = Publicacion_Categoria(ID_publicacion=3, ID_categoria=3)
#     db.session.add_all([pub_categoria1, pub_categoria2, pub_categoria3])
#     db.session.commit()
