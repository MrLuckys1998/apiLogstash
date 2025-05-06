
# Watcher Generator & Orchestrator

Este proyecto permite generar y orquestar **watchers personalizados** que ejecutan consultas sobre Elasticsearch y emiten alertas vía webhook o Elasticsearch cuando se cumplen ciertas condiciones.

---

## 🧱 Estructura del Proyecto

```
.
├── generator_core.py            # Núcleo de generación de watchers (CLI y web)
├── watcher_web.py               # Interfaz web para generar watchers
├── watcher_orchestrator.py      # Orquestador que ejecuta los watchers periódicamente
├── utils.py                     # Funciones auxiliares (webhook + Elasticsearch)
├── logger.py                    # Logger centralizado
├── generated/                   # Watchers generados listos para ejecución
├── templates/                   # Plantillas Jinja2 + ejemplos JSON de configuración
└── generar_docs_pruebas.sh      # Script utilitario (personalizable)
```

---

## 🌐 Interfaz Web

Levantar con:

```bash
systemctl start Watcher-Web.service
```

Disponible en `(http://22.0.82.39:5000/)`

### Funcionalidades:
- Selección de plantilla
- Relleno dinámico de parámetros
- Selección de destino: webhook / Elasticsearch / ambos
- Payload personalizado
- Preview y confirmación

---

## ⚙️ Orquestador

Ejecuta automáticamente todos los watchers generados en la carpeta `generated/`, usando el campo `interval_seconds` definido en cada uno.

Levantar con:

```bash
systemctl start Watcher-Orquestador.servce
```

Levantado como servicio en systemd
---

## 📦 Plantillas disponibles

Cada plantilla se compone de:
- `nombre.py.j2`: código con placeholders Jinja2
- `nombre.example.json`: valores de ejemplo para autocompletar en la web

Lista actual:
- `avg_threshold`: alerta si el promedio de un campo supera umbral
- `min_threshold`: alerta si el mínimo es inferior a un valor
- `sum_threshold`: suma de campo mayor a x
- `count_threshold`: número de documentos que cumplen condición
- `missing_data`: índice sin datos en la última hora
- `field_value_missing`: campo esperado que no llega
- `ratio_between_fields`: errores / totales > umbral
- `multi_field_values`: múltiples campos con valores específicos
- `unique_terms_missing`: un valor único esperado no ha llegado

---

## 📤 Envío de Alertas

Las alertas pueden enviarse a:
- Webhook interno (JSON con campos configurables)
- Elasticsearch (índice configurable)
- Ambos simultáneamente

Configuración en `utils.py` y variables de entorno:

```bash
export WATCHER_WEBHOOK=https://miwebhook
export WATCHER_ELASTIC_URL=https://mi-elastic
export WATCHER_ELASTIC_INDEX=watcher-alerts
```

---

## 🧪 Logs

Todos los watchers y procesos (web/orquestador) escriben logs a `app.log` por defecto:

- Info de ejecución
- Alertas generadas
- Errores de conexión

---

## 📌 Requisitos

- Python 3.6+
- Elasticsearch (7.x o 8.x)
- Flask (`pip install flask`)
- Jinja2 (`pip install jinja2`)
- requests, elasticsearch (`pip install requests elasticsearch`)

---

## ✨ Siguientes pasos

- Añadir más plantillas según reglas de negocio
- Separar HTMLde Web.
- Autenticación en la interfaz web y auditoria.
- logs en Elastic

---

Desarrollado para automatizar alertas operativas basadas en datos en tiempo real de Elasticsearch.
