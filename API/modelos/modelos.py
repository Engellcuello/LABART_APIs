from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from werkzeug.security import generate_password_hash, check_password_hash

db=SQLAlchemy()


class PQRS(db.Model):
    __tablename__ = 'PQRS'

    ID_pqrs = db.Column(db.Integer, primary_key=True)
    Fecha_pqrs = db.Column(db.Date, default=db.func.current_date())
    Contenido_pqrs = db.Column(db.String(100))

    ID_estado = db.Column(db.Integer, db.ForeignKey('Estado.ID_estado'), nullable=False)
    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'), nullable=False)
    ID_tipo_pqrs = db.Column(db.Integer, db.ForeignKey('Tipo_PQRS.ID_tipo_pqrs'), nullable=False)

    estado = db.relationship('Estado', back_populates='pqrs')
    usuario = db.relationship('Usuario', back_populates='pqrs')
    tipo_pqrs = db.relationship('Tipo_PQRS', back_populates='pqrs')


class Tipo_PQRS(db.Model):
    __tablename__ = 'Tipo_PQRS'

    ID_tipo_pqrs = db.Column(db.Integer, primary_key=True)
    Nombre_tipo = db.Column(db.String(20))
    Descripcion_tipo = db.Column(db.String(60))

    pqrs = db.relationship('PQRS', back_populates='tipo_pqrs', cascade='all, delete, delete-orphan')


class Asistente(db.Model):
    __tablename__ = 'Asistente'

    ID_asistente = db.Column(db.Integer, primary_key=True)
    Fecha_peticion = db.Column(db.Date, default=db.func.current_date())
    Detalle_asistente = db.Column(db.String(255))

    ID_estado = db.Column(db.Integer, db.ForeignKey('Estado.ID_estado'), nullable=False)
    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'), nullable=False)

    estado = db.relationship('Estado', back_populates='asistentes')
    usuario = db.relationship('Usuario', back_populates='asistentes')


class Estado(db.Model):
    __tablename__ = 'Estado'

    ID_estado = db.Column(db.Integer, primary_key=True)
    Nombre_estado = db.Column(db.String(255))
    Descripcion_estado = db.Column(db.String(255))

    pqrs = db.relationship('PQRS', back_populates='estado', cascade='all, delete, delete-orphan')
    asistentes = db.relationship('Asistente', back_populates='estado', cascade='all, delete, delete-orphan')


class Sexo(db.Model):
    __tablename__ = 'Sexo'

    ID_sexo = db.Column(db.Integer, primary_key=True)
    Descripcion_sexo = db.Column(db.String(20))
    Nombre_sexo = db.Column(db.String(12))

    usuarios = db.relationship('Usuario', back_populates='sexo', cascade='all, delete, delete-orphan')


class Reaccion(db.Model):
    __tablename__ = 'Reaccion'

    ID_reaccion = db.Column(db.Integer, primary_key=True)
    Nombre_reaccion = db.Column(db.String(20))
    Img_reaccion = db.Column(db.String(80))
    Descripcion_reaccion = db.Column(db.String(20))

    publicaciones = db.relationship('Publicacion_Reaccion', back_populates='reaccion', cascade='all, delete, delete-orphan')
    usuarios = db.relationship('Usuario_Reaccion', back_populates='reaccion', cascade='all, delete, delete-orphan')


class Usuario(db.Model):
    __tablename__ = 'Usuario'

    ID_usuario = db.Column(db.Integer, primary_key=True)
    Nombre_usuario = db.Column(db.String(20))
    contrasena_hash = db.Column(db.String(255))
    correo_usuario = db.Column(db.String(60))
    Fecha_usuario = db.Column(db.Date, default=db.func.current_date())
    Notificaciones = db.Column(db.Boolean, default=False)
    Img_usuario = db.Column(db.String(60))
    ID_sexo = db.Column(db.Integer, db.ForeignKey('Sexo.ID_sexo'), nullable=False)
    ID_rol = db.Column(db.Integer, db.ForeignKey('Rol.ID_rol'), nullable=False)
    Cont_Explicit = db.Column(db.Boolean, default=False)
    
    @property
    def contrasena(self):
        raise AttributeError("La contraseña no es un atributo legible.")

    @property
    def contrasena(self):
        raise AttributeError("La contraseña no es un atributo legible.")

    @contrasena.setter
    def contrasena(self, password):
        self.contrasena_hash = generate_password_hash(password)

    def verificar_contrasena(self, password):
        if not self.contrasena_hash:
            return False
        return check_password_hash(self.contrasena_hash, password)
    

    sexo = db.relationship('Sexo', back_populates='usuarios')
    rol = db.relationship('Rol', back_populates='usuarios')
    pqrs = db.relationship('PQRS', back_populates='usuario', cascade='all, delete, delete-orphan')
    notificaciones = db.relationship('Notificaciones', back_populates='usuario', cascade='all, delete, delete-orphan')
    asistentes = db.relationship('Asistente', back_populates='usuario', cascade='all, delete, delete-orphan')
    comentarios = db.relationship('Comentario', back_populates='usuario', cascade='all, delete, delete-orphan')
    reacciones = db.relationship('Usuario_Reaccion', back_populates='usuario', cascade='all, delete, delete-orphan')
    publicaciones = db.relationship('Publicacion', back_populates='usuario', cascade='all, delete, delete-orphan')
    publicaciones_guardadas = db.relationship('PublicacionGuardada', back_populates='usuario', cascade='all, delete, delete-orphan')


