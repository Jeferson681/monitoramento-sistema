import os
import pytest
from services.utils import enviar_email_alerta

# ✅ Testa envio real sem mensagem
def test_enviar_email_sem_mensagem(capsys):
    enviar_email_alerta("", modo_teste=False)
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

# ✅ (Opcional) Testa envio real com variáveis presentes — cuidado: envia de verdade!
@pytest.mark.skip(reason="Evita envio real durante testes automáticos")
def test_enviar_email_real_com_config(monkeypatch, capsys):
    monkeypatch.setenv("EMAIL_USER", "seu_email@gmail.com")
    monkeypatch.setenv("EMAIL_PASS", "senha_app")
    monkeypatch.setenv("EMAIL_DEST", "destinatario@gmail.com")
    enviar_email_alerta("Mensagem real", modo_teste=False)
    captured = capsys.readouterr()
    assert "E-mail enviado com sucesso!" in captured.out or "Falha ao enviar e-mail:" in captured.out