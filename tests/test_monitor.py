from core.monitor import metricas, formatar_metricas

def test_metricas_keys():
    dados = metricas()
    assert "cpu_total" in dados
    assert "memoria_usada" in dados
    assert "disco_total" in dados

def test_formatar_metricas_output():
    dados = {
        "cpu_total": 50.0,
        "memoria_usada": 4.0,
        "memoria_total": 8.0,
        "memoria_percent": 50.0,
        "disco_usado": 100.0,
        "disco_total": 200.0,
        "disco_percent": 50.0,
        "temperatura": "45°C"
    }
    texto = formatar_metricas(dados)
    assert "CPU: 50.0%" in texto
    assert "Temperatura: 45°C" in texto