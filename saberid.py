import requests

token = "7932886224:AAFPA3yQrSxTwhUyKnqntIzE_rFdfX-p0dI"
url = f"https://api.telegram.org/bot{token}/getUpdates"
# Realizar la solicitud
response = requests.get(url)

# Verifica si la solicitud fue exitosa
if response.status_code == 200:
    data = response.json()
    print("Datos recibidos:")
    print(data)  # Esto te mostrará toda la respuesta de la API
    
    # Si hay mensajes, se extrae el chat_id
    if data['result']:
        chat_id = data['result'][0]['message']['chat']['id']
        print("chat_id:", chat_id)
    else:
        print("No se han recibido mensajes aún.")
else:
    print("Error en la solicitud:", response.status_code)

