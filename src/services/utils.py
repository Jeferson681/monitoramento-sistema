import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime



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

def debug_log(msg, arquivo="debug_ping.log"):
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
