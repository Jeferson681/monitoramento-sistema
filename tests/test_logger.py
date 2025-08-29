import os
from services.logger import gerar_log

def test_gerar_log_cria_arquivo():
    os.environ["PASTA_SERVICES"] = "services"
    gerar_log("teste", "cpu", 50, 60, "Mensagem de teste")
    assert os.path.exists("services/monitoramento.log")