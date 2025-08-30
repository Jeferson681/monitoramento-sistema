# helpers.py
from datetime import datetime

#  Gera timestamp no formato padrão do sistema
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#  Exibe mensagem no console se verbose=True
def log_verbose(msg, verbose=False):
    if verbose:
        print(f"[VERBOSE] {msg}")

#  Simula envio de e-mail com o conteúdo recebido
def enviar_email_alerta(conteudo):
    # TODO: implementar envio real via SMTP ou API
    print(f"[EMAIL] Alerta enviado:\n{conteudo}")