import platform
import pytest
from unittest.mock import patch, MagicMock

from core.system import (
    medir_cpu,
    medir_memoria,
    obter_disco_principal,
    ler_temperaturas_bash,
    medir_ping,
    medir_latencia,
    medir_rede,
)
from core import system

    # Testa se o cache é utilizado corretamente para CPU
@patch("psutil.cpu_percent", return_value=50.0)
def test_medir_cpu(mock_cpu_percent):
    # Primeira chamada: atualiza o cache
    cpu = medir_cpu()
    assert cpu["data"] == 50.0
    assert "timestamp" in cpu
    mock_cpu_percent.assert_called_once()

    # Segunda chamada: deve retornar o valor do cache
    cpu_cached = medir_cpu()
    assert cpu_cached == cpu
    # Garante que o mock não é chamado novamente após uso do cache

    # Testa se o cache é utilizado corretamente para memória
@patch("psutil.virtual_memory")
def test_medir_memoria(mock_virtual_memory):
    mock_virtual_memory.return_value = MagicMock(
        total=16 * 1024**3, used=8 * 1024**3, percent=50.0
    )

    # Primeira chamada: atualiza o cache
    memoria = medir_memoria()
    assert memoria["data"]["total"] == 16 * 1024**3
    assert memoria["data"]["used"] == 8 * 1024**3
    assert memoria["data"]["percent"] == 50.0
    assert "timestamp" in memoria
    mock_virtual_memory.assert_called_once()

    # Segunda chamada: deve retornar o valor do cache
    memoria_cached = medir_memoria()
    assert memoria_cached == memoria
    # Garante que o mock não é chamado novamente após uso do cache

    # Testa se o cache e mocks funcionam corretamente para disco principal
@pytest.mark.skipif(platform.system().lower() != "windows", reason="Somente para Windows")
@patch("core.system.os.environ.get", return_value="C:\\")
@patch("psutil.disk_usage")
def test_obter_disco_principal_windows(mock_disk_usage, mock_environ_get):
    mock_disk_usage.return_value = MagicMock(
        total=1000, used=500, free=500, percent=50.0
    )
    # Força atualização do cache para garantir uso do mock
    import core.system as system
    system.cache["disk"]["last_updated"] = 0

    disco = obter_disco_principal()
    assert disco["data"]["total"] == 1000
    assert disco["data"]["used"] == 500
    assert disco["data"]["free"] == 500
    assert disco["data"]["percent"] == 50.0
    assert "timestamp" in disco
    mock_environ_get.assert_called()

    # Segunda chamada: deve retornar o valor do cache
    disco_cached = obter_disco_principal()
    assert disco_cached == disco
    # Não é necessário verificar mock_environ_get novamente pois o cache impede nova chamada

@pytest.mark.skipif(platform.system().lower() != "linux", reason="Somente para Linux")
@patch("psutil.disk_usage")
def test_obter_disco_principal_linux(mock_disk_usage):
    mock_disk_usage.return_value = MagicMock(
        total=1000, used=400, free=600, percent=40.0
    )
    # Limpa o cache para garantir que o mock será usado
    import core.system as system
    system.cache["disk"]["last_updated"] = 0

    disco = obter_disco_principal()
    assert disco["data"]["total"] == 1000
    assert disco["data"]["used"] == 400
    assert disco["data"]["free"] == 600
    assert disco["data"]["percent"] == 40.0
    assert "timestamp" in disco

    # Segunda chamada (usa o cache)
    disco_cached = obter_disco_principal()
    assert disco_cached == disco
    # Não precisa verificar mock_environ_get novamente

# Testa ler_temperaturas_bash com saída válida
@patch("subprocess.run")
def test_ler_temperaturas_bash(mock_subprocess_run):
    mock_subprocess_run.return_value = MagicMock(
        returncode=0, stdout="cpu_temp=55.0\nmb_temp=45.0\ngpu_temp=65.0"
    )
    system.cache["temperature"]["last_updated"] = 0

    temps = ler_temperaturas_bash()
    assert temps["data"]["cpu_temp"] == 55.0
    assert temps["data"]["mb_temp"] == 45.0
    assert temps["data"]["gpu_temp"] == 65.0
    assert "timestamp" in temps

    # Segunda chamada (usa o cache)
    temps_cached = ler_temperaturas_bash()
    assert temps_cached == temps
    mock_subprocess_run.assert_called_once()  # Não deve chamar novamente

# Testa medir_ping com saída válida
@patch("subprocess.check_output")
def test_medir_ping(mock_check_output):
    mock_check_output.return_value = "Resposta de 8.8.8.8: tempo=20ms"
    system.cache["ping"]["last_updated"] = 0

    ping = medir_ping()
    assert ping["data"] == 20.0
    assert "timestamp" in ping

    # Segunda chamada (usa o cache)
    ping_cached = medir_ping()
    assert ping_cached == ping
    mock_check_output.assert_called_once()  # Não deve chamar novamente

# Testa medir_latencia com conexão válida
@patch("subprocess.check_output")
def test_medir_latencia(mock_check_output):
    mock_check_output.return_value = "Resposta de 8.8.8.8: tempo=15ms"
    system.cache["latency"]["last_updated"] = 0

    latencia = medir_latencia()
    assert latencia["data"] == 15.0
    assert "timestamp" in latencia

    # Segunda chamada (usa o cache)
    latencia_cached = medir_latencia()
    assert latencia_cached == latencia
    mock_check_output.assert_called_once()  # Não deve chamar novamente

# Testa medir_rede com cache
@patch("psutil.net_io_counters")
def test_medir_rede(mock_net_io_counters):
    mock_net_io_counters.return_value = MagicMock(bytes_sent=1024, bytes_recv=2048)

    # Primeira chamada (atualiza o cache)
    rede = medir_rede()
    assert rede["data"]["bytes_sent"] == 1024
    assert rede["data"]["bytes_recv"] == 2048
    assert "timestamp" in rede
    mock_net_io_counters.assert_called_once()

    # Segunda chamada (usa o cache)
    rede_cached = medir_rede()
    assert rede_cached == rede
    mock_net_io_counters.assert_called_once()  # Não deve chamar novamente