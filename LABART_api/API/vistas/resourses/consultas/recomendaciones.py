from sqlalchemy import func, case, literal_column, or_, and_, not_, text
from sqlalchemy.sql import label
from datetime import datetime
from API.modelos.modelos import db, Publicacion, Etiqueta_Publicacion, Color_Publicacion, Publicacion_Categoria, Categoria, Historial, Publicacion_Guardada, Usuario
from decimal import Decimal

class RecomendacionesHome:

    @staticmethod
    def decimal_to_float(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: RecomendacionesHome.decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [RecomendacionesHome.decimal_to_float(i) for i in obj]
        elif hasattr(obj, '__dict__'):
            return RecomendacionesHome.decimal_to_float(vars(obj))
        return obj

    @staticmethod
    def obtener_recomendaciones(user_id):
        """Ejecuta la consulta compleja de recomendaciones para un usuario específico"""
        
        # Primero verificar si el usuario tiene historial o publicaciones guardadas
        tiene_historial = db.session.query(Historial).filter(
            Historial.ID_usuario == user_id
        ).first() is not None

        tiene_guardados = db.session.query(Publicacion_Guardada).filter(
            Publicacion_Guardada.ID_usuario == user_id
        ).first() is not None

        # Si no tiene historial ni guardados, devolver todas las publicaciones ordenadas por fecha
        if not tiene_historial and not tiene_guardados:
            publicaciones = db.session.query(
                Publicacion.ID_publicacion,
                Publicacion.Titulo_publicacion,
                Publicacion.Descripcion_publicacion,
                Publicacion.Img_publicacion,
                Publicacion.Fecha_Publicacion,
                Publicacion.ID_usuario,
                Publicacion.Cont_Explicit_publi
            ).filter(
                Publicacion.ID_usuario != user_id
            ).order_by(
                Publicacion.Fecha_Publicacion.desc()
            ).all()

            resultados = [{
                'ID_publicacion': p.ID_publicacion,
                'Titulo_publicacion': p.Titulo_publicacion,
                'Descripcion_publicacion': p.Descripcion_publicacion,
                'Img_publicacion': p.Img_publicacion,
                'idUsuario': p.ID_usuario,
                'esExplicita': p.Cont_Explicit_publi,
                'Fecha_Publicacion': p.Fecha_Publicacion.isoformat(),
                'puntaje_total': 0,
                'detalle_puntajes': {
                    'etiquetas_exactas': 0,
                    'etiquetas_parciales': 0,
                    'colores_exactos': 0,
                    'colores_similares': 0,
                    'categorias_exactas': 0,
                    'categorias_relacionadas': 0,
                    'recencia': (datetime.now() - p.Fecha_Publicacion).total_seconds() / 3600
                }
            } for p in publicaciones]

            return RecomendacionesHome.decimal_to_float(resultados)

        # Subconsulta para publicaciones ya vistas por el usuario
        publicaciones_vistas = db.session.query(Historial.ID_publicacion).filter(
            Historial.ID_usuario == user_id
        ).subquery()

        # Subconsulta para publicaciones guardadas por el usuario
        publicaciones_guardadas = db.session.query(Publicacion_Guardada.ID_publicacion).filter(
            Publicacion_Guardada.ID_usuario == user_id
        ).subquery()

        # Obtener etiquetas del usuario (de historial y guardados)
        user_etiquetas = db.session.query(
            Etiqueta_Publicacion.descripcion.label('etiqueta_desc'),
            func.count(Etiqueta_Publicacion.descripcion).label('frecuencia')
        ).join(
            Historial, Historial.ID_publicacion == Etiqueta_Publicacion.ID_publicacion
        ).filter(
            Historial.ID_usuario == user_id
        ).group_by(
            Etiqueta_Publicacion.descripcion
        ).union_all(
            db.session.query(
                Etiqueta_Publicacion.descripcion.label('etiqueta_desc'),
                func.count(Etiqueta_Publicacion.descripcion).label('frecuencia')
            ).join(
                Publicacion_Guardada, Publicacion_Guardada.ID_publicacion == Etiqueta_Publicacion.ID_publicacion
            ).filter(
                Publicacion_Guardada.ID_usuario == user_id
            ).group_by(
                Etiqueta_Publicacion.descripcion
            )
        ).subquery()

        etiquetas_frecuentes = db.session.query(
            user_etiquetas.c.etiqueta_desc,
            func.sum(user_etiquetas.c.frecuencia).label('frecuencia_total')
        ).group_by(
            user_etiquetas.c.etiqueta_desc
        ).all()  # Obtenemos los resultados aquí para usarlos en la condición

        # Construir condiciones para etiquetas
        condiciones_etiquetas = []
        for etiqueta in etiquetas_frecuentes:
            condiciones_etiquetas.append(Etiqueta_Publicacion.descripcion.like(f"%{etiqueta.etiqueta_desc}%"))

        # Obtener colores del usuario
        user_colores = db.session.query(
            Color_Publicacion.red.label('color_r'),
            Color_Publicacion.green.label('color_g'),
            Color_Publicacion.blue.label('color_b'),
            func.count(Color_Publicacion.ID_color_publicacion).label('frecuencia')
        ).join(
            Historial, Historial.ID_publicacion == Color_Publicacion.ID_publicacion
        ).filter(
            Historial.ID_usuario == user_id
        ).group_by(
            Color_Publicacion.red, Color_Publicacion.green, Color_Publicacion.blue
        ).union_all(
            db.session.query(
                Color_Publicacion.red.label('color_r'),
                Color_Publicacion.green.label('color_g'),
                Color_Publicacion.blue.label('color_b'),
                func.count(Color_Publicacion.ID_color_publicacion).label('frecuencia')
            ).join(
                Publicacion_Guardada, Publicacion_Guardada.ID_publicacion == Color_Publicacion.ID_publicacion
            ).filter(
                Publicacion_Guardada.ID_usuario == user_id
            ).group_by(
                Color_Publicacion.red, Color_Publicacion.green, Color_Publicacion.blue
            )
        ).subquery()

        colores_frecuentes = db.session.query(
            user_colores.c.color_r,
            user_colores.c.color_g,
            user_colores.c.color_b,
            func.sum(user_colores.c.frecuencia).label('frecuencia_total')
        ).group_by(
            user_colores.c.color_r, user_colores.c.color_g, user_colores.c.color_b
        ).subquery()

        # Obtener categorías del usuario
        user_categorias = db.session.query(
            Publicacion_Categoria.ID_categoria.label('categoria_id'),
            func.count(Publicacion_Categoria.ID_categoria).label('frecuencia')
        ).join(
            Historial, Historial.ID_publicacion == Publicacion_Categoria.ID_publicacion
        ).filter(
            Historial.ID_usuario == user_id
        ).group_by(
            Publicacion_Categoria.ID_categoria
        ).union_all(
            db.session.query(
                Publicacion_Categoria.ID_categoria.label('categoria_id'),
                func.count(Publicacion_Categoria.ID_categoria).label('frecuencia')
            ).join(
                Publicacion_Guardada, Publicacion_Guardada.ID_publicacion == Publicacion_Categoria.ID_publicacion
            ).filter(
                Publicacion_Guardada.ID_usuario == user_id
            ).group_by(
                Publicacion_Categoria.ID_categoria
            )
        ).subquery()

        categorias_frecuentes = db.session.query(
            user_categorias.c.categoria_id,
            func.sum(user_categorias.c.frecuencia).label('frecuencia_total')
        ).group_by(
            user_categorias.c.categoria_id
        ).subquery()

        # Consulta principal para obtener recomendaciones
        query = db.session.query(
            Publicacion.ID_publicacion,
            Publicacion.Titulo_publicacion,
            Publicacion.Descripcion_publicacion,
            Publicacion.Img_publicacion,
            Publicacion.Fecha_Publicacion,
            Publicacion.ID_usuario,
            Publicacion.Cont_Explicit_publi,
            
            func.count(Etiqueta_Publicacion.ID_etiqueta_publicacion).label('puntaje_etiquetas_exactas'),

            # Versión corregida del CASE - manejo explícito de lista vacía
            func.sum(
                case(
                    *[(or_(*condiciones_etiquetas), 5)] if condiciones_etiquetas else [(literal_column('1'), 0)],
                    else_=0
                )
            ).label('puntaje_etiquetas_parciales'),

            func.count(Color_Publicacion.ID_color_publicacion).label('puntaje_colores_exactos'),
            
            literal_column("0").label('puntaje_colores_similares'),
            literal_column("0").label('puntaje_categorias_exactas'),
            literal_column("0").label('puntaje_categorias_relacionadas'),

            func.timestampdiff(text('HOUR'), Publicacion.Fecha_Publicacion, func.now()).label('horas_desde_publicacion')
        ).outerjoin(
            Etiqueta_Publicacion, Etiqueta_Publicacion.ID_publicacion == Publicacion.ID_publicacion
        ).outerjoin(
            Color_Publicacion, Color_Publicacion.ID_publicacion == Publicacion.ID_publicacion
        ).filter(
            not_(Publicacion.ID_publicacion.in_(publicaciones_vistas)),
            Publicacion.ID_usuario != user_id
        ).group_by(
            Publicacion.ID_publicacion,
            Publicacion.Titulo_publicacion,
            Publicacion.Descripcion_publicacion,
            Publicacion.Img_publicacion,
            Publicacion.Fecha_Publicacion,
            Publicacion.ID_usuario,
            Publicacion.Cont_Explicit_publi
        )

        # Ordenamiento - Versión corregida
        if condiciones_etiquetas:
            query = query.order_by(
                (func.coalesce(
                    func.sum(
                        case(
                            (or_(*condiciones_etiquetas), 5),
                            else_=0
                        )
                    ), 
                    0
                ) + func.coalesce(func.count(), 0)).desc(),
                Publicacion.Fecha_Publicacion.desc()
            )
        else:
            query = query.order_by(Publicacion.Fecha_Publicacion.desc())


        recomendaciones = query.all()
        # Convertir resultados a diccionario
        resultados = []
        for rec in recomendaciones:
            puntaje_total = (
                rec.puntaje_etiquetas_exactas +
                rec.puntaje_etiquetas_parciales +
                rec.puntaje_colores_exactos +
                rec.puntaje_colores_similares +
                rec.puntaje_categorias_exactas +
                rec.puntaje_categorias_relacionadas
            )
            
            resultados.append({
                'ID_publicacion': rec.ID_publicacion,
                'Titulo_publicacion': rec.Titulo_publicacion,
                'Descripcion_publicacion': rec.Descripcion_publicacion,
                'Img_publicacion': rec.Img_publicacion,
                'idUsuario': rec.ID_usuario,
                'esExplicita': rec.Cont_Explicit_publi,
                'Fecha_Publicacion': rec.Fecha_Publicacion.isoformat(),
                'puntaje_total': puntaje_total,
                'detalle_puntajes': {
                    'etiquetas_exactas': rec.puntaje_etiquetas_exactas,
                    'etiquetas_parciales': rec.puntaje_etiquetas_parciales,
                    'colores_exactos': rec.puntaje_colores_exactos,
                    'colores_similares': rec.puntaje_colores_similares,
                    'categorias_exactas': rec.puntaje_categorias_exactas,
                    'categorias_relacionadas': rec.puntaje_categorias_relacionadas,
                    'recencia': rec.horas_desde_publicacion
                }
            })

        # Si no hay recomendaciones con puntaje, devolver todas las publicaciones no vistas
        if not resultados:
            publicaciones = db.session.query(
                Publicacion.ID_publicacion,
                Publicacion.Titulo_publicacion,
                Publicacion.Descripcion_publicacion,
                Publicacion.Img_publicacion,
                Publicacion.Fecha_Publicacion,
                Publicacion.ID_usuario,
                Publicacion.Cont_Explicit_publi
            ).filter(
                not_(Publicacion.ID_publicacion.in_(publicaciones_vistas)),
                Publicacion.ID_usuario != user_id
            ).order_by(
                Publicacion.Fecha_Publicacion.desc()
            ).all()

            resultados = [{
                'ID_publicacion': p.ID_publicacion,
                'Titulo_publicacion': p.Titulo_publicacion,
                'Descripcion_publicacion': p.Descripcion_publicacion,
                'Img_publicacion': p.Img_publicacion,
                'idUsuario': p.ID_usuario,
                'esExplicita': p.Cont_Explicit_publi,
                'Fecha_Publicacion': p.Fecha_Publicacion.isoformat(),
                'puntaje_total': 0,
                'detalle_puntajes': {
                    'etiquetas_exactas': 0,
                    'etiquetas_parciales': 0,
                    'colores_exactos': 0,
                    'colores_similares': 0,
                    'categorias_exactas': 0,
                    'categorias_relacionadas': 0,
                    'recencia': (datetime.now() - p.Fecha_Publicacion).total_seconds() / 3600
                }
            } for p in publicaciones]

        # Aplicar diversificación controlada (10% aleatorias) si hay suficientes resultados
        total_recomendaciones = len(resultados)
        if total_recomendaciones > 10:
            num_aleatorias = max(1, int(total_recomendaciones * 0.1))
            
            aleatorias = db.session.query(
                Publicacion.ID_publicacion,
                Publicacion.Titulo_publicacion,
                Publicacion.Descripcion_publicacion,
                Publicacion.Img_publicacion,
                Publicacion.Fecha_Publicacion,
                Publicacion.ID_usuario,
                Publicacion.Cont_Explicit_publi
            ).join(
                Usuario, Usuario.ID_usuario == Publicacion.ID_usuario
            ).filter(
                not_(Publicacion.ID_publicacion.in_([r['ID_publicacion'] for r in resultados])),
                not_(Publicacion.ID_publicacion.in_(publicaciones_vistas)),
                Publicacion.ID_usuario != user_id,
                or_(
                    Publicacion.Cont_Explicit_publi == False,
                    and_(
                        Publicacion.Cont_Explicit_publi == True,
                        Usuario.Cont_Explicit == True
                    )
                )
            ).order_by(
                func.random()
            ).limit(num_aleatorias).all()

            for aleatoria in aleatorias:
                resultados.append({
                    'ID_publicacion': aleatoria.ID_publicacion,
                    'Titulo_publicacion': aleatoria.Titulo_publicacion,
                    'esExplicita': aleatoria.Cont_Explicit_publi,
                    'idUsuario': aleatoria.ID_usuario,
                    'Descripcion_publicacion': aleatoria.Descripcion_publicacion,
                    'Img_publicacion': aleatoria.Img_publicacion,
                    'Fecha_Publicacion': aleatoria.Fecha_Publicacion.isoformat(),
                    'puntaje_total': 0,
                    'detalle_puntajes': {
                        'etiquetas_exactas': 0,
                        'etiquetas_parciales': 0,
                        'colores_exactos': 0,
                        'colores_similares': 0,
                        'categorias_exactas': 0,
                        'categorias_relacionadas': 0,
                        'recencia': (datetime.now() - aleatoria.Fecha_Publicacion).total_seconds() / 3600
                    }
                })
                    
        return RecomendacionesHome.decimal_to_float(resultados)