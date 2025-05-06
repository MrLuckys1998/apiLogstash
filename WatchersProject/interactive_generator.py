# Importación de módulos necesarios
from generator_core import generate_watcher
# Importación de módulos necesarios
import json
# Importación de módulos necesarios
import os

TEMPLATES = {
    "1": ("missing_data.py.j2", ["index", "timestamp_field", "elastic_url"]),
    "2": ("avg_threshold.py.j2", ["index", "timestamp_field", "target_field", "threshold", "elastic_url"]),
    "3": ("field_value_match.py.j2", ["index", "timestamp_field", "conditions", "elastic_url"]),
}

os.makedirs("generated", exist_ok=True)

# Definición de una función: prompt
def prompt():
    print("Crear watcher")
    name = input("Nombre: ")
    for k, (tpl, _) in TEMPLATES.items():
        print(f"{k}) {tpl}")
    choice = input("Elegí plantilla: ").strip()
    tpl_file, fields = TEMPLATES.get(choice, (None, None))
    if not tpl_file:
        print("Opción inválida.")
        return

    interval = int(input("Intervalo (segundos): "))
    webhook = input("¿Webhook? (s/n): ").lower() == 's'
    elastic = input("¿Elasticsearch? (s/n): ").lower() == 's'

    params = {}
    for field in fields:
        if field == "conditions":
            conds = []
            while True:
                f = input("Campo: ")
                v = input("Valor: ")
                conds.append({"field": f, "value": v})
                if input("¿Otro? (s/n): ").lower() != 's':
                    break
            params[field] = conds
        elif field == "threshold":
            params[field] = int(input(f"{field}: "))
        else:
            params[field] = input(f"{field}: ")

    payload = {}
    if webhook or elastic:
        print("Definí el payload JSON (lo que se enviará a Webhook/Elastic)")
        payload_str = input("Payload JSON (ej: {\"1\":\"alert\",\"2\":\"msg\",\"9\":\"" + name + "\"}): ")
        try:
            payload = json.loads(payload_str)
        except Exception:
            print("JSON inválido. Se usará uno por defecto.")
            payload = {"1": "alert", "2": "default", "9": name}

    path = generate_watcher(
        name=name,
        template_name=tpl_file,
        params=params,
        interval_seconds=interval,
        webhook_enabled=webhook,
        elastic_enabled=elastic,
        payload=payload
    )
    print(f"Watcher generado: {path}")

while True:
    prompt()
    if input("¿Crear otro? (s/n): ").lower() != 's':
        break