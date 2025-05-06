# Importación de módulos necesarios
import os
# Importación de módulos necesarios
import logging

# Ruta absoluta donde está este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carpeta de logs junto a watcher_web.py
LOG_DIR = os.path.join(BASE_DIR, "Logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("watcher_logger")

if not logger.hasHandlers():
    logger.setLevel(logging.INFO)

    file_path = os.path.join(LOG_DIR, "app.log")
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    logger.info(f"Logger inicializado correctamente. Escribiendo en: {file_path}")