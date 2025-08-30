from services.utils import log_verbose

# ✅ Deve imprimir a mensagem quando verbose=True
def test_log_verbose_true(capsys):
    log_verbose("Teste utils", True)
    captured = capsys.readouterr()
    assert "[VERBOSE] Teste utils" in captured.out