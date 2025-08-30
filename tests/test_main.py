# tests/test_main.py
from main import verificar_metricas

# 🔧 Simula argumentos padrão para execução única
class Args:
    modo = "unico"
    loop = 1
    log = "console"
    verbose = False
    enviar = False

# ✅ Testa execução sem estado crítico (valores mockados em 50%)
def test_verificar_metricas_sem_critico(mock_metricas):
    verificar_metricas(Args())