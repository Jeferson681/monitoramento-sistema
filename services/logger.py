from datetime import datetime
import json
import os

from config.settings import LOG_JSON_FILE
from core.monitor import formatar_metricas, metricas
from services.helpers import log_verbose, enviar_email_alerta, timestamp  # agora vem de helpers

PASTA_SERVICES = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(PASTA_SERVICES, exist_ok=True)
CAMINHO_ARQUIVO = os.path.join(PASTA_SERVICES, "monitoramento.log")


def registrar_evento(tipo, componente, valor_antigo, valor_novo, args, mensagem_extra=""):
    log = {
        "tipo": tipo,
        "componente": componente,
        "valor_antigo": valor_antigo,
        "valor_novo": valor_novo,
        "mensagem": mensagem_extra,
        "timestamp": timestamp()
    }

    if getattr(args, "log", "console") == "arquivo":
        with open(LOG_JSON_FILE, "a") as f:
            f.write(json.dumps(log) + "\n")
    else:
        print(log)

    log_verbose(f"Evento registrado: {log}", getattr(args, "verbose", False))

    if getattr(args, "enviar", False):
        enviar_email_alerta(formatar_metricas(metricas(), para_email=True))

def gerar_log(tipo, componente, valor_antigo, valor_novo, mensagem, PASTA_SERVICES=None):
    if not PASTA_SERVICES:
        PASTA_SERVICES = os.path.join(os.path.dirname(__file__), "logs")

    os.makedirs(PASTA_SERVICES, exist_ok=True)
    caminho_arquivo = os.path.join(PASTA_SERVICES, "monitoramento.log")

    dados = {
        "tipo": tipo,
        "componente": componente,
        "valor_antigo": valor_antigo,
        "valor_novo": valor_novo,
        "mensagem": mensagem,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(caminho_arquivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(dados, ensure_ascii=False) + "\n")

    print(dados)

    # Também imprime no console
    print(dados)
