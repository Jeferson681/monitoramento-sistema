import core.sistema

# 🔧 Simula função de métricas com valor seguro após limpeza
def fake_metricas():
    return {"memoria_usada": 65.0}

# ✅ Testa se a limpeza de RAM restaura o valor para fora do estado crítico
def test_estado_ram_limpa_restaurado(monkeypatch):
    # Evita execução real da limpeza
    monkeypatch.setattr(core.sistema, "limpar_ram_global", lambda: None)

    # Executa função com valor inicial crítico (95), limites de alerta (70) e crítico (90)
    novo_valor, restaurado, em_alerta = core.sistema.estado_ram_limpa(
        "memoria_usada", 95.0, 70.0, 90.0, fake_metricas, sleep_seconds=0
    )

    # Verifica se o valor foi restaurado com sucesso
    assert novo_valor < 90.0
    assert restaurado is True
    assert em_alerta is False