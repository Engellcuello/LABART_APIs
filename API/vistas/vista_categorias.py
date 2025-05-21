from flask_restful import Resource
from flask import jsonify, request
from sqlalchemy import desc, func

from API.modelos.modelos import Comentario, Etiqueta_Publicacion, Etiqueta_PublicacionSchema, Historial, Publicacion, Publicacion_Categoria, Publicacion_Reaccion, PublicacionSchema, Usuario, UsuarioSchema  # Corrigiendo importación

from ..modelos import db, Categoria, CategoriaSchema

categoriaschema = CategoriaSchema()
publicacion_schema = PublicacionSchema()
usuario_schema = UsuarioSchema()
categoria_schema = CategoriaSchema()
etiqueta_schema = Etiqueta_PublicacionSchema()

class VistaCategoria_All(Resource):
    def get(self):
        categorias = Categoria.query.all()
        return [categoriaschema.dump(categoria) for categoria in categorias], 200

    def post(self):
        data = request.get_json()
        nueva_categoria = Categoria(**data)
        db.session.add(nueva_categoria)
        db.session.commit()
        return categoriaschema.dump(nueva_categoria), 201


class VistaCategoria(Resource):
    def get(self, id=None):
        if id:
            categoria = Categoria.query.get(id)
            if categoria:
                return categoriaschema.dump(categoria)
            else:
                return {'message': 'Categoría no encontrada'}, 404
        else:
            categorias = Categoria.query.all()
            return [categoriaschema.dump(categoria) for categoria in categorias], 200

    def put(self, id):
        categoria = Categoria.query.get_or_404(id)
        categoria.ID_categoria = request.json.get('ID_categoria', categoria.ID_categoria)
        categoria.Nombre_categoria = request.json.get('Nombre_categoria', categoria.Nombre_categoria)
        categoria.Descripcion_categoria = request.json.get('Descripcion_categoria', categoria.Descripcion_categoria)
        categoria.Img_categoria = request.json.get('Img_categoria', categoria.Img_categoria)
        categoria.publicaciones = request.json.get('Publicacion_Categoria', categoria.publicaciones)

        db.session.commit()
        return categoriaschema.dump(categoria), 200  # Se corrige para devolver la categoría actualizada

    def delete(self, id):
        categoria = Categoria.query.get_or_404(id)  # Se usa get_or_404 para manejo automático de error 404

        db.session.delete(categoria)
        db.session.commit()
        return {'message': 'Categoria eliminada correctamente', 'deleted_category': categoriaschema.dump(categoria)}, 200

