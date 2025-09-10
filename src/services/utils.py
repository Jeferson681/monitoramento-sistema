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
from config.settings import DATE_STR

"""
Funções de tratamento e utilidades do monitoramento:
 - Limpeza de RAM, disco, integridade, logs
 - Envio de e-mail de alerta
Todas funções respeitam intervalos mínimos de execução para evitar sobrecarga.
"""
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")
LOGS_JSON_DIR = os.path.join(LOGS_DIR, "json")
LOGS_LOG_DIR = os.path.join(LOGS_DIR, "log")
os.makedirs(LOGS_JSON_DIR, exist_ok=True)
os.makedirs(LOGS_LOG_DIR, exist_ok=True)

def enviar_email_alerta(mensagem):
    """
    Envia alerta por e-mail usando configurações do ambiente.
    """
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
    """
    Registra mensagem de depuração em arquivo texto.
    """
    arquivo = arquivo or "debug.log"
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def liberar_memoria_processo(pid=None):
    """
    Libera memória RAM de processos (Windows/Linux), respeitando intervalo de execução.
    Exibe os processos que mais liberaram memória e registra log.
    """
    if not pode_executar_tratamento("liberar_ram_global"):
        print("⏳ liberar_memoria_processo só pode ser executado a cada 30 minutos.")
        return False
    print("🔍 Iniciando tratamento: Liberação de Memória")
    sistema = platform.system().lower()
    processos_liberados = []
    if sistema == "windows":
        def liberar(pid):
            try:
                proc = psutil.Process(pid)
                uso_antes = proc.memory_info().rss / (1024 * 1024)
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
                    uso_depois = proc.memory_info().rss / (1024 * 1024)
                    return proc.name(), uso_antes, uso_depois
            except Exception:
                pass
            return None

        if pid is not None:
            resultado = liberar(pid)
            if resultado:
                nome, antes, depois = resultado
                processos_liberados.append({
                    "pid": pid,
                    "name": nome,
                    "mem_before_mb": antes,
                    "mem_after_mb": depois
                })
        else:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and "system" not in proc.info['name'].lower():
                        resultado = liberar(proc.info['pid'])
                        if resultado:
                            nome, antes, depois = resultado
                            processos_liberados.append({
                                "pid": proc.info['pid'],
                                "name": nome,
                                "mem_before_mb": antes,
                                "mem_after_mb": depois
                            })
                except Exception:
                    continue

        # Ordena pelos que mais liberaram memória
        processos_liberados.sort(key=lambda p: p['mem_before_mb'] - p['mem_after_mb'], reverse=True)
        top5 = processos_liberados[:5]
        total_liberado = sum(p['mem_before_mb'] - p['mem_after_mb'] for p in top5)
        print(f"✅ Fim do tratamento: {len(top5)} processos relevantes. Total liberado (top 5): {total_liberado:.2f} MB")
        print("Prévia dos 2 processos que mais liberaram RAM:")
        for p in top5[:2]:
            liberado = p['mem_before_mb'] - p['mem_after_mb']
            print(f"{p['name']} liberado: {liberado:.2f} MB")
        texto_log = "\n".join([
            f"PID {p['pid']} | {p['name']} | RAM antes: {p['mem_before_mb']:.2f} MB | RAM depois: {p['mem_after_mb']:.2f} MB | Liberado: {(p['mem_before_mb'] - p['mem_after_mb']):.2f} MB"
            for p in top5
        ])
        texto_log = f"Total liberado (top 5): {total_liberado:.2f} MB\n" + texto_log
        log_tratamento(
            "log_liberar_memoria_processo",
            {"processos_liberados": top5, "total_liberado_mb": total_liberado},
            texto=texto_log
        )
        atualizar_cache_tratamento("liberar_ram_global")
        return len(processos_liberados)

    elif sistema == "linux":
        uso_antes = psutil.virtual_memory().percent
        try:
            subprocess.run(["sync"])
            subprocess.run(["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"])
            time.sleep(2)
            uso_depois = psutil.virtual_memory().percent
            texto = f"RAM antes: {uso_antes:.2f}% | RAM depois: {uso_depois:.2f}% | Limpeza global executada"
            print(texto)
            log_tratamento(
                "log_liberar_memoria_processo",
                {"ram_before": uso_antes, "ram_after": uso_depois},
                texto=texto
            )
            atualizar_cache_tratamento("liberar_ram_global")
            return {"ram_before": uso_antes, "ram_after": uso_depois}
        except Exception as e:
            print(f"Erro ao liberar RAM no Linux: {e}")
            return False
    else:
        print("Sistema operacional não suportado para liberar memória.")
        return False

def log_tratamento(nome, log_data, texto=None):
    """
    Registra dados de tratamento em arquivos de log texto e JSONL.
    """
    log_txt = os.path.join(LOGS_LOG_DIR, f"{nome}_{DATE_STR}.log")
    log_json = os.path.join(LOGS_JSON_DIR, f"{nome}_{DATE_STR}.jsonl")
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
    """
    Verifica se o tratamento pode ser executado (intervalo respeitado).
    """
    now = time.time()
    info = tratamento_cache[nome]
    return (now - info["last_used"]) >= info["interval"]

def atualizar_cache_tratamento(nome):
    """
    Atualiza cache de execução do tratamento.
    """
    tratamento_cache[nome]["last_used"] = time.time()
    tratamento_cache[nome]["count"] += 1


def verificar_integridade_disco(drive="C:"):
    """
    Verifica integridade do disco (Windows/Linux), respeitando intervalo de execução.
    Registra problemas e instruções no log.
    """
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
    print(f"✅ Fim do tratamento: Status {status}")
    log_tratamento(
        "log_cpu_integridade",
        {
            "status": status,
            "problems": problemas,
            "instructions": instrucoes
        },
        texto=f"Status: {status} | Instruções: {instrucoes if instrucoes else 'Nenhuma'}"
    )
    atualizar_cache_tratamento("verificar_integridade_disco")

def limpar_arquivos_temporarios():
    """
    Limpa arquivos temporários do sistema, respeitando intervalo de execução.
    Registra quantidade removida e espaço liberado.
    """
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

    print(f"✅ Fim do tratamento: {arquivos_removidos} arquivos removidos, {tamanho_liberado / (1024*1024):.2f} MB liberados")
    log_tratamento(
        "log_disco",
        {
            "files_removed": arquivos_removidos,
            "space_freed_mb": tamanho_liberado / (1024*1024)
        },
        texto=f"Arquivos removidos: {arquivos_removidos} | Espaço liberado: {tamanho_liberado / (1024*1024):.2f} MB"
    )
    atualizar_cache_tratamento("limpar_arquivos_temporarios")

def registrar_top_processos_cpu(top_n=5):
    """
    Registra os processos que mais consomem CPU, respeitando intervalo de execução.
    Exibe e registra os top processos por uso de CPU.
    """
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

    print(f"✅ Fim do tratamento: Top {top_n} processos exibidos.")
    print("Prévia dos top processos:")
    for p in top_processos:
        print(f"PID {p['pid']} | {p['name']} | {p['cpu_percent']:.1f}% CPU | Status: {p['status']}")
    log_tratamento(
        "log_cpu_top",
        {
            "top_processos": top_processos
        },
        texto="Top processos por uso de CPU (% padrão):\n" + "\n".join(
            f"PID {p['pid']} | {p['name']} | {p['cpu_percent']:.1f}% CPU | Status: {p['status']}" for p in top_processos
        )
    )
    atualizar_cache_tratamento("registrar_top_processos_cpu")
