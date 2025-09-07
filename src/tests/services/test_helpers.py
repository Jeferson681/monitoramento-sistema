from services.helpers import log_verbose, timestamp

#  Deve imprimir a mensagem quando verbose=True
def test_log_verbose_true(capsys):
    log_verbose("Mensagem de teste", True)
    captured = capsys.readouterr()
    assert "[VERBOSE] Mensagem de teste" in captured.out

#  Não deve imprimir nada quando verbose=False
def test_log_verbose_false(capsys):
    log_verbose("Mensagem de teste", False)
    captured = capsys.readouterr()
    assert captured.out == ""

def test_timestamp_format():
    ts = timestamp()
    # Verifica se o formato está correto: YYYY-MM-DD HH:MM:SS
    import re
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", ts)