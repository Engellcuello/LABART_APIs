import re
from flask_restful import Resource
from flask import request
import requests
from sqlalchemy import desc, func, or_, text
from API.modelos.modelos import Color_Publicacion, Etiqueta_Publicacion, Publicacion_Reaccion
from API.vistas.resourses.cloudinary_uploader import upload_image_to_cloudinary
from API.vistas.resourses.consultas.recomendaciones import RecomendacionesHome
from ..modelos import db, Publicacion, PublicacionSchema,Usuario,Publicacion_Categoria,Categoria
from flask import jsonify
import cloudinary
import cloudinary.uploader
import cloudinary.api

import os

VISION_SERVICE_URL = os.getenv('VISION_SERVICE_URL', 'http://localhost:5000/analizar_imagen')

publicacionschema = PublicacionSchema(session=db.session)


class VistaPublicaciones_All(Resource):
    def get(self):
        publicaciones = Publicacion.query.order_by(desc(Publicacion.Fecha_Publicacion)).all()
        return [publicacionschema.dump(publicacion) for publicacion in publicaciones], 200
    
    def post(self):
        print("Headers:", request.headers)
        print("Form data:", request.form)
        print("Files:", request.files)

        try:
            # Verificar si los datos vienen en JSON o en FormData
            if request.is_json:
                data = request.get_json()
                imagen = None  # No se puede subir imagen si es JSON
            else:
                data = request.form.to_dict()
                imagen = request.files.get('Img_publicacion')

                # ✅ Conversión segura de booleano (solo en form-data)
                if 'Cont_Explicit_publi' in data:
                    valor = data['Cont_Explicit_publi']
                    data['Cont_Explicit_publi'] = valor in ['false', 'False', '0', False]
                    

            # 1. Subir imagen a Cloudinary (solo si hay imagen)
            img_url = upload_image_to_cloudinary(imagen) if imagen else None
            if img_url:
                data['Img_publicacion'] = img_url

            # 2. Crear la publicación
            schema = PublicacionSchema(session=db.session)
            nueva_publicacion = schema.load(data)
            db.session.add(nueva_publicacion)
            db.session.flush()  # Para obtener el ID antes del commit

            # 3. Si hay imagen, analizarla y guardar colores y etiquetas
            if img_url:
                self._analizar_imagen_y_guardar_metadatos(
                    img_url,
                    nueva_publicacion.ID_publicacion,
                    data.get('ID_usuario')
                )

            db.session.commit()
            return schema.dump(nueva_publicacion), 200

        except Exception as e:
            db.session.rollback()
            print("Error creando publicación:", e)
            return {'error': 'Error al crear la publicación'}, 500

    def _analizar_imagen_y_guardar_metadatos(self, image_url, id_publicacion, id_usuario):
    # 1. Llamar al servicio de análisis de imágenes
        response = requests.post(VISION_SERVICE_URL, json={'image_url': image_url})
        
        if response.status_code != 200:
            print(f"Error al analizar imagen: {response.text}")
            return

        analysis_data = response.json()

        # 2. Guardar colores (ya vienen ordenados y limitados a 5)
        colors = analysis_data.get('colores', [])
        for color in colors:
            nuevo_color = Color_Publicacion(
                red=color['red'],
                green=color['green'],
                blue=color['blue'],
                pixel_fraction=color['pixel_fraction'],
                score=color['score'],
                ID_publicacion=id_publicacion,
                ID_usuario=id_usuario
            )
            db.session.add(nuevo_color)

        # 3. Guardar etiquetas (ya vienen ordenadas y limitadas a 5)
        labels = analysis_data.get('labels', [])
        for label in labels:
            nueva_etiqueta = Etiqueta_Publicacion(
                descripcion=label['description'],
                score=label['score'],
                topicality=label['topicality'],
                ID_publicacion=id_publicacion,
                ID_usuario=id_usuario
            )
            db.session.add(nueva_etiqueta)




