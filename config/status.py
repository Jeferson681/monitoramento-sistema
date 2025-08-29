import argparse
import datetime
import socket
import os

# INFO: Tempo atual
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
date_str = now.strftime("%Y-%m-%d")

# INFO: Email do responsável
admin_email = "admin@seudenomino.com"

# INFO: Nome do host/máquina
hostname = socket.gethostname()

# INFO: Diretório de logs
log_dir = "/var/logs/monitoramento"
log_json_file = os.path.join(log_dir, f"log_metricas_{date_str}.json")
os.makedirs(log_dir, exist_ok=True)

# INFO: Caminho do log diário
log_file = os.path.join(log_dir, f"log_{date_str}.txt")

# CRITICO: Flags de controle
DEBUG_MODE = True
SEND_EMAIL_ON_CRITICAL = True
AUTO_CLEANUP_ENABLED = True

# STATUS: Limiares de alerta e crítico por métrica
STATUS = {
    "cpu_total": {"alerta": 75, "critico": 90},
    "memoria_percent": {"alerta": 75, "critico": 90},
    "disco_percent": {"alerta": 80, "critico": 95},
    #"temperatura": {"alerta": 70, "critico": 90},
    #"ping_latency_ms": {"alerta": 100, "critico": 300}
}



def parse_args():
    parser = argparse.ArgumentParser(description="Monitoramento do sistema")
    parser.add_argument("--modo", choices=["único", "contínuo"], default="único", help="Modo de execução")
    parser.add_argument("--loop", type=int, default=30, help="Intervalo em segundos no modo contínuo")
    parser.add_argument("--log", choices=["console", "arquivo"], default="console", help="Destino do log")
    parser.add_argument("--verbose", action="store_true", help="Ativa logs verbosos")
    parser.add_argument("--enviar", action="store_true", help="Envia e-mail quando há evento")
    return parser.parse_args()
