# tests/test_logger.py
import os
from services.logger import gerar_log

def test_gerar_log_cria_arquivo(tmp_path, monkeypatch):
    # O conftest já define PASTA_SERVICES, mas reforçamos aqui com o tmp_path do teste
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    monkeypatch.setenv("PASTA_SERVICES", str(logs_dir))

    gerar_log("teste", "cpu_total", 50, 60, "Mensagem de teste")

    caminho = os.path.join(str(logs_dir), "monitoramento.log")
    assert os.path.exists(caminho)
    with open(caminho, "r", encoding="utf-8") as f:
        linha = f.readline()
        assert "Mensagem de teste" in linha