class VistaRecomendacionesHome(Resource):
    def get(self, id_usuario):
        try:
            # 1. Obtener las 3 categorías más vistas por el usuario desde su historial
            categorias_mas_vistas = db.session.query(
                Publicacion_Categoria.ID_categoria,
                func.count(Publicacion_Categoria.ID_categoria).label('frecuencia')
            ).join(
                Historial, 
                Publicacion_Categoria.ID_publicacion == Historial.ID_publicacion
            ).filter(
                Historial.ID_usuario == id_usuario
            ).group_by(
                Publicacion_Categoria.ID_categoria
            ).order_by(
                desc('frecuencia')
            ).limit(3).all()

            # Si no hay suficiente historial, obtener categorías populares generales
            if len(categorias_mas_vistas) < 3:
                categorias_adicionales = db.session.query(
                    Publicacion_Categoria.ID_categoria,
                    func.count(Publicacion_Categoria.ID_categoria).label('frecuencia')
                ).group_by(
                    Publicacion_Categoria.ID_categoria
                ).order_by(
                    desc('frecuencia')
                ).limit(3 - len(categorias_mas_vistas)).all()
                
                categorias_mas_vistas.extend(categorias_adicionales)

            # 2. Para cada categoría, obtener 3 publicaciones
            secciones = []
            
            for categoria in categorias_mas_vistas:
                categoria_id = categoria.ID_categoria
                categoria_obj = Categoria.query.get(categoria_id)
                
                if not categoria_obj:
                    continue

                # Obtener 3 publicaciones recientes de esta categoría
                publicaciones = Publicacion.query\
                    .join(Publicacion_Categoria, Publicacion.ID_publicacion == Publicacion_Categoria.ID_publicacion)\
                    .filter(Publicacion_Categoria.ID_categoria == categoria_id)\
                    .order_by(desc(Publicacion.Fecha_Publicacion))\
                    .limit(3)\
                    .all()

                publicaciones_data = []
                
                for pub in publicaciones:
                    # Datos del usuario
                    usuario = Usuario.query.get(pub.ID_usuario)
                    
                    # Etiqueta principal de la publicación
                    etiqueta_principal = Etiqueta_Publicacion.query\
                        .filter_by(ID_publicacion=pub.ID_publicacion)\
                        .order_by(desc(Etiqueta_Publicacion.score))\
                        .first()
                    
                    # Totales
                    total_reacciones = Publicacion_Reaccion.query\
                        .filter_by(ID_publicacion=pub.ID_publicacion)\
                        .count()
                    
                    total_comentarios = Comentario.query\
                        .filter_by(ID_publicacion=pub.ID_publicacion)\
                        .count()
                    
                    publicaciones_data.append({
                        'imagen_publicacion': pub.Img_publicacion,
                        'nombre_usuario': usuario.Nombre_usuario,
                        'foto_usuario': usuario.Img_usuario,
                        'fecha_publicacion': pub.Fecha_Publicacion.isoformat(),
                        'categoria': categoria_obj.Nombre_categoria,
                        'etiqueta': etiqueta_principal.descripcion if etiqueta_principal else None,
                        'total_reacciones': total_reacciones,
                        'total_comentarios': total_comentarios
                    })

                # Solo agregar si hay publicaciones
                if publicaciones_data:
                    secciones.append({
                        'titulo_seccion': categoria_obj.Nombre_categoria,
                        'publicaciones': publicaciones_data
                    })

            # 3. Limitar a 3 secciones exactamente
            secciones = secciones[:3]
            
            # Asegurarnos de que cada sección tenga exactamente 3 publicaciones
            for seccion in secciones:
                seccion['publicaciones'] = seccion['publicaciones'][:3]
                
                # Si faltan publicaciones, completar con otras de la misma categoría o similares
                while len(seccion['publicaciones']) < 3:
                    publicacion_extra = Publicacion.query\
                        .join(Publicacion_Categoria, Publicacion.ID_publicacion == Publicacion_Categoria.ID_publicacion)\
                        .filter(Publicacion_Categoria.ID_categoria == categoria_id)\
                        .order_by(func.random())\
                        .first()
                    
                    if publicacion_extra:
                        usuario = Usuario.query.get(publicacion_extra.ID_usuario)
                        etiqueta_principal = Etiqueta_Publicacion.query\
                            .filter_by(ID_publicacion=publicacion_extra.ID_publicacion)\
                            .order_by(desc(Etiqueta_Publicacion.score))\
                            .first()
                        
                        total_reacciones = Publicacion_Reaccion.query\
                            .filter_by(ID_publicacion=publicacion_extra.ID_publicacion)\
                            .count()
                        
                        total_comentarios = Comentario.query\
                            .filter_by(ID_publicacion=publicacion_extra.ID_publicacion)\
                            .count()
                        
                        seccion['publicaciones'].append({
                            'imagen_publicacion': publicacion_extra.Img_publicacion,
                            'nombre_usuario': usuario.Nombre_usuario,
                            'foto_usuario': usuario.Img_usuario,
                            'fecha_publicacion': publicacion_extra.Fecha_Publicacion.isoformat(),
                            'categoria': categoria_obj.Nombre_categoria,
                            'etiqueta': etiqueta_principal.descripcion if etiqueta_principal else None,
                            'total_reacciones': total_reacciones,
                            'total_comentarios': total_comentarios
                        })
                    else:
                        break

            return jsonify({
                'status': 'success',
                'data': {
                    'secciones': secciones
                }
            })

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error al obtener recomendaciones: {str(e)}'
            }), 500