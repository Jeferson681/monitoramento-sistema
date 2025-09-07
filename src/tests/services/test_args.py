from core.args import parse_args

# ✅ Testa se os valores padrão são aplicados quando nenhum argumento é passado
def test_parse_args_default(monkeypatch):
    # Simula execução sem argumentos (como se fosse: python main.py)
    monkeypatch.setattr("sys.argv", ["main.py"])
    args = parse_args()

    # Verifica se os valores padrão foram aplicados corretamente
    assert args.modo == "unico"
    assert args.loop == 30
    assert args.ciclos is None
    assert args.log == "arquivo"
    assert args.verbose is False
    assert args.enviar is False

def test_parse_args_custom(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--modo", "continuo",
            "--loop", "10",
            "--ciclos", "5",
            "--log", "console",
            "--verbose",
            "--enviar"
        ]
    )
    args = parse_args()
    assert args.modo == "continuo"
    assert args.loop == 10
    assert args.ciclos == 5
    assert args.log == "console"
    assert args.verbose is True
    assert args.enviar is True