import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psutil
import ctypes
import shutil
import tempfile
import subprocess
import platform
import json
from services.helpers import timestamp, log_verbose

# Caminhos de logs padronizados (igual logger.py)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")
LOGS_JSON_DIR = os.path.join(LOGS_DIR, "json")
LOGS_LOG_DIR = os.path.join(LOGS_DIR, "log")
os.makedirs(LOGS_JSON_DIR, exist_ok=True)
os.makedirs(LOGS_LOG_DIR, exist_ok=True)

def enviar_email_alerta(mensagem):
    if not mensagem:
        print("⚠️ Nenhuma mensagem para enviar.")
        return

    remetente = os.getenv("EMAIL_USER")
    senha_app = os.getenv("EMAIL_PASS")
    destinatario = os.getenv("EMAIL_TO")
    host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    port = int(os.getenv("EMAIL_PORT", 587))

    if not (remetente and senha_app and destinatario):
        print("⚠ Configurações de e-mail ausentes.")
        return

    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = "Alerta de Métrica Crítica"
    msg.attach(MIMEText(mensagem, "plain"))

    try:
        with smtplib.SMTP(host, port) as servidor:
            servidor.starttls()
            servidor.login(remetente, senha_app)
            servidor.sendmail(remetente, destinatario, msg.as_string())
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {e}")

def debug_log(msg, arquivo=None):
    arquivo = arquivo or "debug.log"
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def liberar_memoria_processo(pid=None):
    if not pode_executar_tratamento("liberar_ram_global"):
        print("⏳ liberar_memoria_processo só pode ser executado a cada 30 minutos.")
        return False
    sistema = platform.system().lower()
    if sistema == "windows":
        # Libera memória de um processo específico ou de todos se pid for None
        def liberar(pid):
            try:
                PROCESS_SET_QUOTA = 0x0100
                PROCESS_QUERY_INFORMATION = 0x0400
                PROCESS_VM_READ = 0x0010
                handle = ctypes.windll.kernel32.OpenProcess(
                    PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                    False,
                    pid
                )
                if handle:
                    ctypes.windll.psapi.EmptyWorkingSet(handle)
                    ctypes.windll.kernel32.CloseHandle(handle)
                    return True
            except Exception:
                pass
            return False

        if pid is not None:
            return liberar(pid)
        else:
            total_limpos = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and "system" not in proc.info['name'].lower():
                        if liberar(proc.info['pid']):
                            total_limpos += 1
                except Exception:
                    continue
            return total_limpos  # retorna número de processos tratados

    elif sistema == "linux":
        # Limpa cache global de RAM
        uso_antes = psutil.virtual_memory().percent
        try:
            subprocess.run(["sync"])
            subprocess.run(["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"])
            time.sleep(2)
            uso_depois = psutil.virtual_memory().percent
            print(f"RAM antes: {uso_antes:.2f}% | RAM depois: {uso_depois:.2f}% | Limpeza global executada")
            return {"ram_before": uso_antes, "ram_after": uso_depois}
        except Exception as e:
            print(f"Erro ao liberar RAM no Linux: {e}")
            return False
    else:
        print("Sistema operacional não suportado para liberar memória.")
        return False

