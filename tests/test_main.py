from main import _eh_memoria

def test_eh_memoria_variacoes():
    assert _eh_memoria("memória")
    assert _eh_memoria("RAM")
    assert not _eh_memoria("cpu")