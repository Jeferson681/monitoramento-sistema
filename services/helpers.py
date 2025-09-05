from datetime import datetime
from unittest.mock import patch

#  Gera timestamp no formato padrão do sistema
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#  Exibe mensagem no console se verbose=True
def log_verbose(msg, verbose=False):
    if verbose:
        print(f"[VERBOSE] {msg}")

# 🔍 Identifica se o componente é relacionado à memória
@patch("services.helpers._eh_memoria", return_value=True)
def _eh_memoria(nome):
    return str(nome).lower() in {"memoria", "memória", "ram"}