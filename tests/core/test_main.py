from src.main import executar

# ✅ Testa execução em modo contínuo com interrupção simulada
def test_executar_continuo_interrompido(monkeypatch, capsys):
    class Args:
        modo = "continuo"
        loop = 1
        log = "console"
        verbose = True
        enviar = False

    # Simula verificação + interrupção após primeira chamada
    def fake_verificar_metricas(args):
        print("🔁 Verificação rodada")
        raise KeyboardInterrupt

    monkeypatch.setattr("main.verificar_metricas", fake_verificar_metricas)
    monkeypatch.setattr("time.sleep", lambda s: None)

    executar(Args())  # Não precisa de try/except, já tratado no main

    captured = capsys.readouterr()
    assert "🔁 Verificação rodada" in captured.out
    assert "[INFO] Monitoramento interrompido." in captured.out