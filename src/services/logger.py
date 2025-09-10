"""
Módulo de registro e análise de eventos do sistema.
Inclui funções para registrar logs, calcular médias e enviar alertas por e-mail.
"""
import os
import json
from datetime import datetime
from config.settings import DATE_STR
from core.monitor import formatar_metricas, metricas
from services.helpers import timestamp, log_verbose
from services.utils import enviar_email_alerta

def enviar_alerta_media_alertas(estados_alerta, args):
    """
    Envia alerta por e-mail com médias dos últimos estados de alerta registrados.
    """
    medias_jsonl = calcular_media_ultimas_linhas_jsonl()
    mensagem = f"Alerta de média dos últimos estados de alerta!\nMédias JSONL: {medias_jsonl}"
    enviar_email_alerta(mensagem)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOGS_JSON_DIR = os.path.join(LOGS_DIR, "json")
os.makedirs(LOGS_JSON_DIR, exist_ok=True)
LOGS_TEXT_DIR = os.path.join(LOGS_DIR, "log")
os.makedirs(LOGS_TEXT_DIR, exist_ok=True)
LOG_JSON_FILE = os.path.join(LOGS_JSON_DIR, f"log_metricas_{DATE_STR}.jsonl")
LOG_FILE = os.path.join(LOGS_TEXT_DIR, f"log_metricas{DATE_STR}.log")


