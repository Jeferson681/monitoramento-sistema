import pytest

@pytest.fixture(autouse=True)
def _tmp_logs_dir(tmp_path, monkeypatch):
    tmp_logs = tmp_path / "logs"
    tmp_logs.mkdir()
    monkeypatch.setenv("PASTA_SERVICES", str(tmp_logs))
    monkeypatch.setenv("LOG_DIR", str(tmp_logs))
    return tmp_logs

@pytest.fixture
def mock_metricas(monkeypatch):
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

@pytest.fixture(autouse=True)
def mock_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)

@pytest.fixture(autouse=True)
def mock_timestamp(monkeypatch):
    monkeypatch.setattr("services.helpers.timestamp", lambda fmt="%Y-%m-%d %H:%M:%S": "2025-01-01 00:00:00")

@pytest.fixture(autouse=True)
def mock_temperatura(monkeypatch):
    monkeypatch.setattr("core.monitor.ler_temperaturas_bash", lambda: "45°C")

@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    monkeypatch.setattr("services.utils.enviar_email_alerta", lambda *a, **k: None)