class VistaPublicaciones(Resource):
    def get(self, id=None):
        if id:
            publicacion = Publicacion.query.get(id)
            if publicacion:
                return publicacionschema.dump(publicacion), 200
            else:
                return {'message': 'Publicación no encontrada'}, 404
        else:
            publicaciones = Publicacion.query.all()
            return [publicacionschema.dump(publicacion) for publicacion in publicaciones], 200
        

    def put(self, id):
        publicacion = Publicacion.query.get_or_404(id)
        data = request.get_json()

        # Actualizar campos básicos de la publicación
        publicacion.Titulo_publicacion = data.get('Titulo_publicacion', publicacion.Titulo_publicacion)
        publicacion.Descripcion_publicacion = data.get('Descripcion_publicacion', publicacion.Descripcion_publicacion)
        publicacion.Img_publicacion = data.get('Img_publicacion', publicacion.Img_publicacion)
        publicacion.Cont_Explicit_publi = data.get('Cont_Explicit_publi', publicacion.Cont_Explicit_publi)
        publicacion.ID_usuario = data.get('ID_usuario', publicacion.ID_usuario)

        if 'etiquetas' in data:
            for etiqueta_descripcion in data['etiquetas']:
                # Verificar si ya existe una etiqueta igual para la publicación
                etiqueta_existente = Etiqueta_Publicacion.query.filter_by(
                    descripcion=etiqueta_descripcion,
                    ID_publicacion=id,
                    ID_usuario=publicacion.ID_usuario
                ).first()

                if not etiqueta_existente:
                    nueva_etiqueta = Etiqueta_Publicacion(
                        descripcion=etiqueta_descripcion,
                        score=98.0,  # Valores por defecto
                        topicality=90.0,  # Valores por defecto
                        ID_publicacion=id,
                        ID_usuario=publicacion.ID_usuario
                    )
                    db.session.add(nueva_etiqueta)

        db.session.commit()


    def extract_public_id_from_url(self, url):
        """Extrae el public_id de una URL de Cloudinary."""
        pattern = r"upload/(?:v\d+/)?([^\.]+)"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def extract_cloud_name_from_url(self, url):
        """Extrae el cloud_name desde la URL de Cloudinary."""
        pattern = r"https?://res\.cloudinary\.com/([^/]+)/"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def delete(self, id):
        publicacion = Publicacion.query.get_or_404(id)

        try:
            # Intentar eliminar la imagen de Cloudinary si existe
            if publicacion.Img_publicacion:
                try:
                    # Extraer el public_id y cloud_name desde la URL
                    public_id = self.extract_public_id_from_url(publicacion.Img_publicacion)
                    cloud_name = self.extract_cloud_name_from_url(publicacion.Img_publicacion)

                    if public_id and cloud_name:
                        # Configurar Cloudinary según el cloud_name
                        if cloud_name == 'dnssxeplk':  # Cuenta principal
                            cloudinary.config(
                                cloud_name='dnssxeplk',
                                api_key='637359175714758',
                                api_secret='s9L3jLCjpLYm0WpW-LxkYeHno30'
                            )
                        elif cloud_name == 'dgykc3yp5':  # Cuenta de respaldo
                            cloudinary.config(
                                cloud_name='dgykc3yp5',
                                api_key='665733994526989',
                                api_secret='lB1U1-Sviw1Ijdy7ntPUC9oPtnA'
                            )
                        else:
                            print(f"Cuenta de Cloudinary no reconocida: {cloud_name}")
                            # Continuar con la eliminación aunque no reconozcamos la cuenta

                        # Intentar eliminar la imagen (no verificamos si existe primero)
                        try:
                            result = cloudinary.uploader.destroy(public_id)
                            print(f'Resultado eliminación imagen: {result}')
                        except Exception as img_error:
                            print(f'Error al eliminar imagen de Cloudinary: {str(img_error)}')
                            # Continuar con la eliminación aunque falle la eliminación de la imagen
                except Exception as extraction_error:
                    print(f'Error al extraer información de la URL de Cloudinary: {str(extraction_error)}')
                    # Continuar con la eliminación aunque falle la extracción de datos

            # Eliminar etiquetas y publicación (esto es lo importante que debe ejecutarse)
            try:
                Etiqueta_Publicacion.query.filter_by(ID_publicacion=id).delete()
                db.session.delete(publicacion)
                db.session.commit()
                return {'message': 'Publicación eliminada correctamente'}, 200
            except Exception as db_error:
                db.session.rollback()
                return {'error': f'Error al eliminar la publicación de la base de datos: {str(db_error)}'}, 500

        except Exception as e:
            db.session.rollback()
            return {'error': f'Error inesperado al procesar la eliminación: {str(e)}'}, 500



