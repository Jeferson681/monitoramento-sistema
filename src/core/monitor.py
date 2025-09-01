import psutil
import platform
from core.system import obter_disco_principal, ler_temperaturas_bash
import subprocess
import time
import socket
import re
from services.utils import debug_log

# 📡 Coleta métricas do sistema em tempo real
def medir_ping(host="8.8.8.8", count=4, timeout=2):
    """
    Mede o tempo de resposta (ping) para um host.
    Retorna latência média em ms, None em caso de erro, ou 0.0 se inacessível.
    Adiciona prints para debug.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    try:
        cmd = ["ping", param, str(count), timeout_param, str(timeout), host]
        debug_log(f"[DEBUG] Executando comando: {' '.join(cmd)}")
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True, encoding="utf-8", errors="ignore")
        debug_log("[DEBUG] Saída do ping:\n" + output)
        for line in output.splitlines():
            debug_log(f"[DEBUG] Linha: {line}")
            match = re.search(r"=\s*(\d+)\s*ms", line)
            if match and ("M" in line or "A" in line):
                debug_log(f"[DEBUG] Latência encontrada: {match.group(1)} ms")
                return float(match.group(1))
        debug_log("[DEBUG] Latência não encontrada, retornando 0.0")
        return 0.0
    except subprocess.CalledProcessError as e:
        debug_log(f"[DEBUG] CalledProcessError: {e.output}")
        return 0.0
    except Exception as ex:
        debug_log(f"[DEBUG] Erro inesperado: {ex}")
        return None

def medir_latencia(host="8.8.8.8"):
    """
    Mede a latência de conexão TCP ao host na porta 80.
    Retorna latência em ms ou None se falhar.
    """
    try:
        start = time.time()
        s = socket.create_connection((host, 443), timeout=2)
        s.close()
        return (time.time() - start) * 1000
    except Exception:
        return None

def metricas():
    mem = psutil.virtual_memory()  # dados de memória RAM
    disco = psutil.disk_usage(obter_disco_principal())  # uso do disco principal
    net = psutil.net_io_counters()

    ping_ms = medir_ping()
    latencia_tcp = medir_latencia()

    # Chama função que executa o bash e retorna temperaturas
    temps = ler_temperaturas_bash()

    return {
        "cpu_total": psutil.cpu_percent(interval=None),  # uso total da CPU (%)
        "memoria_usada": mem.used / (1024 ** 3),         # memória usada (GB)
        "memoria_total": mem.total / (1024 ** 3),        # memória total (GB)
        "memoria_percent": mem.percent,                  # uso da memória (%)
        "disco_usado": disco.used / (1024 ** 3),         # disco usado (GB)
        "disco_total": disco.total / (1024 ** 3),        # disco total (GB)
        "disco_percent": disco.percent,                  # uso do disco (%)
        "temperatura_cpu": temps.get("cpu_temp", None),          # temperatura CPU
        "temperatura_motherboard": temps.get("mb_temp", None),   # temperatura placa-mãe
        "temperatura_gpu": temps.get("gpu_temp", None),          # temperatura GPU
        "ping_ms": ping_ms,                              # ping médio (ms)
        "latencia_tcp_ms": latencia_tcp,                 # latência TCP (ms)
        "rede_bytes_enviados": net.bytes_sent,
        "rede_bytes_recebidos": net.bytes_recv
    }

def format_bytes(n):
    """
    Formata um número de bytes em uma string legível (ex: '1.5 GB').
    """
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if n < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"

# 🧾 Formata as métricas para exibição ou envio por e-mail
def formatar_metricas(dados, para_email=False):
    base = (
        f"CPU: {dados.get('cpu_total', 0.0) or 0.0:.1f}%\n"
        f"Memória: {dados.get('memoria_usada', 0.0) or 0.0:.1f} GB / {dados.get('memoria_total', 0.0) or 0.0:.1f} GB ({dados.get('memoria_percent', 0.0) or 0.0:.1f}%)\n"
        f"Disco: {dados.get('disco_usado', 0.0) or 0.0:.1f} GB / {dados.get('disco_total', 0.0) or 0.0:.1f} GB ({dados.get('disco_percent', 0.0) or 0.0:.1f}%)\n"
        f"Temperatura CPU: {dados.get('temperatura_cpu', 'Indisponível') or 'Indisponível'}°C\n"
        f"Temperatura Placa-mãe: {dados.get('temperatura_motherboard', 'Indisponível') or 'Indisponível'}°C\n"
        f"Temperatura GPU: {dados.get('temperatura_gpu', 'Indisponível') or 'Indisponível'}°C\n"
        f"Ping: {dados.get('ping_ms', 0.0) or 0.0:.1f} ms\n"
        f"Latência TCP: {dados.get('latencia_tcp_ms', 0.0) or 0.0:.1f} ms\n"
        f"Rede: {format_bytes(dados.get('rede_bytes_enviados', 0) or 0)} enviados / {format_bytes(dados.get('rede_bytes_recebidos', 0) or 0)} recebidos"
    )

    # Se for para e-mail, inclui o timestamp no topo
    return f"📊 MÉTRICAS ({dados.get('timestamp', '')})\n{base}" if para_email else base