class Rol(db.Model):
    __tablename__ = 'Rol'

    ID_rol = db.Column(db.Integer, primary_key=True)
    Nombre_rol = db.Column(db.String(20))
    Descripcion_rol = db.Column(db.String(40))

    usuarios = db.relationship('Usuario', back_populates='rol', cascade='all, delete, delete-orphan')


class Comentario(db.Model):
    __tablename__ = 'Comentario'

    ID_comentario = db.Column(db.Integer, primary_key=True)
    Contenido_comentario = db.Column(db.String(100))
    Fecha_comentario = db.Column(db.Date, default=db.func.current_date())

    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'), nullable=False)
    ID_publicacion = db.Column(db.Integer, db.ForeignKey('Publicacion.ID_publicacion'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='comentarios')
    publicacion = db.relationship('Publicacion', back_populates='comentarios')


class Publicacion(db.Model):
    __tablename__ = 'Publicacion'

    ID_publicacion = db.Column(db.Integer, primary_key=True)
    Fecha_publicacion = db.Column(db.Date, default=db.func.current_date())
    Descripcion_publicacion = db.Column(db.String(100))
    Img_publicacion = db.Column(db.String(100))
    Cont_Explicit_publi = db.Column(db.Boolean, default=False)

    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='publicaciones')
    comentarios = db.relationship('Comentario', back_populates='publicacion', cascade='all, delete, delete-orphan')
    reacciones = db.relationship('Publicacion_Reaccion', back_populates='publicacion', cascade='all, delete, delete-orphan')
    categorias = db.relationship('Publicacion_Categoria', back_populates='publicacion', cascade='all, delete, delete-orphan')
    publicaciones_guardadas = db.relationship('PublicacionGuardada', back_populates='publicacion', cascade='all, delete, delete-orphan')


class Categoria(db.Model):
    __tablename__ = 'Categoria'

    ID_categoria = db.Column(db.Integer, primary_key=True)
    Nombre_categoria = db.Column(db.String(20))
    Descripcion_categoria = db.Column(db.String(50))

    publicaciones = db.relationship('Publicacion_Categoria', back_populates='categoria', cascade='all, delete, delete-orphan')


class Notificaciones(db.Model):
    __tablename__ = 'Notificaciones'

    ID_notificaciones = db.Column(db.Integer, primary_key=True)
    Mensaje = db.Column(db.String(100))
    Fecha_notificacion = db.Column(db.Date)

    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='notificaciones')


class PublicacionGuardada(db.Model):
    __tablename__ = 'PublicacionGuardada'

    ID_publicacion_guardada = db.Column(db.Integer, primary_key=True)
    Fecha_guardado = db.Column(db.Date)

    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'), nullable=False)
    ID_publicacion = db.Column(db.Integer, db.ForeignKey('Publicacion.ID_publicacion'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='publicaciones_guardadas')
    publicacion = db.relationship('Publicacion', back_populates='publicaciones_guardadas')



class Publicacion_Reaccion(db.Model):
    __tablename__ = 'Publicacion_Reaccion'

    ID_publicacion_reaccion = db.Column(db.Integer, primary_key=True)

    ID_publicacion = db.Column(db.Integer, db.ForeignKey('Publicacion.ID_publicacion'), nullable=False)
    ID_reaccion = db.Column(db.Integer, db.ForeignKey('Reaccion.ID_reaccion'), nullable=False)

    publicacion = db.relationship('Publicacion', back_populates='reacciones')
    reaccion = db.relationship('Reaccion', back_populates='publicaciones')


class Usuario_Reaccion(db.Model):
    __tablename__ = 'Usuario_Reaccion'

    ID_usuario_reaccion = db.Column(db.Integer, primary_key=True)

    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'), nullable=False)
    ID_reaccion = db.Column(db.Integer, db.ForeignKey('Reaccion.ID_reaccion'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='reacciones')
    reaccion = db.relationship('Reaccion', back_populates='usuarios')


class Publicacion_Categoria(db.Model):
    __tablename__ = 'Publicacion_Categoria'

    ID_publicacion_categoria = db.Column(db.Integer, primary_key=True)

    ID_publicacion = db.Column(db.Integer, db.ForeignKey('Publicacion.ID_publicacion'), nullable=False)
    ID_categoria = db.Column(db.Integer, db.ForeignKey('Categoria.ID_categoria'), nullable=False)

    publicacion = db.relationship('Publicacion', back_populates='categorias')
    categoria = db.relationship('Categoria', back_populates='publicaciones')


class PQRSSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PQRS
        include_relationships = True
        load_instance = True

class Tipo_PQRSSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tipo_PQRS
        include_relationships = True
        load_instance = True

class EstadoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Estado
        include_relationships = True
        load_instance = True

class AsistenteSchema(SQLAlchemyAutoSchema):
    estado = fields.Nested(EstadoSchema)
    class Meta:
        model = Asistente
        include_relationships = True
        load_instance = True
    
class SexoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Sexo
        include_relationships = True
        load_instance = True

class ReaccionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Reaccion
        include_relationships = True
        load_instance = True

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

class RolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Rol
        include_relationships = True
        load_instance = True

class ComentarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comentario
        include_relationships = True
        load_instance = True

class PublicacionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Publicacion
        include_relationships = True
        load_instance = True

class CategoriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Categoria
        include_relationships = True
        load_instance = True

class NotificacionesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Notificaciones
        include_relationships = True
        load_instance = True

class PublicacionGuardadaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PublicacionGuardada
        include_relationships = True
        load_instance = True

class Publicacion_ReaccionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Publicacion_Reaccion
        include_relationships = True
        load_instance = True

class Usuario_ReaccionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario_Reaccion
        include_relationships = True
        load_instance = True

class Publicacion_CategoriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Publicacion_Categoria
        include_relationships = True
        load_instance = True
