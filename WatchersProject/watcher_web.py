from flask import Flask, request, render_template_string, redirect
import os
import json
from generator_core import generate_watcher
from logger import logger

app = Flask(__name__)

TEMPLATE_DIR = "templates"
GENERATED_DIR = "generated"
EXAMPLE_SUFFIX = ".example.json"

CLUSTERS = {
    "Cluster-1": {"url": "https://wtslcccelkp0050.unix.wtes.corp:9200", "user": "admin", "pass": "temporal"},
    "Cluster-2": {"url": "https://wtslcccelkp0050.unix.wtes.corp:9200", "user": "admin", "pass": "temporal"}
}

WEBHOOKS = {
    "ESP": "https://webhook.esp/alert",
    "CL": "https://webhook.cl/alert",
    "USA": "https://webhook.usa/alert"
}

def load_templates():
    return [f for f in os.listdir(TEMPLATE_DIR) if f.endswith(".py.j2")]

def load_example(template_name):
    base_name = template_name.replace(".py.j2", "")
    path = os.path.join(TEMPLATE_DIR, base_name + EXAMPLE_SUFFIX)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Generador de Watchers</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-5">
  <h2 class="mb-4">Generador de Watchers</h2>

  {% if error %}
    <div class="alert alert-danger">{{ error }}</div>
  {% endif %}

  {% if watcher_list %}
    <div class="alert alert-info"><strong>Watchers disponibles:</strong><br>{{ watcher_list|safe }}</div>
  {% endif %}

  {% if cat_result %}
    <div class="alert alert-secondary"><strong>Contenido del watcher:</strong>
      <pre>{{ cat_result }}</pre>
    </div>
  {% endif %}

  {% if preview %}
    <h5>Código generado (previsualización):</h5>
    <pre class="bg-dark text-light p-3 rounded">{{ preview }}</pre>
    <form method="post">
      <input type="hidden" name="confirm" value="1">
      {% for key, value in hidden_fields.items() %}
        <input type="hidden" name="{{ key }}" value="{{ value|e }}">
      {% endfor %}
      <button class="btn btn-success" type="submit">Confirmar creación</button>
      <a href="/" class="btn btn-secondary">Cancelar</a>
    </form>
    <hr>
  {% endif %}

  <form method="post" class="bg-white p-4 rounded shadow-sm">
    <input type="hidden" name="template" value="{{ selected_template }}">

    <div class="mb-3">
      <label class="form-label">Plantilla</label>
      <select class="form-select" onchange="location.href='/?template=' + this.value">
        {% for tpl in templates %}
          <option value="{{ tpl }}" {% if tpl == selected_template %}selected{% endif %}>{{ tpl }}</option>
        {% endfor %}
      </select>
    </div>

    <div class="row mb-3">
      <div class="col">
        <label class="form-label">Nombre del watcher</label>
        <input name="name" class="form-control" value="{{ name }}">
      </div>
      <div class="col">
        <label class="form-label">Intervalo (segundos)</label>
        <input name="interval" type="number" value="{{ interval }}" class="form-control" required>
      </div>
      <div class="col">
        <label class="form-label">Cluster</label>
        <select name="cluster" class="form-select">
          {% for key in clusters.keys() %}
            <option value="{{ key }}" {% if selected_cluster == key %}selected{% endif %}>{{ key }}</option>
          {% endfor %}
        </select>
      </div>
    </div>

    <div class="mb-3">
      <label class="form-label">Región Webhook</label>
      <select name="webhook_region" class="form-select">
        {% for region in webhook_regions %}
          <option value="{{ region }}" {% if selected_webhook_region == region %}selected{% endif %}>{{ region }}</option>
        {% endfor %}
      </select>
    </div>

    {% if selected_template == "custom_query.py.j2" %}
    <div class="mb-3">
      <label class="form-label">Condition Script</label>
      <textarea name="condition_script" class="form-control" rows="6">{% if condition_script %}{{ condition_script }}{% else %}if result['hits']['total']['value'] > 0 : {% endif %}</textarea>
    </div>
    {% endif %}

    <div class="mb-3">
      <label class="form-label">Parámetros JSON de la plantilla</label>
      <textarea name="params" class="form-control" rows="8">{{ json_params }}</textarea>
    </div>

    <div class="form-check mb-2">
      <input type="checkbox" name="webhook" class="form-check-input" id="webhook" {% if webhook %}checked{% endif %}>
      <label for="webhook" class="form-check-label">Enviar a Webhook</label>
    </div>

    <div class="form-check mb-3">
      <input type="checkbox" name="elastic" class="form-check-input" id="elastic" {% if elastic %}checked{% endif %}>
      <label for="elastic" class="form-check-label">Enviar a Elasticsearch</label>
    </div>

    <div class="mb-3">
      <label class="form-label">Payload Webhook (JSON)</label>
      <textarea name="alert_payload_webhook" class="form-control" rows="4">{{ alert_payload_webhook }}</textarea>
    </div>

    <div class="mb-3">
      <label class="form-label">Payload Elasticsearch (JSON)</label>
      <textarea name="alert_payload_elastic" class="form-control" rows="4">{{ alert_payload_elastic }}</textarea>
    </div>

    <button class="btn btn-primary" name="preview" value="1">Previsualizar</button>
    <button class="btn btn-outline-info" name="list_watchers" value="1">Listar Watchers</button>
    <div class="mt-3">
      <label class="form-label">Ver contenido de watcher</label>
      <div class="input-group">
        <input type="text" name="cat_name" class="form-control" placeholder="ej: my_watcher.py">
        <button class="btn btn-outline-secondary" name="cat" value="1">Mostrar</button>
      </div>
    </div>
  </form>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    templates = load_templates()
    selected_template = request.args.get("template") or request.form.get("template") or templates[0]
    default_params = load_example(selected_template)

    name = ""
    interval = "300"
    webhook = False
    elastic = False
    selected_cluster = "Cluster-1"
    selected_webhook_region = "ESP"
    webhook_payload = ""
    elastic_payload = ""
    json_params = json.dumps(default_params, indent=2)
    watcher_list, cat_result, error, preview = None, None, None, None
    condition_script = ""

    created = request.args.get("created")
    if created:
        watcher_list = f"Watcher creado: {created}"

    if request.method == "POST":
        if request.form.get("list_watchers") == "1":
            try:
                files = os.listdir(GENERATED_DIR)
                py_files = [f for f in files if f.endswith(".py")]
                watcher_list = "<br>".join(py_files)
                return render_template_string(HTML, templates=templates, selected_template=selected_template,
                                              json_params=json_params, webhook=webhook, elastic=elastic,
                                              alert_payload_webhook=webhook_payload, alert_payload_elastic=elastic_payload,
                                              error=error, name=name, interval=interval, clusters=CLUSTERS,
                                              selected_cluster=selected_cluster, webhook_regions=WEBHOOKS.keys(),
                                              selected_webhook_region=selected_webhook_region,
                                              watcher_list=watcher_list, cat_result=cat_result)
            except Exception as e:
                error = f"Error listando watchers: {e}"

        elif request.form.get("cat") == "1":
            try:
                cat_name = request.form.get("cat_name", "").strip()
                full_path = os.path.join(GENERATED_DIR, cat_name)
                if os.path.exists(full_path):
                    with open(full_path) as f:
                        cat_result = f.read()
                else:
                    error = "Watcher no encontrado."
            except Exception as e:
                error = f"Error leyendo watcher: {e}"

        elif request.form.get("preview") == "1":
            try:
                name = request.form.get("name", "")
                interval = request.form.get("interval", "300")
                webhook = "webhook" in request.form
                elastic = "elastic" in request.form
                selected_cluster = request.form.get("cluster", "Cluster-1")
                selected_webhook_region = request.form.get("webhook_region", "ESP")
                webhook_payload = request.form.get("alert_payload_webhook", "")
                elastic_payload = request.form.get("alert_payload_elastic", "")
                json_params = request.form.get("params", json.dumps(default_params, indent=2))
                condition_script = request.form.get("condition_script", "")

                if not name:
                    error = "El campo 'Nombre del watcher' es obligatorio."
                    return render_template_string(HTML, templates=templates, selected_template=selected_template,
                                                  json_params=json_params, webhook=webhook, elastic=elastic,
                                                  alert_payload_webhook=webhook_payload, alert_payload_elastic=elastic_payload,
                                                  error=error, name=name, interval=interval, clusters=CLUSTERS,
                                                  selected_cluster=selected_cluster, webhook_regions=WEBHOOKS.keys(),
                                                  selected_webhook_region=selected_webhook_region,
                                                  watcher_list=watcher_list, cat_result=cat_result)

                params = json.loads(json_params)
                cluster_info = CLUSTERS[selected_cluster]
                webhook_url = WEBHOOKS[selected_webhook_region]

                params.update({
                    "elastic_url": cluster_info["url"],
                    "elastic_user": cluster_info["user"],
                    "elastic_pass": cluster_info["pass"],
                    "webhook_url": webhook_url
                })

                if selected_template == "custom_query.py.j2":
                    params["condition_script"] = condition_script

                webhook_payload_data = json.loads(webhook_payload) if webhook_payload.strip() else {}
                elastic_payload_data = json.loads(elastic_payload) if elastic_payload.strip() else {}

                preview = generate_watcher(
                    name=name,
                    template_name=selected_template,
                    params=params,
                    interval_seconds=int(interval),
                    webhook_enabled=webhook,
                    elastic_enabled=elastic,
                    payload={
                        "webhook": webhook_payload_data,
                        "elastic": elastic_payload_data
                    },
                    webhook_region=selected_webhook_region,
                    preview_mode=True
                )

                hidden_fields = {
                    "template": selected_template,
                    "name": name,
                    "interval": interval,
                    "params": json.dumps(params),
                    "webhook": "1" if webhook else "",
                    "elastic": "1" if elastic else "",
                    "alert_payload_webhook": webhook_payload,
                    "alert_payload_elastic": elastic_payload,
                    "cluster": selected_cluster,
                    "webhook_region": selected_webhook_region,
                    "condition_script": condition_script
                }

                return render_template_string(HTML, templates=templates, selected_template=selected_template,
                                              json_params=json.dumps(params, indent=2), webhook=webhook,
                                              elastic=elastic, alert_payload_webhook=webhook_payload,
                                              alert_payload_elastic=elastic_payload, preview=preview,
                                              hidden_fields=hidden_fields, name=name, interval=interval,
                                              clusters=CLUSTERS, selected_cluster=selected_cluster,
                                              webhook_regions=WEBHOOKS.keys(),
                                              selected_webhook_region=selected_webhook_region,
                                              condition_script=condition_script)

            except Exception as e:
                error = f"Error al previsualizar: {e}"
                logger.error(error)

        elif request.form.get("confirm") == "1":
            try:
                params = json.loads(request.form.get("params", "{}"))
                name = request.form.get("name", "")
                interval = int(request.form.get("interval", "300"))
                selected_template = request.form.get("template")
                selected_cluster = request.form.get("cluster", "Cluster-1")
                selected_webhook_region = request.form.get("webhook_region", "ESP")
                webhook = request.form.get("webhook", "") == "1"
                elastic = request.form.get("elastic", "") == "1"
                webhook_payload = request.form.get("alert_payload_webhook", "")
                elastic_payload = request.form.get("alert_payload_elastic", "")
                condition_script = request.form.get("condition_script", "")

                cluster_info = CLUSTERS[selected_cluster]
                params.update({
                    "elastic_url": cluster_info["url"],
                    "elastic_user": cluster_info["user"],
                    "elastic_pass": cluster_info["pass"],
                    "webhook_url": WEBHOOKS[selected_webhook_region]
                })

                if selected_template == "custom_query.py.j2":
                    params["condition_script"] = condition_script

                payload = {
                    "webhook": json.loads(webhook_payload) if webhook_payload.strip() else {},
                    "elastic": json.loads(elastic_payload) if elastic_payload.strip() else {}
                }

                path = generate_watcher(
                    name=name,
                    template_name=selected_template,
                    params=params,
                    interval_seconds=interval,
                    webhook_enabled=webhook,
                    elastic_enabled=elastic,
                    payload=payload,
                    webhook_region=selected_webhook_region,
                    preview_mode=False
                )

                return redirect(f"/?created={os.path.basename(path)}")

            except Exception as e:
                error = f"Error al generar el watcher: {e}"
                logger.error(error)

    return render_template_string(HTML, templates=templates, selected_template=selected_template,
                                  json_params=json_params, webhook=webhook, elastic=elastic,
                                  alert_payload_webhook=webhook_payload, alert_payload_elastic=elastic_payload,
                                  error=error, name=name, interval=interval, clusters=CLUSTERS,
                                  selected_cluster=selected_cluster, webhook_regions=WEBHOOKS.keys(),
                                  selected_webhook_region=selected_webhook_region,
                                  watcher_list=watcher_list, cat_result=cat_result,
                                  condition_script=condition_script)

if __name__ == "__main__":
    os.makedirs(GENERATED_DIR, exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)