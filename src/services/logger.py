from datetime import datetime
import json
import os

from config.settings import LOG_JSON_FILE
from core.monitor import formatar_metricas, metricas
from services.helpers import log_verbose, timestamp
from services.utils import enviar_email_alerta

#  Define pasta padrão para salvar logs locais
PASTA_SERVICES = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(PASTA_SERVICES, exist_ok=True)
CAMINHO_ARQUIVO = os.path.join(PASTA_SERVICES, "monitoramento.log")

#  Registra evento completo: log, console, e-mail (se ativado)
def registrar_evento(tipo, componente, valor_antigo, valor_novo, args, mensagem_extra=""):
    log = {
        "tipo": tipo,
        "componente": componente,
        "valor_antigo": valor_antigo,
        "valor_novo": valor_novo,
        "mensagem": mensagem_extra,
        "timestamp": timestamp()
    }

    # Salva no log local (arquivo .log)
    gerar_log(tipo, componente, valor_antigo, valor_novo, mensagem_extra)

    # Salva no log JSON (se modo arquivo estiver ativado)
    if getattr(args, "log", "console") == "arquivo":
        with open(LOG_JSON_FILE, "a") as f:
            f.write(json.dumps(log) + "\n")
    else:
        return

    # Exibe log verboso no console (se ativado)
    log_verbose(f"Evento registrado: {log}", getattr(args, "verbose", False))

    # Envia e-mail com métricas (se ativado)
    if getattr(args, "enviar", False):
        enviar_email_alerta(formatar_metricas(metricas(), para_email=True))

#  Gera log local em formato JSON simples
def gerar_log(tipo, componente, valor_antigo, valor_novo, mensagem, pasta_services=None):
    if not pasta_services:
        # Usa pasta padrão ou definida via variável de ambiente
        pasta_services = os.getenv("PASTA_SERVICES", os.path.join(os.path.dirname(__file__), "logs"))

    os.makedirs(pasta_services, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_services, "monitoramento.log")

    dados = {
        "tipo": tipo,
        "componente": componente,
        "valor_antigo": valor_antigo,
        "valor_novo": valor_novo,
        "mensagem": mensagem,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Salva linha JSON no arquivo de log
    with open(caminho_arquivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(dados, ensure_ascii=False) + "\n")