import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime

from config.settings import STATUS
from core.args import parse_args
from core.sistema import estado_ram_limpa
from core.monitor import metricas, formatar_metricas
from services.logger import gerar_log, registrar_evento

#  Gera timestamp com formato padrão
def timestamp(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.now().strftime(fmt)

#  Exibe mensagem se verbose=True
def log_verbose(msg, verbose):
    if verbose:
        print(f"[VERBOSE] {msg}")

#  Envia alerta por e-mail (simulado por padrão)
def enviar_email_alerta(mensagem, modo_teste=True):
    if not mensagem:
        print("⚠️ Nenhuma mensagem para enviar.")
        return
    if modo_teste:
        print(" [SIMULADO] Mensagem de e-mail:")
        print(mensagem)
        return

    # Dados do remetente e destinatário via .env
    remetente = os.getenv("EMAIL_USER")
    senha_app = os.getenv("EMAIL_PASS")
    destinatario = os.getenv("EMAIL_DEST")

    if not (remetente and senha_app and destinatario):
        print("⚠ Configurações de e-mail ausentes.")
        return

    # Monta e envia e-mail real
    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = remetente, destinatario, "Alerta de Métrica Crítica"
    msg.attach(MIMEText(mensagem, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(remetente, senha_app)
            servidor.sendmail(remetente, destinatario, msg.as_string())
        print(" E-mail enviado com sucesso!")
    except Exception as e:
        print(f" Falha ao enviar e-mail: {e}")

#  Verifica se o nome do componente é relacionado à memória
def _eh_memoria(nome):
    return str(nome).lower() in {"memoria", "memória", "ram"}

#  Avalia métricas e toma decisões (alerta, limpeza, registro)
def verificar_metricas(args):
    dados = metricas()
    snapshot_inicial = formatar_metricas(dados)
    print(snapshot_inicial)

    # Flags de estado
    estado_critico = False
    estado_alerta = False
    comp_disparo = None
    valor_disparo = None

    #  Identifica componente em alerta ou crítico
    for nome, valor in dados.items():
        if nome in STATUS and valor is not None:
            lim = STATUS[nome]
            if valor >= lim["critico"]:
                estado_critico = True
                comp_disparo = nome
                valor_disparo = valor
                break
            elif lim["alerta"] <= valor < lim["critico"] and not estado_critico:
                estado_alerta = True
                comp_disparo = nome
                valor_disparo = valor

    #  Se for memória crítica, tenta limpar
    houve_critico = estado_critico
    critico_memoria = False
    restaurado = False
    em_alerta_apos_limpeza = False
    valor_antes = valor_disparo
    valor_depois = None

    if estado_critico:
        if _eh_memoria(comp_disparo):
            critico_memoria = True
            lim_comp = STATUS[comp_disparo]
            novo_valor, restaurado, em_alerta_apos_limpeza = estado_ram_limpa(
                comp_disparo, valor_disparo, lim_comp["alerta"], lim_comp["critico"]
            )
            dados[comp_disparo] = novo_valor
            snapshot_pos = formatar_metricas(dados)
            valor_depois = novo_valor

            gerar_log(
                "acao_limpeza_ram",
                comp_disparo,
                valor_antes,
                valor_depois,
                f"ANTES:\n{snapshot_inicial}\n---\nDEPOIS:\n{snapshot_pos}\nrestaurado={restaurado}, em_alerta={em_alerta_apos_limpeza}"
            )

            if novo_valor >= lim_comp["critico"]:
                registrar_evento("alerta_crítico", comp_disparo, valor_antes, novo_valor, args, mensagem_extra=snapshot_pos)
                gerar_log("alerta_crítico", comp_disparo, valor_antes, novo_valor, snapshot_pos)
            elif em_alerta_apos_limpeza:
                gerar_log(
                    "restaurado_para_alerta",
                    comp_disparo,
                    valor_antes,
                    valor_depois,
                    f"Estava em crítico (memória), limpeza feita, permanece em ALERTA.\n{snapshot_pos}"
                )
            else:
                registrar_evento("restaurado", comp_disparo, valor_antes, valor_depois, args, mensagem_extra=snapshot_pos)
                gerar_log("restaurado", comp_disparo, valor_antes, valor_depois, snapshot_pos)
        else:
            registrar_evento("alerta_crítico", comp_disparo, valor_disparo, valor_disparo, args, mensagem_extra=snapshot_inicial)
    #  Reavalia se ainda há alerta após limpeza
    estado_alerta_atual = False
    comp_alerta = None
    valor_alerta = None
    for nome, valor in dados.items():
        if nome in STATUS and valor is not None:
            lim = STATUS[nome]
            if lim["alerta"] <= valor < lim["critico"]:
                estado_alerta_atual = True
                comp_alerta = nome
                valor_alerta = valor
                break

    snapshot_atual = formatar_metricas(dados)

    if estado_alerta_atual:
        if houve_critico and not critico_memoria:
            pass  # já tratado
        elif houve_critico and critico_memoria and restaurado and em_alerta_apos_limpeza:
            gerar_log(
                "restaurado_para_alerta",
                comp_alerta,
                valor_depois if valor_depois is not None else valor_alerta,
                valor_alerta,
                f"Tentativa de limpeza → permanece em ALERTA.\n{snapshot_atual}"
            )
        elif not houve_critico:
            registrar_evento("alerta_atenção", comp_alerta, valor_alerta, valor_alerta, args, mensagem_extra=snapshot_atual)
            gerar_log("alerta_atenção", comp_alerta, valor_alerta, valor_alerta, snapshot_atual)

    #  Se tudo está estável, registra
    if not houve_critico and not estado_alerta_atual:
        registrar_evento("sistema_estável", "todas", None, None, args, mensagem_extra=snapshot_inicial)
        gerar_log("sistema_estável", "todas", None, None, snapshot_inicial)

#  Executa o monitoramento conforme o modo escolhido
def executar(args):
    if args.modo == "contínuo":
        log_verbose(f"Iniciando monitoramento com intervalo {args.loop}s", args.verbose)
        try:
            while True:
                verificar_metricas(args)
                time.sleep(args.loop)
        except KeyboardInterrupt:
            print("\n[INFO] Monitoramento interrompido.")
    else:
        verificar_metricas(args)

#  Ponto de entrada do sistema
if __name__ == "__main__":
    executar(parse_args())