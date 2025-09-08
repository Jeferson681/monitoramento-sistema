from core.evaluator import verificar_metricas, EstadoSistema
from unittest.mock import patch
import pytest

DADOS_FAKE = {
    "memoria_percent": 95,
    "cpu_total": 85,
    "ping_ms": 160,
    "latencia_tcp_ms": 155,
    "disco_percent": 97
}

@pytest.fixture(autouse=True)
def mock_parse_args(monkeypatch):
    class ArgsFake:
        modo = "teste"
        log = "arquivo"
        verbose = False
        enviar = False
    monkeypatch.setattr("core.args.parse_args", lambda: ArgsFake())

@pytest.fixture
def estado_sistema():
    return EstadoSistema(DADOS_FAKE, ArgsFake())

@patch("core.evaluator.metricas", return_value=DADOS_FAKE)
@patch("core.evaluator.registrar_evento")
@patch("core.evaluator.enviar_email_alerta")
def test_verificar_metricas(mock_enviar_email, mock_registrar_evento, mock_metricas, capsys):
    verificar_metricas(ArgsFake())
    captured = capsys.readouterr()
    assert "CPU" in captured.out or "cpu" in captured.out
    assert mock_registrar_evento.call_count >= 1
    assert mock_enviar_email.call_count >= 1

@patch("core.evaluator.registrar_evento")
@patch("core.evaluator.enviar_email_alerta")
def test_detectar_estado_critico(mock_enviar_email, mock_registrar_evento, estado_sistema):
    estado_sistema.detectar_estado_critico()
    assert estado_sistema.estado_critico is True
    assert estado_sistema.comp_disparo == "memoria_percent"
    assert mock_enviar_email.call_count == 1

@patch("core.evaluator.registrar_evento")
def test_avaliar_alerta(mock_registrar_evento, estado_sistema):
    estado_sistema.avaliar_alerta()
    assert mock_registrar_evento.call_count == 1
    mock_registrar_evento.assert_called_with(
        "alerta", "memoria_percent", 95, 95, estado_sistema.args, estado_sistema.snapshot_inicial
    )

@patch("core.evaluator.registrar_evento")
def test_avaliar_estavel(mock_registrar_evento, estado_sistema):
    estado_sistema.houve_critico = False
    estado_sistema.avaliar_estavel(False)
    mock_registrar_evento.assert_called_once_with(
        "estavel", None, None, None, estado_sistema.args, estado_sistema.snapshot_inicial
    )

def test_avaliar_metrica_bom(estado_sistema):
    # Valor abaixo do alerta
    assert estado_sistema._avaliar_metrica(10, "cpu_total") == "bom"

def test_avaliar_metrica_medio(estado_sistema):
    # Valor entre alerta e crítico
    assert estado_sistema._avaliar_metrica(85, "cpu_total") == "médio"

def test_avaliar_metrica_ruim(estado_sistema):
    # Valor acima do crítico
    assert estado_sistema._avaliar_metrica(100, "cpu_total") == "ruim"

def test_avaliar_metrica_indisponivel(estado_sistema):
    # Valor None
    assert estado_sistema._avaliar_metrica(None, "cpu_total") == "indisponível"
    # Limite não encontrado
    assert estado_sistema._avaliar_metrica(10, "inexistente") == "indisponível"
    # Valor não numérico
    assert estado_sistema._avaliar_metrica("texto", "cpu_total") == "indisponível"