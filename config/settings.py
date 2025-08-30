import os
import datetime
import socket
from dotenv import load_dotenv

# Carrega variáveis do .env, se existir
load_dotenv()

# Info de tempo e host
now = datetime.datetime.now()
TIMESTAMP = now.strftime("%Y-%m-%d %H:%M:%S")
DATE_STR = now.strftime("%Y-%m-%d")
HOSTNAME = socket.gethostname()

# Email e alertas
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.exemplo.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

# Limiares
THRESH_MEM_ALERTA = float(os.getenv("THRESH_MEM_ALERTA", "75"))
THRESH_MEM_CRITICO = float(os.getenv("THRESH_MEM_CRITICO", "90"))

THRESH_CPU_ALERTA = float(os.getenv("THRESH_CPU_ALERTA", "75"))
THRESH_CPU_CRITICO = float(os.getenv("THRESH_CPU_CRITICO", "90"))

THRESH_DISCO_ALERTA = float(os.getenv("THRESH_DISCO_ALERTA", "80"))
THRESH_DISCO_CRITICO = float(os.getenv("THRESH_DISCO_CRITICO", "95"))

# Execução
LOOP_SECONDS = int(os.getenv("LOOP_SECONDS", "30"))
SLEEP_AFTER_CLEAN = int(os.getenv("SLEEP_AFTER_CLEAN", "30"))

# Diretórios e logs
LOG_DIR = os.getenv("LOG_DIR", os.path.join("services", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_JSON_FILE = os.path.join(LOG_DIR, f"log_metricas_{DATE_STR}.json")
LOG_FILE = os.path.join(LOG_DIR, f"log_{DATE_STR}.txt")

STATUS = {
    "cpu_total": {
        "alerta": THRESH_CPU_ALERTA,
        "critico": THRESH_CPU_CRITICO
    },
    "memoria_percent": {
        "alerta": THRESH_MEM_ALERTA,
        "critico": THRESH_MEM_CRITICO
    },
    "disco_percent": {
        "alerta": THRESH_DISCO_ALERTA,
        "critico": THRESH_DISCO_CRITICO
    }
}