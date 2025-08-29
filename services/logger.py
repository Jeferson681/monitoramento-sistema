from datetime import datetime
import json
import os

from config.status import log_json_file
from core.monitor import formatar_metricas, metricas
from services.helpers import log_verbose, enviar_email_alerta, timestamp  # agora vem de helpers

PASTA_LOGS = os.path.join(os.path.dirname(__file__), "logs")

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
        with open(log_json_file, "a") as f:
            f.write(json.dumps(log) + "\n")
    else:
        print(log)

    log_verbose(f"Evento registrado: {log}", getattr(args, "verbose", False))

    if getattr(args, "enviar", False):
        enviar_email_alerta(formatar_metricas(metricas(), para_email=True))

def gerar_log(tipo, componente, valor_antigo, valor_novo, mensagem, PASTA_SERVICES=None):
    dados = {
        "tipo": tipo,
        "componente": componente,
        "valor_antigo": valor_antigo,
        "valor_novo": valor_novo,
        "mensagem": mensagem,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    os.makedirs(PASTA_SERVICES, exist_ok=True)
    caminho_arquivo = os.path.join(PASTA_SERVICES, "monitoramento.log")

    with open(caminho_arquivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(dados, ensure_ascii=False) + "\n")