def registrar_evento(tipo, componente, valor, limite, args, mensagem, ciclo=None):
    """
    Registra evento de métrica em arquivos de log texto e JSONL.
    Exibe no console se configurado. Envio de e-mail é centralizado.
    """
    log_data = {
        "tipo": tipo,
        "componente": componente,
        "valor": valor,
        "limite": limite,
        "mensagem": mensagem,
        "timestamp": timestamp(),
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        ciclo_str = f"CICLO: {ciclo}\n" if ciclo is not None else ""
        f.write(f"[{log_data['timestamp']}] {tipo.upper()} - {componente if componente else ''}\n")
        f.write(ciclo_str)
        f.write(mensagem.strip() + "\n")
        f.write("-" * 70 + "\n")
    with open(LOG_JSON_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
    if getattr(args, "log", "arquivo") == "console":
        print(mensagem.strip())
        print("-" * 70)
    log_verbose(f"Evento registrado: {log_data}", getattr(args, "verbose", False))


def calcular_media_ultimas_linhas_jsonl():
    """
    Calcula a média dos valores numéricos dos últimos registros JSONL.
    """
    if not os.path.exists(LOG_JSON_FILE):
        return None
    linhas = []
    with open(LOG_JSON_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip():
                linhas.append(json.loads(linha))
    ultimas = linhas[-60:] if len(linhas) >= 60 else linhas
    metricas_agregadas = {}
    for log in ultimas:
        for k, v in log.items():
            if k in ["valor"] and isinstance(v, (int, float)):
                metricas_agregadas.setdefault(k, []).append(v)
    medias = {k: (sum(vs)/len(vs) if vs else None) for k, vs in metricas_agregadas.items()}
    return medias


def calcular_media_ultimos_blocos_log():
    """
    Calcula a média dos valores encontrados nos últimos blocos do log texto.
    """
    if not os.path.exists(LOG_FILE):
        return None
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        conteudo = f.read()
    blocos = conteudo.split("-"*70)
    blocos = [b for b in blocos if b.strip()]
    ultimos = blocos[-60:] if len(blocos) >= 60 else blocos

    # Dicionários para somar valores
    soma = {
        "cpu": [], "mem_usada": [], "mem_total": [], "mem_percent": [],
        "disco_usado": [], "disco_total": [], "disco_percent": [],
        "ping": [], "latencia": [], "rede_enviados": [], "rede_recebidos": []
    }
    for bloco in ultimos:
        for linha in bloco.splitlines():
            if linha.startswith("CPU:"):
                try:
                    soma["cpu"].append(float(linha.split(":")[1].replace("%", "").strip()))
                except: pass
            elif linha.startswith("Memória:"):
                try:
                    partes = linha.split(":")[1].split("/")
                    mem_usada = float(partes[0].replace("GB", "").strip())
                    mem_total = float(partes[1].split("(")[0].replace("GB", "").strip())
                    mem_percent = float(partes[1].split("(")[1].replace("%)", "").replace("%", "").strip())
                    soma["mem_usada"].append(mem_usada)
                    soma["mem_total"].append(mem_total)
                    soma["mem_percent"].append(mem_percent)
                except: pass
            elif linha.startswith("Disco:"):
                try:
                    partes = linha.split(":")[1].split("/")
                    disco_usado = float(partes[0].replace("GB", "").strip())
                    disco_total = float(partes[1].split("(")[0].replace("GB", "").strip())
                    disco_percent = float(partes[1].split("(")[1].replace("%)", "").replace("%", "").strip())
                    soma["disco_usado"].append(disco_usado)
                    soma["disco_total"].append(disco_total)
                    soma["disco_percent"].append(disco_percent)
                except: pass
            elif linha.startswith("Ping:"):
                try:
                    soma["ping"].append(float(linha.split(":")[1].replace("ms", "").strip()))
                except: pass
            elif linha.startswith("Latência TCP:"):
                try:
                    soma["latencia"].append(float(linha.split(":")[1].replace("ms", "").strip()))
                except: pass
            elif linha.startswith("Rede:"):
                try:
                    partes = linha.split(":")[1].split("/")
                    enviados = partes[0].replace("enviados", "").strip()
                    recebidos = partes[1].replace("recebidos", "").strip()
                    # Converter para MB se necessário
                    if "MB" in enviados:
                        enviados = float(enviados.replace("MB", "").strip())
                    else:
                        enviados = float(enviados.replace("bytes", "").strip()) / (1024*1024)
                    if "MB" in recebidos:
                        recebidos = float(recebidos.replace("MB", "").strip())
                    else:
                        recebidos = float(recebidos.replace("bytes", "").strip()) / (1024*1024)
                    soma["rede_enviados"].append(enviados)
                    soma["rede_recebidos"].append(recebidos)
                except: pass

    # Calcular médias
    def media(lista):
        return sum(lista)/len(lista) if lista else None

    def fmt(val):
        return f"{val:.1f}" if val is not None else "N/A"

    bloco_media = (
        f"CPU: {fmt(media(soma['cpu']))}%\n"
        f"Memória: {media(soma['mem_usada']):.1f} GB / {media(soma['mem_total']):.1f} GB ({media(soma['mem_percent']):.1f}%)\n"
        f"Disco: {media(soma['disco_usado']):.1f} GB / {media(soma['disco_total']):.1f} GB ({media(soma['disco_percent']):.1f}%)\n"
        f"Temperatura CPU: Indisponível°C\n"
        f"Temperatura Placa-mãe: Indisponível°C\n"
        f"Temperatura GPU: Indisponível°C\n"
        f"Ping: {media(soma['ping']):.1f} ms\n"
        f"Latência TCP: {media(soma['latencia']):.1f} ms\n"
        f"Rede: {media(soma['rede_enviados']):.1f} MB enviados / {media(soma['rede_recebidos']):.1f} MB recebidos\n"
    )

    metricas_media_log = os.path.join(LOGS_TEXT_DIR, f"metricas_media_{DATE_STR}.log")
    with open(metricas_media_log, "a", encoding="utf-8") as f:
        f.write("-"*70 + "\n")
        f.write(bloco_media)
        f.write("-"*70 + "\n")

    media_obj = {
        "media": {k: media(v) for k, v in soma.items()},
        "ciclos": len(ultimos),
        "timestamp": timestamp()
    }
    metricas_media_json = os.path.join(LOGS_JSON_DIR, f"metricas_media_{DATE_STR}.jsonl")
    with open(metricas_media_json, "a", encoding="utf-8") as f:
        f.write(json.dumps(media_obj, ensure_ascii=False) + "\n")
    return bloco_media


def enviar_alerta_media_criticos(estados_criticos, args):
    """
    Envia alerta por e-mail com médias dos últimos estados críticos registrados.
    """
    medias_jsonl = calcular_media_ultimas_linhas_jsonl()
    media_log = calcular_media_ultimos_blocos_log()
    mensagem = f"Alerta de média dos últimos estados críticos!\nMédias JSONL: {medias_jsonl}\nMédia LOG: {media_log}"
    enviar_email_alerta(mensagem)