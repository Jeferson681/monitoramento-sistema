from services.helpers import log_verbose, enviar_email_alerta

def test_log_verbose_true(capsys):
    log_verbose("Mensagem de teste", True)
    captured = capsys.readouterr()
    assert "[VERBOSE] Mensagem de teste" in captured.out

def test_log_verbose_false(capsys):
    log_verbose("Mensagem de teste", False)
    captured = capsys.readouterr()
    assert captured.out == ""

