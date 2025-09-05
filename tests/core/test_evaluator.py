from core.evaluator import verificar_metricas, EstadoSistema
from unittest.mock import patch
import pytest

# Dados simulados para os testes
DADOS_FAKE = {
    "memoria_percent": 95,
    "cpu_total": 85,
    "ping_ms": 160,
    "latencia_tcp_ms": 155,
    "disco_percent": 97
}

ARGS_FAKE = {"modo": "teste"}

@pytest.fixture
def estado_sistema():
    with patch("core.evaluator.formatar_metricas", return_value="snapshot_fake"):
        return EstadoSistema(DADOS_FAKE, ARGS_FAKE)

@patch("core.evaluator.metricas", return_value=DADOS_FAKE)
@patch("core.evaluator.formatar_metricas", return_value="snapshot_fake")
@patch("core.evaluator.registrar_evento")
def test_verificar_metricas(mock_registrar_evento, mock_formatar_metricas, mock_metricas):
    verificar_metricas(ARGS_FAKE)
    assert mock_registrar_evento.call_count >= 1

@patch("core.evaluator.registrar_evento")
def test_tratar_critico(mock_registrar_evento, estado_sistema):
    estado_sistema.detectar_estado_critico()
    estado_sistema.tratar_critico()
    mock_registrar_evento.assert_called_once_with(
        "alerta_crítico", "memoria_percent", 95, 95, ARGS_FAKE, "snapshot_fake"
    )

@patch("core.evaluator.registrar_evento")
def test_avaliar_alerta(mock_registrar_evento, estado_sistema):
    estado_sistema.avaliar_alerta()
    assert mock_registrar_evento.call_count >= 1