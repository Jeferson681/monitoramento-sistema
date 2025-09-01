# tests/test_utils.py

from src.services.utils import (
    log_verbose,
    timestamp,
    enviar_email_alerta
)

# ✅ Deve imprimir a mensagem quando verbose=True
def test_log_verbose_true(capsys):
    log_verbose("Teste utils", True)
    captured = capsys.readouterr()
    assert "[VERBOSE] Teste utils" in captured.out

# ✅ Não deve imprimir nada quando verbose=False
def test_log_verbose_false(capsys):
    log_verbose("Teste silencioso", False)
    captured = capsys.readouterr()
    assert captured.out == ""

# ✅ Retorna timestamp com formato padrão
def test_timestamp_default():
    ts = timestamp()
    assert isinstance(ts, str)
    assert len(ts) == 19  # "YYYY-MM-DD HH:MM:SS"

# ✅ Retorna timestamp com formato customizado
def test_timestamp_custom_format():
    ts = timestamp("%d/%m/%Y")
    assert "/" in ts

# ✅ Simula envio de e-mail com mensagem válida
def test_enviar_email_simulado_com_mensagem(capsys):
    enviar_email_alerta("Mensagem de teste", modo_teste=True)
    captured = capsys.readouterr()
    assert "[SIMULADO] Mensagem de e-mail:" in captured.out
    assert "Mensagem de teste" in captured.out

# ✅ Simula envio de e-mail sem mensagem
def test_enviar_email_simulado_sem_mensagem(capsys):
    enviar_email_alerta("", modo_teste=True)
    captured = capsys.readouterr()
    assert "⚠️ Nenhuma mensagem para enviar." in captured.out

# ✅ Testa envio real com variáveis ausentes
def test_enviar_email_real_sem_config(monkeypatch, capsys):
    monkeypatch.delenv("EMAIL_USER", raising=False)
    monkeypatch.delenv("EMAIL_PASS", raising=False)
    monkeypatch.delenv("EMAIL_DEST", raising=False)
    enviar_email_alerta("Mensagem real", modo_teste=False)
    captured = capsys.readouterr()
    assert "⚠ Configurações de e-mail ausentes." in captured.out