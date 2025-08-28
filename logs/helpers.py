# helpers.py
from datetime import datetime

def timestamp():
    """Retorna timestamp no formato padrão do sistema."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_verbose(msg, verbose=False):
    """Exibe mensagem apenas se verbose=True."""
    if verbose:
        print(f"[VERBOSE] {msg}")

def enviar_email_alerta(conteudo):
    """Envia e-mail com o conteúdo recebido. Implementar SMTP/API."""
    # TODO: implementar envio real
    print(f"[EMAIL] Alerta enviado:\n{conteudo}")