def log_tratamento(nome, log_data, texto=None):
    log_txt = os.path.join(LOGS_LOG_DIR, f"{nome}.log")
    log_json = os.path.join(LOGS_JSON_DIR, f"{nome}.jsonl")
    timestamp_str = timestamp()

    if texto:
        with open(log_txt, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp_str}] {texto}\n")

    log_data["timestamp"] = timestamp_str
    with open(log_json, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")

tratamento_cache = {
    "liberar_ram_global": {"last_used": 0, "count": 0, "interval": 1800},         # 30 min
    "verificar_integridade_disco": {"last_used": 0, "count": 0, "interval": 43200}, # 12h
    "limpar_arquivos_temporarios": {"last_used": 0, "count": 0, "interval": 604800}, # 7 dias
    "registrar_top_processos_cpu": {"last_used": 0, "count": 0, "interval": 1800},   # 30 min
}

def pode_executar_tratamento(nome):
    now = time.time()
    info = tratamento_cache[nome]
    return (now - info["last_used"]) >= info["interval"]

def atualizar_cache_tratamento(nome):
    tratamento_cache[nome]["last_used"] = time.time()
    tratamento_cache[nome]["count"] += 1


def verificar_integridade_disco(drive="C:"):
    if not pode_executar_tratamento("verificar_integridade_disco"):
        print("⏳ verificar_integridade_disco só pode ser executado a cada 12 horas.")
        return
    print("🔍 Iniciando tratamento: CPU Integridade")
    sistema = platform.system().lower()
    problemas = []
    instrucoes = ""
    try:
        if sistema == "windows":
            resultado = subprocess.run(
                ["chkdsk", drive],
                capture_output=True,
                text=True,
                encoding="cp850",
                check=False
            )
            saida = resultado.stdout
            if "não encontrou problemas" in saida or "no problems were found" in saida:
                status = "OK"
            else:
                status = "PROBLEMAS"
                problemas.append(saida)
                instrucoes = "Execute 'chkdsk /f' como administrador para tentar corrigir automaticamente."
        elif sistema == "linux":
            resultado = subprocess.run(
                ["sudo", "fsck", "-n", "/"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False
            )
            saida = resultado.stdout
            if "clean" in saida.lower():
                status = "OK"
            else:
                status = "PROBLEMAS"
                problemas.append(saida)
                instrucoes = "Execute 'sudo fsck -y /' para tentar corrigir automaticamente."
        else:
            status = "NÃO SUPORTADO"
            problemas.append("Sistema operacional não suportado.")
    except Exception as e:
        status = "ERRO"
        problemas.append(str(e))

    resultado = f"Status: {status} | Instruções: {instrucoes if instrucoes else 'Nenhuma'}"
    print(resultado)
    log_tratamento(
        "log_cpu_integridade",
        {
            "status": status,
            "problems": problemas,
            "instructions": instrucoes
        },
        texto=resultado
    )
    atualizar_cache_tratamento("verificar_integridade_disco")

def limpar_arquivos_temporarios():
    if not pode_executar_tratamento("limpar_arquivos_temporarios"):
        print("⏳ limpar_arquivos_temporarios só pode ser executado uma vez a cada 7 dias.")
        return
    print("🔍 Iniciando tratamento: Disco Limpeza")
    sistema = platform.system().lower()
    temp_dir = tempfile.gettempdir() if sistema == "windows" else "/tmp"
    arquivos_removidos = 0
    tamanho_liberado = 0

    for root, dirs, files in os.walk(temp_dir):
        for nome in files:
            caminho = os.path.join(root, nome)
            try:
                tamanho = os.path.getsize(caminho)
                os.remove(caminho)
                arquivos_removidos += 1
                tamanho_liberado += tamanho
            except Exception:
                continue

    resultado = f"Arquivos removidos: {arquivos_removidos} | Espaço liberado: {tamanho_liberado / (1024*1024):.2f} MB"
    print(resultado)
    log_tratamento(
        "log_disco",
        {
            "files_removed": arquivos_removidos,
            "space_freed_mb": tamanho_liberado / (1024*1024)
        },
        texto=resultado
    )
    atualizar_cache_tratamento("limpar_arquivos_temporarios")

def registrar_top_processos_cpu(top_n=5):
    if not pode_executar_tratamento("registrar_top_processos_cpu"):
        print("⏳ registrar_top_processos_cpu só pode ser executado a cada 30 minutos.")
        return
    
    print("🔍 Iniciando tratamento: Top Processos CPU")
    processos = []
    total_cpus = psutil.cpu_count(logical=True)
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'status']):
        try:
            if proc.info['pid'] == 0:
                continue  # Ignora processo ocioso do sistema
            uso_cpu = proc.cpu_percent(interval=0.1)
            uso_cpu_padrao = uso_cpu / total_cpus if total_cpus else uso_cpu
            processos.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu_percent": uso_cpu_padrao,
                "status": proc.status()
            })
        except Exception:
            continue

    top_processos = sorted(processos, key=lambda p: p["cpu_percent"], reverse=True)[:top_n]

    texto = "Top processos por uso de CPU (% padrão):\n"
    for p in top_processos:
        texto += f"PID {p['pid']} | {p['name']} | {p['cpu_percent']:.1f}% CPU | Status: {p['status']}\n"

    print(texto.strip())
    log_tratamento(
        "log_cpu_top",
        {
            "top_processos": top_processos
        },
        texto=texto.strip()
    )
    atualizar_cache_tratamento("registrar_top_processos_cpu")

#