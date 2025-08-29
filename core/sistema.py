import ctypes
import os
import platform
import subprocess
import time

import psutil
from pathlib import Path
SCRIPT_PATH = Path(__file__).parent / "script" / "lm_sensors.sh"

# INFO: Caminho do disco principal
def obter_disco_principal():
    if os.name == "nt":
        return os.environ.get('SystemDrive', 'C:\\')
    else:
        return '/'

# SCRIPT: sensor.sh externo para tentativa de consulta de temperatura
def sensor_sh():
    subprocess.run(["bash", str(SCRIPT_PATH)], check=False)


# INFO: Verificação de estado de alerta e crítico
def verificar_estado(valor, alerta, critico):
    if valor is None:
        return False, False
    return alerta <= valor < critico, valor >= critico


import platform
import psutil
import ctypes
import os

def limpar_ram_global():
    """Limpa RAM ou cache dependendo do sistema"""
    sistema = platform.system().lower()

    if sistema == "windows":
        print("🧹 Limpando RAM no Windows...")
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.info['pid'])
                ctypes.windll.psapi.EmptyWorkingSet(handle)
                ctypes.windll.kernel32.CloseHandle(handle)
            except Exception:
                pass  # ignora processos protegidos
    elif sistema == "linux":
        print("🧹 Limpando cache no Linux...")
        try:
            os.system("sync; echo 3 > /proc/sys/vm/drop_caches")
        except Exception as e:
            print(f"Erro ao limpar cache: {e}")
    else:
        print(f"⚠️ Limpeza de RAM não suportada para: {sistema}")


def estado_ram_limpa(componente, valor, alerta, critico, metricas_func, sleep_seconds=None):
    """Tenta limpar RAM e reavalia estado"""
    limpar_ram_global()
    if sleep_seconds is None:
        sleep_seconds = int(os.getenv("SLEEP_AFTER_CLEAN", "30"))
    time.sleep(sleep_seconds)
    novo_valor = metricas_func().get(componente)
    if novo_valor is None:
        return valor, False, False
    estado_restaurado = novo_valor < critico
    estado_alerta = alerta <= novo_valor < critico
    return novo_valor, estado_restaurado, estado_alerta

def ler_temperatura():
    try:
        resultado = subprocess.run(
            ["bash", "./script/lm_sensors.sh"],
            capture_output=True,
            text=True
        )
        if resultado.returncode == 0:
            return f"{resultado.stdout.strip()}°C"
        return None  # Não printa nada, só retorna None
    except Exception:
        return None


# INFO: Coleta de métricas específicas
