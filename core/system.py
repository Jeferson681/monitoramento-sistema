import ctypes
import os
import platform
import subprocess
import time
import psutil
from pathlib import Path

#  Caminho do script externo para leitura de sensores (Linux)
SCRIPT_PATH = Path(__file__).parent / "script" / "lm_sensors.sh"

#  Retorna o caminho do disco principal (C:\ no Windows, / no Linux)
def obter_disco_principal():
    if os.name == "nt":
        return os.environ.get('SystemDrive', 'C:\\')
    else:
        return '/'

#  Executa script externo para tentar obter temperatura via lm_sensors
def sensor_sh():
    subprocess.run(["bash", str(SCRIPT_PATH)], check=False)

#  Verifica se o valor está em estado de alerta ou crítico
def verificar_estado(valor, alerta, critico):
    if valor is None:
        return False, False
    return alerta <= valor < critico, valor >= critico

#  Tenta limpar RAM ou cache, dependendo do sistema operacional
def limpar_ram_global():
    sistema = platform.system().lower()

    if sistema == "windows":
        print(" Limpando RAM no Windows...")
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.info['pid'])
                ctypes.windll.psapi.EmptyWorkingSet(handle)
                ctypes.windll.kernel32.CloseHandle(handle)
            except Exception:
                pass  # ignora processos protegidos
    elif sistema == "linux":
        print(" Limpando cache no Linux...")
        try:
            os.system("sync; echo 3 > /proc/sys/vm/drop_caches")
        except Exception as e:
            print(f"Erro ao limpar cache: {e}")
    else:
        print(f" Limpeza de RAM não suportada para: {sistema}")

#  Executa limpeza de RAM e reavalia se o valor saiu do estado crítico
def estado_ram_limpa(componente, valor, alerta, critico, metricas_func, sleep_seconds=None):
    try:
        # Executa a limpeza de RAM
        limpar_ram_global()

        # Define o tempo de espera após a limpeza
        if sleep_seconds is None:
            sleep_seconds = int(os.getenv("SLEEP_AFTER_CLEAN", "30"))
        time.sleep(sleep_seconds)

        # Obtém o novo valor do componente
        novo_valor = metricas_func().get(componente)
        if novo_valor is None:
            print(f"[ERRO] Não foi possível obter o valor atualizado para o componente: {componente}")
            return valor, False, False

        # Avalia os estados
        estado_restaurado = novo_valor < critico
        estado_alerta = alerta <= novo_valor < critico

        return novo_valor, estado_restaurado, estado_alerta

    except Exception as e:
        print(f"[ERRO] Falha ao executar estado_ram_limpa: {e}")
        return valor, False, False

#  Tenta ler temperatura via script externo (Linux)
def ler_temperatura():
    try:
        resultado = subprocess.run(
            ["bash", "./script/lm_sensors.sh"],
            capture_output=True,
            text=True
        )
        if resultado.returncode == 0:
            return f"{resultado.stdout.strip()}°C"
        return None  # sem saída válida
    except Exception:
        return None

#  Lê temperaturas de CPU, placa-mãe e GPU via script bash (Linux)
def ler_temperaturas_bash():
    """
    Executa o script lm_sensors.sh e retorna um dicionário com as temperaturas coletadas.
    Espera saída no formato:
      cpu_temp=XX
      mb_temp=YY
      gpu_temp=ZZ
    """
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
        return temps
    except Exception:
        return {}  # em caso de erro, retorna dicionário vazio

# INFO: Coleta de métricas específicas (comentário de rodapé para organização)