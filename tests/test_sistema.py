import core.sistema

def fake_metricas():
    return {"memoria_usada": 65.0}

def test_estado_ram_limpa_restaurado(monkeypatch):
    monkeypatch.setattr(core.sistema, "limpar_ram_global", lambda: None)
    novo_valor, restaurado, em_alerta = core.sistema.estado_ram_limpa(
        "memoria_usada", 95.0, 70.0, 90.0, fake_metricas, sleep_seconds=0
    )
    assert novo_valor < 90.0
    assert restaurado is True
    assert em_alerta is False