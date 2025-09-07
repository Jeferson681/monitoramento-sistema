import os
import json
from datetime import datetime
from src.config.settings import DATE_STR
from src.core.monitor import formatar_metricas, metricas
from src.services.helpers import log_verbose, timestamp
from src.services.utils import enviar_email_alerta


# Absolute path to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Subdirectory for JSON logs
LOGS_JSON_DIR = os.path.join(LOGS_DIR, "json")
os.makedirs(LOGS_JSON_DIR, exist_ok=True)

# Subdirectory for text logs
LOGS_TEXT_DIR = os.path.join(LOGS_DIR, "log")
os.makedirs(LOGS_TEXT_DIR, exist_ok=True)

LOG_JSON_FILE = os.path.join(LOGS_JSON_DIR, f"log_metricas_{DATE_STR}.jsonl")
LOG_FILE = os.path.join(LOGS_TEXT_DIR, f"log_{DATE_STR}.log")

#  Registra evento completo: log, console, e-mail (se ativado)
def registrar_evento(tipo, componente, valor, limite, args, mensagem):
    log = {
        "tipo": tipo,
        "componente": componente,
        "valor": valor,
        "limite": limite,
        "mensagem": mensagem,
        "timestamp": timestamp(),
    }

    # Sempre salva nos arquivos
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{log['timestamp']}] {tipo.upper()} - {componente if componente else ''}\n")
        f.write(mensagem.strip() + "\n")
        f.write("-" * 70 + "\n")

    with open(LOG_JSON_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

    # Só exibe no console se --log console
    if getattr(args, "log", "arquivo") == "console":
        print(mensagem.strip())
        print("-" * 70)

    log_verbose(f"Evento registrado: {log}", getattr(args, "verbose", False))

    if getattr(args, "enviar", False):
        enviar_email_alerta(formatar_metricas(metricas(), para_email=True))