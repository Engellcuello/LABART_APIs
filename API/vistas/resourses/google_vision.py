from flask_restful import Resource
from flask import request, jsonify
import os
import requests
from io import BytesIO
from google.cloud import vision

# Autenticación con Google Vision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'ServiceAcountToken.json'
client = vision.ImageAnnotatorClient()

class AnalizarImagen(Resource):
    def post(self):
        # Verificar si se envió una URL o un archivo
        if 'image_url' in request.json:
            # Caso 1: Se envió una URL
            image_url = request.json['image_url']
            try:
                response = requests.get(image_url)
                content = response.content
            except Exception as e:
                return jsonify({'error': f'No se pudo descargar la imagen: {str(e)}'}), 400
        elif 'imagen' in request.files:
            # Caso 2: Se envió un archivo
            imagen = request.files['imagen']
            content = imagen.read()
        else:
            return jsonify({'error': 'Debe enviar una URL de imagen o un archivo de imagen'}), 400

        image = vision.Image(content=content)

        # -------- Etiquetas (labels) --------
        label_response = client.label_detection(image=image)
        labels = label_response.label_annotations

        # Ordenar por score descendente y tomar las 5 mejores
        label_data = sorted(
            [{
                'description': label.description,
                'score': round(label.score * 100, 2),
                'topicality': round(label.topicality * 100, 2)
            } for label in labels],
            key=lambda x: x['score'],
            reverse=True
        )[:5]  # Limitar a 5 etiquetas con mayor score

        # -------- Colores dominantes --------
        color_response = client.image_properties(image=image)
        colors = color_response.image_properties_annotation.dominant_colors.colors

        # Ordenar por pixel_fraction descendente y tomar los 5 mejores
        color_data = sorted(
            [{
                'red': int(color.color.red),
                'green': int(color.color.green),
                'blue': int(color.color.blue),
                'pixel_fraction': round(color.pixel_fraction * 100, 2),
                'score': round(color.score * 100, 2)
            } for color in colors],
            key=lambda x: x['pixel_fraction'],
            reverse=True
        )[:5]  # Limitar a 5 colores con mayor pixel_fraction

        return jsonify({
            'labels': label_data,
            'colores': color_data
        })