# tests/test_logger.py
import os
from src.services.logger import gerar_log

# ✅ Testa se o log é criado corretamente no diretório temporário
def test_gerar_log_cria_arquivo(tmp_path, monkeypatch):
    # Reforça o uso do tmp_path como pasta de logs (apesar do conftest já definir)
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(exist_ok=True)
    monkeypatch.setenv("PASTA_SERVICES", str(logs_dir))

    # Gera um log de teste
    gerar_log("teste", "cpu_total", 50, 60, "Mensagem de teste")

    # Verifica se o arquivo foi criado e contém a mensagem esperada
    caminho = os.path.join(str(logs_dir), "monitoramento.log")
    assert os.path.exists(caminho)
    with open(caminho, "r", encoding="utf-8") as f:
        linha = f.readline()
        assert "Mensagem de teste" in linha