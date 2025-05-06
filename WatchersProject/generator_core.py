import os
import json
from jinja2 import Environment, FileSystemLoader
from logger import logger

TEMPLATE_PATH = "templates"
GENERATED_PATH = "generated"

env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))

def generate_watcher(
    name: str,
    template_name: str,
    params: dict,
    interval_seconds: int = 300,
    webhook_enabled: bool = False,
    elastic_enabled: bool = False,
    payload: dict = None,
    webhook_region: str = "ESP",
    custom_condition: str = "",
    preview_mode: bool = False
):
    os.makedirs(GENERATED_PATH, exist_ok=True)

    if payload is None:
        payload = {}

    # --- Imports automáticos ---
    imports = "from logger import logger\n"
    if webhook_enabled:
        imports += "from utils import send_webhook_alert\n"
    if elastic_enabled:
        imports += "from utils import send_elasticsearch_alert\n"

    # --- Cargar la plantilla ---
    template = env.get_template(template_name)
    if "custom_condition" in template.module.__dict__:
        params["custom_condition"] = custom_condition

    rendered = template.render(params)
    lines = rendered.splitlines()

    new_lines = []
    for line in lines:
        new_lines.append(line)
        stripped = line.strip()
        if stripped.startswith("# Webhooks"): 
            indent = line[:len(line) - len(line.lstrip())]
            if webhook_enabled:
                payload_str = json.dumps(payload.get("webhook") or {"message": "Webhook alert"}, ensure_ascii=False)
                new_lines.append(f"{indent}send_webhook_alert({payload_str}, region='{webhook_region}')")
            if elastic_enabled:
                payload_str = json.dumps(payload.get("elastic") or {"message": "Elastic alert"}, ensure_ascii=False)
                new_lines.append(f"{indent}send_elasticsearch_alert({payload_str}, es_url=elastic_url, user=elastic_user, password=elastic_pass)")

    # --- Construir el watcher final ---
    full_code = f"interval_seconds = {interval_seconds}\n{imports}\n" + "\n".join(new_lines)

    if preview_mode:
        logger.info(f"[PREVIEW] Watcher: {name} | plantilla: {template_name}")
        return full_code

    path = os.path.join(GENERATED_PATH, f"{name}.py")
    with open(path, "w") as f:
        f.write(full_code)

    logger.info(f"Watcher generado: {path} | plantilla: {template_name} | interval: {interval_seconds}s")
    return path