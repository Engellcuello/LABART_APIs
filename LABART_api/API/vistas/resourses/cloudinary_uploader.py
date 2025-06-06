import requests
from requests.auth import HTTPBasicAuth

# Credenciales de la cuenta principal
# Credenciales de la cuenta de respaldo
PRIMARY_CLOUD_NAME = 'dgykc3yp5'
PRIMARY_PRESET_NAME = 'Imagenes_publicaciones'
PRIMARY_API_KEY = '665733994526989'
PRIMARY_API_SECRET = 'lB1U1-Sviw1Ijdy7ntPUC9oPtnA'


# Credenciales de la cuenta de respaldo
BACKUP_CLOUD_NAME = 'doperjl15'
BACKUP_PRESET_NAME = 'Imagenes_perfil'
SECONDARY_API_KEY = '579629149437376'
SECONDARY_API_SECRET = 'eOu4rXYCbSsJ9HSmKJKTyHwRrbE'

validacion = 0

def get_credit_usage(cloud_name, api_key, api_secret):
    url = f'https://api.cloudinary.com/v1_1/{cloud_name}/usage'
    response = requests.get(url, auth=HTTPBasicAuth(api_key, api_secret))
    
    if response.status_code == 200:
        usage_data = response.json()
        # Extraer el porcentaje de créditos usados (por ejemplo: 0.60%)
        validacion = usage_data.get("credits", {}).get("used_percent")
        print(validacion)
        print (usage_data)
        print(f"Uso de créditos de Cloudinary ({cloud_name}): {validacion}%")
        return validacion
    else:
        print(f"Error obteniendo el uso de créditos de la cuenta {cloud_name}: {response.status_code}")
        print(response.text)
        return 100  # Asume 100% si falla, para forzar el uso de respaldo

def upload_image_to_cloudinary(file):
    credit_percent = get_credit_usage(PRIMARY_CLOUD_NAME, PRIMARY_API_KEY, PRIMARY_API_SECRET)

    if float(credit_percent) >= 100:
        print("Créditos agotados. Usando cuenta de respaldo.")
        return _upload_image(file, BACKUP_CLOUD_NAME, BACKUP_PRESET_NAME, backup=False)
    else:
        return _upload_image(file, PRIMARY_CLOUD_NAME, PRIMARY_PRESET_NAME, backup=True)

def _upload_image(file, cloud_name, preset_name, backup):
    url = f'https://api.cloudinary.com/v1_1/{cloud_name}/image/upload'
    files = {'file': file}
    data = {'upload_preset': preset_name}

    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print(f'Imagen subida con éxito a {"respaldo" if not backup else "principal"} ({cloud_name})')
            print("Respuesta completa:")
            print(response.json())
            return response.json().get('secure_url')
        else:
            print(f'Error subiendo imagen a {cloud_name}:', response.text)
            if backup:
                print('Intentando con la cuenta de respaldo...')
                return _upload_image(file, BACKUP_CLOUD_NAME, BACKUP_PRESET_NAME, backup=False)
    except Exception as e:
        print(f'Error subiendo imagen ({cloud_name}):', e)
        if backup:
            print('Intentando con la cuenta de respaldo...')
            return _upload_image(file, BACKUP_CLOUD_NAME, BACKUP_PRESET_NAME, backup=False)

    return None