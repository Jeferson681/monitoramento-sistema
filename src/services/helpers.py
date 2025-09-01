from datetime import datetime

#  Gera timestamp no formato padrão do sistema
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#  Exibe mensagem no console se verbose=True
def log_verbose(msg, verbose=False):
    if verbose:
        print(f"[VERBOSE] {msg}")

# 🔍 Identifica se o componente é relacionado à memória
def _eh_memoria(nome):
    return str(nome).lower() in {"memoria", "memória", "ram"}