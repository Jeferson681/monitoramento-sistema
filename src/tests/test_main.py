import pytest
from main import executar

@pytest.mark.timeout(5)
def test_executar_continuo_interrompido(monkeypatch, capsys):
    class Args:
        modo = "continuo"
        loop = 1
        log = "console"
        verbose = True
        enviar = False

    def fake_verificar_metricas(args, ciclo_atual=None):
        print(f"🔁 Verificação rodada ciclo {ciclo_atual}")
        raise KeyboardInterrupt

    monkeypatch.setattr("main.verificar_metricas", fake_verificar_metricas)
    monkeypatch.setattr("time.sleep", lambda s: None)

    executar(Args())

    captured = capsys.readouterr()
    assert "🔁 Verificação rodada ciclo 1" in captured.out
    assert "[INFO] Monitoramento interrompido." in captured.out

@pytest.mark.timeout(5)
def test_executar_unico(monkeypatch, capsys):
    class Args:
        modo = "unico"
        loop = 1
        log = "console"
        verbose = True
        enviar = False

    def fake_verificar_metricas(args, ciclo_atual=None):
        print("🔁 Verificação rodada única")

    monkeypatch.setattr("main.verificar_metricas", fake_verificar_metricas)

    executar(Args())

    captured = capsys.readouterr()
    assert "🔁 Verificação rodada única" in captured.out

@pytest.mark.timeout(5)
def test_executar_continuo_limite(monkeypatch, capsys):
    class Args:
        modo = "continuo"
        loop = 1
        log = "console"
        verbose = True
        enviar = False
        ciclos = 2

    chamadas = []

    def fake_verificar_metricas(args, ciclo_atual=None):
        print(f"🔁 Verificação rodada ciclo {ciclo_atual}")
        chamadas.append(ciclo_atual)

    monkeypatch.setattr("main.verificar_metricas", fake_verificar_metricas)
    monkeypatch.setattr("time.sleep", lambda s: None)

    executar(Args())

    captured = capsys.readouterr()
    assert chamadas == [1, 2]
    assert "Fim do Ciclo" in captured.out