class VistaRecomendaciones(Resource):
    def get(self, user_id):
        try:
            recomendaciones = RecomendacionesHome.obtener_recomendaciones(user_id)
            
            # Asegúrate que los datos sean serializables
            if not isinstance(recomendaciones, (list, dict)):
                raise TypeError("Las recomendaciones deben ser una lista o diccionario")
            
            return {
                'success': True,
                'recomendaciones': recomendaciones,
                'total': len(recomendaciones)
            }, 200
            
        except Exception as e:
            # Registra el error completo para diagnóstico
            import traceback
            print(f"Error en VistaRecomendaciones: {str(e)}")
            traceback.print_exc()
            
            return {
                'success': False,
                'message': f"Error al obtener recomendaciones: {str(e)}"
            }, 500

class VistaRecomendacionesPublicacion(Resource):
    def get(self, id_publicacion):
        try:
            # Validar que el ID es un número positivo
            id_publicacion = int(id_publicacion)
            if id_publicacion <= 0:
                return {'error': 'El ID de publicación debe ser un número positivo'}, 400
            
            # Consulta SQL parametrizada para evitar SQL injection
            sql_query = text("""
            WITH 
            -- Definir el margen de similitud de colores (ajustable)
            constantes AS (
                SELECT 
                    :id_publicacion_param AS id_publicacion_referencia,
                    80 AS margen_color -- Margen de diferencia permitido para cada componente RGB (0-255)
            ),

            -- Obtener etiquetas de la publicación de referencia
            etiquetas_referencia AS (
                SELECT descripcion, score
                FROM Etiqueta_Publicacion
                WHERE ID_publicacion = (SELECT id_publicacion_referencia FROM constantes)
            ),

            -- Obtener colores de la publicación de referencia
            colores_referencia AS (
                SELECT red, green, blue, score
                FROM Color_Publicacion
                WHERE ID_publicacion = (SELECT id_publicacion_referencia FROM constantes)
            ),

            -- Obtener categorías de la publicación de referencia
            categorias_referencia AS (
                SELECT ID_categoria
                FROM Publicacion_Categoria
                WHERE ID_publicacion = (SELECT id_publicacion_referencia FROM constantes)
            ),

            -- 1. Publicaciones con las mismas etiquetas (score similar con margen) y colores similares (con margen)
            mismas_etiquetas_colores_similares AS (
                SELECT 
                    p.ID_publicacion,
                    1 AS prioridad,
                    COUNT(DISTINCT ep.descripcion) AS coincidencias_etiquetas,
                    SUM(ep.score) AS suma_scores_etiquetas,
                    COUNT(DISTINCT cp.ID_color_publicacion) AS coincidencias_colores,
                    SUM(
                        (1 - (ABS(cp.red - cr.red)/255.0)) * 
                        (1 - (ABS(cp.green - cr.green)/255.0)) * 
                        (1 - (ABS(cp.blue - cr.blue)/255.0)) * 
                        ((cp.score + cr.score)/2)
                    ) AS suma_scores_colores,
                    COUNT(DISTINCT pc.ID_categoria) AS coincidencias_categorias
                FROM Publicacion p
                -- Unir con etiquetas que coinciden en nombre y con score similar (margen de 0.1)
                JOIN Etiqueta_Publicacion ep ON p.ID_publicacion = ep.ID_publicacion
                JOIN etiquetas_referencia er ON ep.descripcion = er.descripcion 
                                       AND ABS(ep.score - er.score) <= 20  -- Margen de 0.9 para el score
                -- Unir con colores que están dentro del margen permitido
                JOIN Color_Publicacion cp ON p.ID_publicacion = cp.ID_publicacion
                JOIN colores_referencia cr ON 
                    ABS(cp.red - cr.red) <= (SELECT margen_color FROM constantes) AND
                    ABS(cp.green - cr.green) <= (SELECT margen_color FROM constantes) AND
                    ABS(cp.blue - cr.blue) <= (SELECT margen_color FROM constantes)
                -- Unir con categorías en común
                LEFT JOIN Publicacion_Categoria pc ON p.ID_publicacion = pc.ID_publicacion
                LEFT JOIN categorias_referencia cr2 ON pc.ID_categoria = cr2.ID_categoria
                WHERE p.ID_publicacion != (SELECT id_publicacion_referencia FROM constantes)
                GROUP BY p.ID_publicacion
            ),
            
            -- 2. Publicaciones con categorías en común (nueva prioridad 2)
            categorias_comunes AS (
                SELECT 
                    p.ID_publicacion,
                    2 AS prioridad,
                    0 AS coincidencias_etiquetas,
                    0 AS suma_scores_etiquetas,
                    0 AS coincidencias_colores,
                    0 AS suma_scores_colores,
                    COUNT(*) AS coincidencias_categorias
                FROM Publicacion p
                JOIN Publicacion_Categoria pc ON p.ID_publicacion = pc.ID_publicacion
                JOIN categorias_referencia cr ON pc.ID_categoria = cr.ID_categoria
                WHERE p.ID_publicacion != (SELECT id_publicacion_referencia FROM constantes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM mismas_etiquetas_colores_similares)
                GROUP BY p.ID_publicacion
            ),

            -- 3. Publicaciones con algunas etiquetas en común (no necesariamente mismo score) y algunos colores similares
            etiquetas_colores_comunes AS (
                SELECT 
                    p.ID_publicacion,
                    3 AS prioridad,
                    COUNT(DISTINCT ep.descripcion) AS coincidencias_etiquetas,
                    SUM(ep.score) AS suma_scores_etiquetas,
                    COUNT(DISTINCT cp.ID_color_publicacion) AS coincidencias_colores,
                    SUM(
                        (1 - (ABS(cp.red - cr.red)/255.0)) * 
                        (1 - (ABS(cp.green - cr.green)/255.0)) * 
                        (1 - (ABS(cp.blue - cr.blue)/255.0)) * 
                        ((cp.score + cr.score)/2)
                    ) AS suma_scores_colores,
                    0 AS coincidencias_categorias
                FROM Publicacion p
                JOIN Etiqueta_Publicacion ep ON p.ID_publicacion = ep.ID_publicacion
                JOIN etiquetas_referencia er ON ep.descripcion = er.descripcion
                JOIN Color_Publicacion cp ON p.ID_publicacion = cp.ID_publicacion
                JOIN colores_referencia cr ON 
                    ABS(cp.red - cr.red) <= (SELECT margen_color FROM constantes) AND
                    ABS(cp.green - cr.green) <= (SELECT margen_color FROM constantes) AND
                    ABS(cp.blue - cr.blue) <= (SELECT margen_color FROM constantes)
                WHERE p.ID_publicacion != (SELECT id_publicacion_referencia FROM constantes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM mismas_etiquetas_colores_similares)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM categorias_comunes)
                GROUP BY p.ID_publicacion
            ),

            -- 4. Publicaciones con etiquetas similares pero NINGÚN color similar
            etiquetas_similares_sin_colores AS (
                SELECT 
                    p.ID_publicacion,
                    4 AS prioridad,
                    COUNT(DISTINCT ep.descripcion) AS coincidencias_etiquetas,
                    SUM(ep.score) AS suma_scores_etiquetas,
                    0 AS coincidencias_colores,
                    0 AS suma_scores_colores,
                    0 AS coincidencias_categorias
                FROM Publicacion p
                JOIN Etiqueta_Publicacion ep ON p.ID_publicacion = ep.ID_publicacion
                JOIN etiquetas_referencia er ON ep.descripcion = er.descripcion
                WHERE p.ID_publicacion != (SELECT id_publicacion_referencia FROM constantes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM mismas_etiquetas_colores_similares)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM categorias_comunes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM etiquetas_colores_comunes)
                  AND NOT EXISTS (
                      SELECT 1 
                      FROM Color_Publicacion cp
                      JOIN colores_referencia cr ON 
                          ABS(cp.red - cr.red) <= (SELECT margen_color FROM constantes) AND
                          ABS(cp.green - cr.green) <= (SELECT margen_color FROM constantes) AND
                          ABS(cp.blue - cr.blue) <= (SELECT margen_color FROM constantes)
                      WHERE cp.ID_publicacion = p.ID_publicacion
                  )
                GROUP BY p.ID_publicacion
            ),

            -- 5. Publicaciones con colores similares pero NINGUNA etiqueta en común
            colores_similares_sin_etiquetas AS (
                SELECT 
                    p.ID_publicacion,
                    5 AS prioridad,
                    0 AS coincidencias_etiquetas,
                    0 AS suma_scores_etiquetas,
                    COUNT(DISTINCT cp.ID_color_publicacion) AS coincidencias_colores,
                    SUM(
                        (1 - (ABS(cp.red - cr.red)/255.0)) * 
                        (1 - (ABS(cp.green - cr.green)/255.0)) * 
                        (1 - (ABS(cp.blue - cr.blue)/255.0)) * 
                        ((cp.score + cr.score)/2)
                    ) AS suma_scores_colores,
                    0 AS coincidencias_categorias
                FROM Publicacion p
                JOIN Color_Publicacion cp ON p.ID_publicacion = cp.ID_publicacion
                JOIN colores_referencia cr ON 
                    ABS(cp.red - cr.red) <= (SELECT margen_color FROM constantes) AND
                    ABS(cp.green - cr.green) <= (SELECT margen_color FROM constantes) AND
                    ABS(cp.blue - cr.blue) <= (SELECT margen_color FROM constantes)
                WHERE p.ID_publicacion != (SELECT id_publicacion_referencia FROM constantes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM mismas_etiquetas_colores_similares)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM categorias_comunes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM etiquetas_colores_comunes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM etiquetas_similares_sin_colores)
                  AND NOT EXISTS (
                      SELECT 1 
                      FROM Etiqueta_Publicacion ep
                      JOIN etiquetas_referencia er ON ep.descripcion = er.descripcion
                      WHERE ep.ID_publicacion = p.ID_publicacion
                  )
                GROUP BY p.ID_publicacion
            ),

            -- 6. Otras publicaciones sin relación directa (ordenadas por fecha descendente)
            otras_publicaciones AS (
                SELECT 
                    p.ID_publicacion,
                    6 AS prioridad,
                    0 AS coincidencias_etiquetas,
                    0 AS suma_scores_etiquetas,
                    0 AS coincidencias_colores,
                    0 AS suma_scores_colores,
                    0 AS coincidencias_categorias,
                    p.Fecha_Publicacion
                FROM Publicacion p
                WHERE p.ID_publicacion != (SELECT id_publicacion_referencia FROM constantes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM mismas_etiquetas_colores_similares)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM categorias_comunes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM etiquetas_colores_comunes)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM etiquetas_similares_sin_colores)
                  AND p.ID_publicacion NOT IN (SELECT ID_publicacion FROM colores_similares_sin_etiquetas)
                ORDER BY p.Fecha_Publicacion DESC
            )

            -- Unir todos los resultados
            SELECT 
                p.ID_publicacion,
                p.Titulo_publicacion,
                p.Descripcion_publicacion,
                p.Img_publicacion,
                p.Cont_Explicit_publi,
                p.ID_usuario,
                r.prioridad,
                r.coincidencias_etiquetas,
                r.suma_scores_etiquetas,
                r.coincidencias_colores,
                r.suma_scores_colores,
                r.coincidencias_categorias,
                CASE r.prioridad
                    WHEN 1 THEN 'Mismas etiquetas y colores similares'
                    WHEN 2 THEN 'Mismas categorías'
                    WHEN 3 THEN 'Algunas etiquetas y colores similares'
                    WHEN 4 THEN 'Etiquetas similares sin colores similares'
                    WHEN 5 THEN 'Colores similares sin etiquetas'
                    WHEN 6 THEN 'Otras publicaciones'
                END AS tipo_recomendacion,
                p.Fecha_Publicacion
            FROM (
                SELECT ID_publicacion, prioridad, coincidencias_etiquetas, suma_scores_etiquetas, 
                    coincidencias_colores, suma_scores_colores, coincidencias_categorias, NULL AS Fecha_Publicacion 
                FROM mismas_etiquetas_colores_similares
                UNION ALL
                SELECT ID_publicacion, prioridad, coincidencias_etiquetas, suma_scores_etiquetas, 
                    coincidencias_colores, suma_scores_colores, coincidencias_categorias, NULL AS Fecha_Publicacion 
                FROM categorias_comunes
                UNION ALL
                SELECT ID_publicacion, prioridad, coincidencias_etiquetas, suma_scores_etiquetas, 
                    coincidencias_colores, suma_scores_colores, coincidencias_categorias, NULL AS Fecha_Publicacion 
                FROM etiquetas_colores_comunes
                UNION ALL
                SELECT ID_publicacion, prioridad, coincidencias_etiquetas, suma_scores_etiquetas, 
                    coincidencias_colores, suma_scores_colores, coincidencias_categorias, NULL AS Fecha_Publicacion 
                FROM etiquetas_similares_sin_colores
                UNION ALL
                SELECT ID_publicacion, prioridad, coincidencias_etiquetas, suma_scores_etiquetas, 
                    coincidencias_colores, suma_scores_colores, coincidencias_categorias, NULL AS Fecha_Publicacion 
                FROM colores_similares_sin_etiquetas
                UNION ALL
                SELECT ID_publicacion, prioridad, coincidencias_etiquetas, suma_scores_etiquetas, 
                    coincidencias_colores, suma_scores_colores, coincidencias_categorias, Fecha_Publicacion 
                FROM otras_publicaciones
            ) r
            JOIN Publicacion p ON p.ID_publicacion = r.ID_publicacion
            ORDER BY 
                r.prioridad,
                CASE WHEN r.prioridad = 6 THEN 0 ELSE 1 END,
                r.coincidencias_categorias DESC,
                r.coincidencias_etiquetas DESC,
                r.suma_scores_etiquetas DESC,
                r.suma_scores_colores DESC,
                r.coincidencias_colores DESC,
                CASE WHEN r.prioridad = 6 THEN p.Fecha_Publicacion ELSE NULL END DESC,
                CASE WHEN r.prioridad <> 6 THEN p.Fecha_Publicacion ELSE NULL END DESC
            """)

            # Ejecutar la consulta con parámetros
            result = db.session.execute(sql_query, {'id_publicacion_param': id_publicacion})
            
            # Convertir resultados a diccionario
            recomendaciones = []
            for row in result:
                recomendaciones.append({
                    'ID_publicacion': row.ID_publicacion,
                    'Titulo_publicacion': row.Titulo_publicacion,
                    'Descripcion_publicacion': row.Descripcion_publicacion,
                    'Cont_Explicit_publi': row.Cont_Explicit_publi,
                    'ID_usuario': row.ID_usuario,
                    'Img_publicacion': row.Img_publicacion,
                    'prioridad': row.prioridad,
                    'coincidencias_etiquetas': row.coincidencias_etiquetas,
                    'suma_scores_etiquetas': row.suma_scores_etiquetas,
                    'coincidencias_colores': row.coincidencias_colores,
                    'suma_scores_colores': row.suma_scores_colores,
                    'coincidencias_categorias': row.coincidencias_categorias,
                    'tipo_recomendacion': row.tipo_recomendacion,
                    'Fecha_Publicacion': row.Fecha_Publicacion.isoformat() if row.Fecha_Publicacion else None
                })

            return {'recomendaciones': recomendaciones}, 200

        except ValueError:
            return {'error': 'El ID de publicación debe ser un número válido'}, 400
        except Exception as e:
            db.session.rollback()
            print(f"Error al obtener recomendaciones: {str(e)}")
            return {'error': 'Error al obtener recomendaciones'}, 500
        

