from flask_restful import Resource
from flask import request, jsonify
import os
import requests
from io import BytesIO
from google.cloud import vision
import tempfile
import json


credentials_json_str = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if not credentials_json_str:
    raise RuntimeError("La variable de entorno GOOGLE_CREDENTIALS_JSON no está definida")

with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_cred_file:
    temp_cred_file.write(credentials_json_str)
    temp_cred_file.flush()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_cred_file.name

client = vision.ImageAnnotatorClient()

class AnalizarImagen(Resource):
    def post(self):
        # Verificar si se envió una URL o un archivo
        if 'image_url' in request.json:
            image_url = request.json['image_url']
            try:
                response = requests.get(image_url)
                content = response.content
            except Exception as e:
                return jsonify({'error': f'No se pudo descargar la imagen: {str(e)}'}), 400
        elif 'imagen' in request.files:
            imagen = request.files['imagen']
            content = imagen.read()
        else:
            return jsonify({'error': 'Debe enviar una URL de imagen o un archivo de imagen'}), 400

        image = vision.Image(content=content)

        label_response = client.label_detection(image=image)
        labels = label_response.label_annotations

        label_data = sorted(
            [{
                'description': label.description,
                'score': round(label.score * 100, 2),
                'topicality': round(label.topicality * 100, 2)
            } for label in labels],
            key=lambda x: x['score'],
            reverse=True
        )[:5]

        color_response = client.image_properties(image=image)
        colors = color_response.image_properties_annotation.dominant_colors.colors

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
        )[:5]

        return jsonify({
            'labels': label_data,
            'colores': color_data
        })
