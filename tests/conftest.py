import os
import pytest

@pytest.fixture(autouse=True)
def _tmp_logs_dir(tmp_path, monkeypatch):
    #  Redireciona logs para pasta temporária isolada por teste
    tmp_logs = tmp_path / "logs"
    tmp_logs.mkdir()
    monkeypatch.setenv("PASTA_SERVICES", str(tmp_logs))
    monkeypatch.setenv("LOG_DIR", str(tmp_logs))
    return tmp_logs

@pytest.fixture
def mock_metricas(monkeypatch):
    #  Retorna métricas fixas para testes previsíveis
    def fake_metricas():
        return {
            "cpu_total": 50.0,
            "memoria_usada": 4.0,
            "memoria_total": 8.0,
            "memoria_percent": 50.0,
            "disco_usado": 100.0,
            "disco_total": 200.0,
            "disco_percent": 50.0,
            "temperatura": "45°C",
        }
    monkeypatch.setattr("core.monitor.metricas", fake_metricas)

@pytest.fixture
def mock_estado_ram(monkeypatch):
    #  Simula limpeza de RAM sem executar comandos reais
    monkeypatch.setattr("core.sistema.estado_ram_limpa", lambda *a, **k: (40.0, True, False))

@pytest.fixture(autouse=True)
def mock_sleep(monkeypatch):
    #  Remove delays nos testes
    monkeypatch.setattr("time.sleep", lambda s: None)

@pytest.fixture(autouse=True)
def mock_timestamp(monkeypatch):
    #  Timestamp fixo para facilitar asserts em logs
    monkeypatch.setattr("services.helpers.timestamp", lambda: "2025-01-01 00:00:00")
    monkeypatch.setattr("main.timestamp", lambda fmt="%Y-%m-%d %H:%M:%S": "2025-01-01 00:00:00")

@pytest.fixture(autouse=True)
def mock_temperatura(monkeypatch):
    #  Simula leitura de temperatura no monitor
    monkeypatch.setattr("core.monitor.ler_temperatura", lambda: "45°C")

@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    #  Bloqueia envio real de e-mail em qualquer ponto
    monkeypatch.setattr("services.helpers.enviar_email_alerta", lambda *a, **k: None)
    monkeypatch.setattr("main.enviar_email_alerta", lambda *a, **k: None)