# esto sirve para sacar un conteo de las publicaciones y reacciones que tiene un usuario
class VistaEstadisticasUsuario(Resource):
    def get(self, id_usuario):
        try:
            # 1. Contar publicaciones del usuario
            total_publicaciones = db.session.query(func.count(Publicacion.ID_publicacion))\
                .filter(Publicacion.ID_usuario == id_usuario).scalar()

            # 2. Obtener IDs de las publicaciones del usuario
            ids_publicaciones = db.session.query(Publicacion.ID_publicacion)\
                .filter(Publicacion.ID_usuario == id_usuario).all()
            ids_publicaciones = [id_pub[0] for id_pub in ids_publicaciones]

            # 3. Contar reacciones en esas publicaciones
            if ids_publicaciones:
                total_reacciones = db.session.query(func.count(Publicacion_Reaccion.ID_reaccion))\
                    .filter(Publicacion_Reaccion.ID_publicacion.in_(ids_publicaciones)).scalar()
            else:
                total_reacciones = 0

            return {
                "ID_usuario": id_usuario,
                "total_publicaciones": total_publicaciones,
                "total_reacciones": total_reacciones
            }, 200

        except Exception as e:
            return {"error": f"Ocurrió un error al obtener las estadísticas: {str(e)}"}, 500
        

