import psutil
from src.core.system import (
    obter_disco_principal,
    ler_temperaturas_bash,
    medir_ping,
    medir_latencia,
)
import datetime

def metricas():
    """Coleta métricas do sistema em tempo real."""
    memoria = psutil.virtual_memory()
    disco_principal = obter_disco_principal()
    mountpoint = disco_principal.get("mountpoint", "/") if isinstance(disco_principal, dict) else disco_principal

    try:
        disco = psutil.disk_usage(mountpoint)
    except FileNotFoundError:
        disco = psutil.disk_usage("/")

    rede = psutil.net_io_counters()
    ping_ms = medir_ping()["data"] or 0.0
    latencia_tcp = medir_latencia()["data"] or 0.0
    temperaturas = ler_temperaturas_bash()

    if isinstance(temperaturas, str):
        temperaturas = {"cpu_temp": None, "mb_temp": None, "gpu_temp": None}

    return {
        "cpu_total": psutil.cpu_percent(interval=None),
        "memoria_usada": memoria.used / (1024 ** 3),
        "memoria_total": memoria.total / (1024 ** 3),
        "memoria_percent": memoria.percent,
        "disco_usado": disco.used / (1024 ** 3),
        "disco_total": disco.total / (1024 ** 3),
        "disco_percent": disco.percent,
        "temperatura_cpu": temperaturas.get("cpu_temp"),
        "temperatura_motherboard": temperaturas.get("mb_temp"),
        "temperatura_gpu": temperaturas.get("gpu_temp"),
        "ping_ms": ping_ms,
        "latencia_tcp_ms": latencia_tcp,
        "rede_bytes_enviados": rede.bytes_sent,
        "rede_bytes_recebidos": rede.bytes_recv,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def format_bytes(n):
    """Formata um número de bytes em uma string legível (ex: '1.5 GB')."""
    for unidade in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if n < 1024.0:
            return f"{n:.1f} {unidade}"
        n /= 1024.0
    return f"{n:.1f} PB"

def formatar_metricas(dados, para_email=False):
    def safe_float(valor, default=0.0):
        try:
            return float(valor)
        except (TypeError, ValueError):
            return default

    def safe_str(valor, default="Indisponível"):
        if valor is None or isinstance(valor, dict):
            return default
        return str(valor)

    texto = (
        f"CPU: {safe_float(dados.get('cpu_total')):.1f}%\n"
        f"Memória: {safe_float(dados.get('memoria_usada')):.1f} GB / "
        f"{safe_float(dados.get('memoria_total')):.1f} GB "
        f"({safe_float(dados.get('memoria_percent')):.1f}%)\n"
        f"Disco: {safe_float(dados.get('disco_usado')):.1f} GB / "
        f"{safe_float(dados.get('disco_total')):.1f} GB "
        f"({safe_float(dados.get('disco_percent')):.1f}%)\n"
        f"Temperatura CPU: {safe_str(dados.get('temperatura_cpu'))}°C\n"
        f"Temperatura Placa-mãe: {safe_str(dados.get('temperatura_motherboard'))}°C\n"
        f"Temperatura GPU: {safe_str(dados.get('temperatura_gpu'))}°C\n"
        f"Ping: {safe_str(dados.get('ping_ms'))} ms\n"
        f"Latência TCP: {safe_str(dados.get('latencia_tcp_ms'))} ms\n"
        f"Rede: {format_bytes(safe_float(dados.get('rede_bytes_enviados')))} enviados / "
        f"{format_bytes(safe_float(dados.get('rede_bytes_recebidos')))} recebidos\n"
        f"-------------------------------------------------------------------"
    )

    if para_email:
        return f"📊 MÉTRICAS ({dados.get('timestamp', '')})\n{texto}"
    return texto