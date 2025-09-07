from main import executar
import pytest

# Testa execução em modo contínuo com interrupção simulada
def test_executar_continuo_interrompido(monkeypatch, capsys):
    class Args:
        modo = "continuo"
        loop = 1
        log = "console"
        verbose = True
        enviar = False

    def fake_verificar_metricas(args):
        print("🔁 Verificação rodada")
        raise KeyboardInterrupt

    monkeypatch.setattr("main.verificar_metricas", fake_verificar_metricas)
    monkeypatch.setattr("time.sleep", lambda s: None)

    executar(Args())

    captured = capsys.readouterr()
    assert "🔁 Verificação rodada" in captured.out
    assert "[INFO] Monitoramento interrompido." in captured.out

# Testa execução em modo único (não contínuo)
def test_executar_unico(monkeypatch, capsys):
    class Args:
        modo = "unico"
        loop = 1
        log = "console"
        verbose = True
        enviar = False

    def fake_verificar_metricas(args):
        print("🔁 Verificação rodada única")

    monkeypatch.setattr("main.verificar_metricas", fake_verificar_metricas)

    executar(Args())

    captured = capsys.readouterr()
    assert "🔁 Verificação rodada única" in captured.out

# Testa execução em modo contínuo com número limitado de ciclos
def test_executar_continuo_limite(monkeypatch, capsys):
    class Args:
        modo = "continuo"
        loop = 1
        log = "console"
        verbose = True
        enviar = False
        ciclos = 2

    chamadas = []

    def fake_verificar_metricas(args):
        print("🔁 Verificação rodada ciclo")
        chamadas.append(1)

    monkeypatch.setattr("main.verificar_metricas", fake_verificar_metricas)
    monkeypatch.setattr("time.sleep", lambda s: None)

    executar(Args())

    captured = capsys.readouterr()
    assert chamadas == [1, 1]
    assert "Fim do Ciclo" in captured.out  # Corrigido aqui