class Vista_Busqueda_publicaciones(Resource):
    def get(self):
        query = request.args.get('q', '').strip()
        tipo_busqueda = request.args.get('tipo', 'todo')  # 'todo', 'titulo', 'usuario', 'etiqueta', 'categoria'

        if not query:
            return jsonify([])

        try:
            if tipo_busqueda == 'titulo':
                publicaciones = Publicacion.query.filter(
                    Publicacion.Titulo_publicacion.ilike(f'%{query}%')
                ).all()
            elif tipo_busqueda == 'usuario':
                publicaciones = Publicacion.query.join(Usuario).filter(
                    Usuario.Nombre_usuario.ilike(f'%{query}%')
                ).all()
            elif tipo_busqueda == 'etiqueta':
                publicaciones = Publicacion.query.join(Etiqueta_Publicacion).filter(
                    Etiqueta_Publicacion.descripcion.ilike(f'%{query}%')
                ).all()
            elif tipo_busqueda == 'categoria':
                publicaciones = Publicacion.query.join(Publicacion_Categoria).join(Categoria).filter(
                    Categoria.Nombre_categoria.ilike(f'%{query}%')
                ).all()
            else:
                # Búsqueda general (en todos los campos)
                publicaciones = Publicacion.query\
                    .join(Usuario)\
                    .outerjoin(Etiqueta_Publicacion)\
                    .outerjoin(Publicacion_Categoria)\
                    .outerjoin(Categoria)\
                    .filter(
                        or_(
                            Publicacion.Titulo_publicacion.ilike(f'%{query}%'),
                            Usuario.Nombre_usuario.ilike(f'%{query}%'),
                            Etiqueta_Publicacion.descripcion.ilike(f'%{query}%'),
                            Categoria.Nombre_categoria.ilike(f'%{query}%')
                        )
                    ).all()

            resultados = []
            for pub in publicaciones:
                usuario = Usuario.query.get(pub.ID_usuario)
                resultados.append({
                    'ID_publicacion': pub.ID_publicacion,
                    'Titulo_publicacion': pub.Titulo_publicacion,
                    'Descripcion_publicacion': pub.Descripcion_publicacion,
                    'Img_publicacion': pub.Img_publicacion,
                    'Cont_Explicit_publi': pub.Cont_Explicit_publi,
                    'Fecha_Publicacion': pub.Fecha_Publicacion.isoformat(),
                    'usuario': {
                        'ID_usuario': usuario.ID_usuario,
                        'Nombre_usuario': usuario.Nombre_usuario,
                        'Img_usuario': usuario.Img_usuario
                    }
                })

            return jsonify(resultados)

        except Exception as e:
            print(f"Error en búsqueda: {str(e)}")
            return jsonify([])
