from core.sistema import estado_ram_limpa

def fake_metricas():
    return {"memoria_usada": 65.0}

def test_estado_ram_limpa_restaurado():
    novo_valor, restaurado, em_alerta = estado_ram_limpa("memoria_usada", 95.0, 70.0, 90.0, fake_metricas, sleep_seconds=0)
    assert novo_valor < 90.0
    assert restaurado is True
    assert em_alerta is False

def test_estado_ram_limpa_alerta():
    novo_valor, restaurado, em_alerta = estado_ram_limpa("memoria_usada", 91.0, 70.0, 90.0, fake_metricas, sleep_seconds=0)
    assert novo_valor < 70.0
    assert em_alerta is False
    assert restaurado is True