from flask import Flask, request
import requests, datetime, hashlib, hmac, base64, json

import keys
from keys import *

app = Flask(__name__)

# Dados do seu workspace Sentinel
workspace_id = keys.workspareid
primary_key = keys.primarykey
log_type = 'WearOSData'

def build_signature(date, content_length):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    string_to_hash = f'{method}\n{content_length}\n{content_type}\nx-ms-date:{date}\n{resource}'
    bytes_to_hash = bytes(string_to_hash, 'utf-8')
    decoded_key = base64.b64decode(primary_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, hashlib.sha256).digest()).decode()
    return f'SharedKey {workspace_id}:{encoded_hash}'

@app.route('/wear', methods=['POST'])
def receive_data():
    body = request.get_data()

    # 👇 Adicione isso para imprimir os dados recebidos
    print("Dados recebidos do Wear OS:")
    print(body.decode("utf-8"))

    date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    signature = build_signature(date, len(body))

    headers = {
        'Content-Type': 'application/json',
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': date
    }

    url = f'https://{workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01'
    response = requests.post(url, data=body, headers=headers)

    # 👇 Adicione isso
    print("Código de resposta do Sentinel:", response.status_code)
    print("Texto de resposta do Sentinel:", response.text)
    return {'status': response.status_code}, response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
