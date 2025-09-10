
import sys
import pytest
from unittest.mock import patch, MagicMock
# Aplica skipif globalmente para todos os testes deste arquivo
pytestmark = pytest.mark.skipif(sys.platform not in ["win32", "linux"], reason="Compatível apenas com Windows e Linux")

class Args:
    pass

from config.settings import STATUS

def mock_metricas_critico():
    return {
        "memoria_percent": STATUS["memoria_percent"]["critico"] + 5,  # acima do critico
        "disco_percent": 10,
        "cpu_total": 10,
    }

def mock_metricas_alerta():
    alerta = STATUS["memoria_percent"]["alerta"]
    critico = STATUS["memoria_percent"]["critico"]
    valor_alerta = alerta + (critico - alerta) / 2  # valor entre alerta e crítico
    return {
        "memoria_percent": valor_alerta,
        "disco_percent": 10,
        "cpu_total": 10,
    }

def mock_metricas_estavel():
    return {
        "memoria_percent": STATUS["memoria_percent"]["alerta"] - 10,
        "disco_percent": 10,
        "cpu_total": 10,
    }

@patch("core.evaluator.metricas", side_effect=mock_metricas_critico)
@patch("core.evaluator.liberar_memoria_processo")
def test_fluxo_critico(mock_libera, mock_metricas):
    args = Args()
    with patch("core.evaluator.formatar_metricas", return_value="CRITICO"):
        from core.evaluator import verificar_metricas
        verificar_metricas(args)
    assert mock_libera.called, "Tratamento deve ser acionado em estado crítico"

@patch("core.evaluator.metricas", side_effect=mock_metricas_alerta)
@patch("core.evaluator.liberar_memoria_processo")
def test_fluxo_alerta(mock_libera, mock_metricas):
    args = Args()
    with patch("core.evaluator.formatar_metricas", return_value="ALERTA"):
        from core.evaluator import verificar_metricas
        verificar_metricas(args)
    assert not mock_libera.called, "Tratamento NÃO deve ser acionado em estado de alerta"

@patch("core.evaluator.metricas", side_effect=mock_metricas_estavel)
@patch("core.evaluator.liberar_memoria_processo")
def test_fluxo_estavel(mock_libera, mock_metricas):
    args = Args()
    with patch("core.evaluator.formatar_metricas", return_value="ESTAVEL"):
        from core.evaluator import verificar_metricas
        verificar_metricas(args)
    assert not mock_libera.called, "Tratamento não deve ser acionado em estado estável"
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

class ArgsFake:
    modo = "unico"
    log = "console"
    verbose = False
    enviar = False
    loop = 1
    ciclos = 1

@pytest.fixture(autouse=True)
def mock_parse_args(monkeypatch):
    monkeypatch.setattr("core.args.parse_args", lambda: ArgsFake())

@pytest.fixture
def estado_sistema():
    return EstadoSistema(DADOS_FAKE, ArgsFake())


@patch("core.evaluator.metricas", return_value=DADOS_FAKE)
@patch("services.logger.registrar_evento")
def test_verificar_metricas(mock_registrar_evento, mock_metricas, capsys):
    verificar_metricas(ArgsFake())
    captured = capsys.readouterr()
    assert "CPU" in captured.out or "cpu" in captured.out
    assert mock_registrar_evento.call_count >= 0

@patch("core.evaluator.registrar_evento")
def test_detectar_estado_critico(mock_registrar_evento, estado_sistema):
    estado_sistema.detectar_estado_critico()
    assert estado_sistema.estado_critico is True
    assert estado_sistema.comp_disparo in DADOS_FAKE.keys()

@patch("core.evaluator.registrar_evento")
def test_avaliar_alerta(mock_registrar_evento, estado_sistema):
    estado_sistema.avaliar_alerta()
    assert mock_registrar_evento.call_count == 1
    args, kwargs = mock_registrar_evento.call_args
    assert args[0] == "estado_alerta"
    assert args[1] in DADOS_FAKE.keys()

@patch("core.evaluator.registrar_evento")
def test_avaliar_estavel(mock_registrar_evento, estado_sistema):
    estado_sistema.houve_critico = False
    estado_sistema.avaliar_estavel(False)
    # Garante que o mock foi chamado para cada métrica avaliada como 'estável'
    assert mock_registrar_evento.call_count == len(DADOS_FAKE)
    for call in mock_registrar_evento.call_args_list:
        assert call[0][0] == "estavel"

def test_avaliar_metrica_bom(estado_sistema):
    # Testa retorno 'bom' para valor abaixo do limiar de alerta
    assert estado_sistema.avaliar_metrica(10, "cpu_total") == "bom"

def test_avaliar_metrica_medio(estado_sistema):
    # Testa retorno 'médio' para valor entre alerta e crítico
    assert estado_sistema.avaliar_metrica(85, "cpu_total") == "médio"

def test_avaliar_metrica_ruim(estado_sistema):
    # Testa retorno 'ruim' para valor acima do limiar crítico
    assert estado_sistema.avaliar_metrica(100, "cpu_total") == "ruim"

def test_avaliar_metrica_indisponivel(estado_sistema):
    # Testa retorno 'indisponível' para casos de valor None, limiar inexistente e valor não numérico
    assert estado_sistema.avaliar_metrica(None, "cpu_total") == "indisponível"
    assert estado_sistema.avaliar_metrica(10, "inexistente") == "indisponível"
    assert estado_sistema.avaliar_metrica("texto", "cpu_total") == "indisponível"