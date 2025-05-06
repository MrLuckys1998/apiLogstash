import os
import time
import threading
import importlib.util
import traceback
from logger import logger

WATCHER_DIR = "generated"
CHECK_INTERVAL = 5  # Intervalo de chequeo en segundos

executing_watchers = {}

def run_periodically(path, interval, module_name, stop_event):
    def task():
        while not stop_event.is_set():
            try:
                logger.info(f"[RUNNING] {module_name}")
                spec = importlib.util.spec_from_file_location(module_name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.run()
            except Exception as e:
                logger.error(f"[ERROR] {module_name}: {e}\n{traceback.format_exc()}")
            stop_event.wait(interval)
    return threading.Thread(target=task, daemon=True)

def load_or_reload_watcher(path):
    filename = os.path.basename(path)
    module_name = os.path.splitext(filename)[0]
    mtime = os.path.getmtime(path)

    watcher_info = executing_watchers.get(module_name)

    if watcher_info:
        # Watcher ya cargado, ¿ha cambiado?
        if watcher_info["mtime"] != mtime:
            logger.info(f"[RELOADING] {module_name} ha cambiado, recargando...")
            watcher_info["stop_event"].set()  # Parar el thread anterior
            del executing_watchers[module_name]
        else:
            return  # No ha cambiado, no hacemos nada

    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        interval = getattr(module, "interval_seconds", 300)
        stop_event = threading.Event()
        t = run_periodically(path, interval, module_name, stop_event)
        t.start()
        executing_watchers[module_name] = {"thread": t, "path": path, "mtime": mtime, "stop_event": stop_event}
        logger.info(f"[STARTED] {filename} cada {interval}s")
    except Exception as e:
        logger.error(f"[FAILED] {filename} no se pudo iniciar: {e}")

def main():
    os.makedirs(WATCHER_DIR, exist_ok=True)
    logger.info("=== Orquestador V2 iniciado ===")

    while True:
        for file in os.listdir(WATCHER_DIR):
            if file.endswith(".py"):
                path = os.path.join(WATCHER_DIR, file)
                load_or_reload_watcher(path)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()