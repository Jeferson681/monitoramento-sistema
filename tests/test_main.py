# tests/test_main.py
from main import verificar_metricas

class Args:
    modo = "unico"
    loop = 1
    log = "console"
    verbose = False
    enviar = False

def test_verificar_metricas_sem_critico(mock_metricas):
    # Com mock_metricas, os valores estão em 50% → sem crítico
    verificar_metricas(Args())