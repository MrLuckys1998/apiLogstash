# Importación de módulos necesarios
import os
# Importación de módulos necesarios
import requests
# Importación de módulos necesarios
from elasticsearch import Elasticsearch
# Importación de módulos necesarios
from logger import logger

# Configuración de webhooks por región
WEBHOOKS = {
    "ESP": "https://webhook.esp.local/alerta",
    "CL": "https://webhook.cl.local/alerta",
    "USA": "https://webhook.usa.local/alerta"
}

# Definir a qué índice se envía la alerta
ES_INDEX = os.getenv("WATCHER_ELASTIC_INDEX", "watcher-alerts")

# Definición de una función: send_webhook_alert
def send_webhook_alert(payload: dict, region: str = "ESP"):
    url = WEBHOOKS.get(region)
    if not url:
        logger.error(f"[WEBHOOK] Región no soportada: {region}")
        return
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"[WEBHOOK] Enviado a {region}: {url}")
    except Exception as e:
        logger.error(f"[WEBHOOK] Error enviando a {region}: {e}")

# Definición de una función: send_elasticsearch_alert
def send_elasticsearch_alert(payload: dict, es_url: str = "", user: str = "", password: str = ""):
    try:
        es = Elasticsearch(es_url, basic_auth=(user, password), verify_certs=False)
        es.index(index=ES_INDEX, body=payload)
        logger.info(f"[ELASTIC] Alerta enviada al índice {ES_INDEX}")
    except Exception as e:
        logger.error(f"[ELASTIC] Error enviando alerta: {e}")