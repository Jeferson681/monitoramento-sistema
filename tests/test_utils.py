from services.utils import log_verbose

def test_log_verbose_true(capsys):
    log_verbose("Teste utils", True)
    captured = capsys.readouterr()
    assert "[VERBOSE] Teste utils" in captured.out