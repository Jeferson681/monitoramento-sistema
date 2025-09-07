import os
import subprocess
import platform
import time
import socket
import re
from pathlib import Path
import psutil
import shutil
from src.services.utils import debug_log

# Caminho do script externo para leitura de sensores (Linux)
SCRIPT_PATH = Path(__file__).parent / "script" / "lm_sensors.sh"

# Cache para armazenar os dados coletados e os timestamps
cache = {
    "cpu": {"data": None, "last_updated": 0, "interval": 10},
    "memory": {"data": None, "last_updated": 0, "interval": 10},
    "disk": {"data": None, "last_updated": 0, "interval": 30},
    "temperature": {"data": None, "last_updated": 0, "interval": 60},
    "ping": {"data": None, "last_updated": 0, "interval": 30},
    "latency": {"data": None, "last_updated": 0, "interval": 30},
    "network": {"data": None, "last_updated": 0, "interval": 15},
}

# Função auxiliar para verificar se o intervalo foi ultrapassado
def _should_update(key):
    current_time = time.time()
    return current_time - cache[key]["last_updated"] >= cache[key]["interval"]

# CPU: Coleta o uso total da CPU
def medir_cpu():
    if _should_update("cpu"):
        cache["cpu"]["data"] = psutil.cpu_percent(interval=None)
        cache["cpu"]["last_updated"] = time.time()
    return {
        "data": cache["cpu"]["data"],
        "timestamp": cache["cpu"]["last_updated"]
    }

# Memória RAM: Coleta informações sobre a memória
def medir_memoria():
    if _should_update("memory"):
        mem = psutil.virtual_memory()
        cache["memory"]["data"] = {
            "total": mem.total,
            "used": mem.used,
            "percent": mem.percent,
        }
        cache["memory"]["last_updated"] = time.time()
    return {
        "data": cache["memory"]["data"],
        "timestamp": cache["memory"]["last_updated"]
    }

def obter_disco_principal():
    if _should_update("disk"):
        system_name = platform.system().lower()
        debug_log(f"[DEBUG] platform.system().lower(): {system_name}")
        if system_name == "windows":
            disk_path = os.environ.get('SystemDrive', 'C:\\')
        else:
            disk_path = '/'
        disk_usage = psutil.disk_usage(disk_path)
        cache["disk"]["data"] = {
            "path": disk_path,
            "total": disk_usage.total,
            "used": disk_usage.used,
            "free": disk_usage.free,
            "percent": disk_usage.percent,
        }
        cache["disk"]["last_updated"] = time.time()
    return {
        "data": cache["disk"]["data"],
        "timestamp": cache["disk"]["last_updated"]
    }

# Temperatura: Coleta temperaturas de CPU, placa-mãe e GPU via script bash (Linux)
def ler_temperaturas_bash():
    if _should_update("temperature"):
        try:
            resultado = subprocess.run(
                ["bash", str(SCRIPT_PATH)],
                capture_output=True,
                text=True
            )
            temps = {}
            if resultado.returncode == 0:
                for line in resultado.stdout.strip().splitlines():
                    if "=" in line:
                        chave, valor = line.strip().split("=", 1)
                        try:
                            temps[chave.strip()] = float(valor.strip())
                        except ValueError:
                            temps[chave.strip()] = None
            cache["temperature"]["data"] = temps
        except Exception:
            cache["temperature"]["data"] = {}  # Em caso de erro, retorna dicionário vazio
        cache["temperature"]["last_updated"] = time.time()
    return {
        "data": cache["temperature"]["data"],
        "timestamp": cache["temperature"]["last_updated"]
    }

# Ping: Mede o tempo de resposta (ping)

def medir_ping(host="8.8.8.8", count=4, timeout=2000):
    if _should_update("ping"):
        latencias = []
        sistema = platform.system().lower()
        param = "-n" if sistema == "windows" else "-c"
        timeout_param = "-w" if sistema == "windows" else "-W"
        timeout_value = str(timeout) if sistema == "windows" else str(int(timeout / 1000))

        try:
            cmd = ["ping", param, str(count), timeout_param, timeout_value, host]
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore"
            )
            for line in output.splitlines():
                match_pt = re.search(r"tempo[=<]?\s*(\d+(?:\.\d+)?)\s*ms", line)
                match_en = re.search(r"time[=<]?\s*(\d+(?:\.\d+)?)\s*ms", line)
                if match_pt:
                    latencias.append(float(match_pt.group(1)))
                elif match_en:
                    latencias.append(float(match_en.group(1)))
            if latencias:
                cache["ping"]["data"] = sum(latencias) / len(latencias)
            else:
                cache["ping"]["data"] = None
        except Exception as e:
            debug_log(f"[DEBUG] Erro ao executar ping: {e}")
            cache["ping"]["data"] = None
        cache["ping"]["last_updated"] = time.time()
    return {
        "data": cache["ping"]["data"],
        "timestamp": cache["ping"]["last_updated"]
    }

def medir_latencia(host="8.8.8.8", count=4, timeout=2000):
    if _should_update("latency"):
        latencias = []
        sistema = platform.system().lower()
        param = "-n" if sistema == "windows" else "-c"
        timeout_param = "-w" if sistema == "windows" else "-W"
        timeout_value = str(timeout) if sistema == "windows" else str(int(timeout / 1000))

        try:
            cmd = ["ping", param, str(count), timeout_param, timeout_value, host]
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore"
            )
            for line in output.splitlines():
                match_pt = re.search(r"tempo[=<]?\s*(\d+(?:\.\d+)?)\s*ms", line)
                match_en = re.search(r"time[=<]?\s*(\d+(?:\.\d+)?)\s*ms", line)
                if match_pt:
                    latencias.append(float(match_pt.group(1)))
                elif match_en:
                    latencias.append(float(match_en.group(1)))
            if latencias:
                cache["latency"]["data"] = sum(latencias) / len(latencias)
            else:
                cache["latency"]["data"] = None
        except Exception as e:
            debug_log(f"[DEBUG] Erro ao executar ping para latência: {e}")
            cache["latency"]["data"] = None
        cache["latency"]["last_updated"] = time.time()
    return {
        "data": cache["latency"]["data"],
        "timestamp": cache["latency"]["last_updated"]
    }

# Rede: Coleta informações sobre bytes enviados e recebidos
def medir_rede():
    if _should_update("network"):
        net = psutil.net_io_counters()
        cache["network"]["data"] = {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
        }
        cache["network"]["last_updated"] = time.time()
    return {
        "data": cache["network"]["data"],
        "timestamp": cache["network"]["last_updated"]
    }
