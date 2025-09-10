
"""
Configurações globais do sistema de monitoramento.
Carrega variáveis do .env, define limiares e parâmetros de execução.
Inclui informações de tempo, host, e limites para alertas/críticos.
"""

from dotenv import load_dotenv
import os
import datetime
import socket

# Carrega variáveis do .env, se existir
load_dotenv()

# Informações de tempo e host
now = datetime.datetime.now()
TIMESTAMP = now.strftime("%Y-%m-%d %H:%M:%S")  # Data/hora atual
DATE_STR = now.strftime("%Y-%m-%d")            # Data atual (YYYY-MM-DD)
HOSTNAME = socket.gethostname()                 # Nome do host

# Configurações de e-mail (usadas para alertas)
EMAIL_HOST = os.getenv("EMAIL_HOST", "example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "usuario_exemplo")
EMAIL_PASS = os.getenv("EMAIL_PASS", "senha_exemplo")
EMAIL_TO = os.getenv("EMAIL_TO", "destinatario@exemplo.com")

# Limiares para alertas e críticos (ajuste conforme ambiente)
THRESH_MEM_ALERTA = float(os.getenv("THRESH_MEM_ALERTA", "70"))      # Memória alerta (%)
THRESH_MEM_CRITICO = float(os.getenv("THRESH_MEM_CRITICO", "90"))   # Memória crítico (%)
THRESH_CPU_ALERTA = float(os.getenv("THRESH_CPU_ALERTA", "70"))      # CPU alerta (%)
THRESH_CPU_CRITICO = float(os.getenv("THRESH_CPU_CRITICO", "90"))   # CPU crítico (%)
THRESH_DISCO_ALERTA = float(os.getenv("THRESH_DISCO_ALERTA", "75"))  # Disco alerta (%)
THRESH_DISCO_CRITICO = float(os.getenv("THRESH_DISCO_CRITICO", "90"))# Disco crítico (%)
THRESH_PING_ALERTA = float(os.getenv("THRESH_PING_ALERTA", "80"))    # Ping alerta (ms)
THRESH_PING_CRITICO = float(os.getenv("THRESH_PING_CRITICO", "200")) # Ping crítico (ms)
THRESH_LATENCIA_ALERTA = float(os.getenv("THRESH_LATENCIA_ALERTA", "80"))  # Latência alerta (ms)
THRESH_LATENCIA_CRITICO = float(os.getenv("THRESH_LATENCIA_CRITICO", "200"))# Latência crítico (ms)

# Parâmetros de execução do monitoramento
LOOP_SECONDS = int(os.getenv("LOOP_SECONDS", "30"))          # Intervalo entre ciclos
SLEEP_AFTER_CLEAN = int(os.getenv("SLEEP_AFTER_CLEAN", "30"))# Pausa após limpeza

# Dicionário de status para avaliação de métricas
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
    },
    "ping_ms": {
        "alerta": THRESH_PING_ALERTA,
        "critico": THRESH_PING_CRITICO
    },
    "latencia_tcp_ms": {
        "alerta": THRESH_LATENCIA_ALERTA,
        "critico": THRESH_LATENCIA_CRITICO
    }
}

