from core.args import parse_args

# ✅ Testa se os valores padrão são aplicados quando nenhum argumento é passado
def test_parse_args_default(monkeypatch):
    # Simula execução sem argumentos (como se fosse: python main.py)
    monkeypatch.setattr("sys.argv", ["main.py"])
    args = parse_args()

    # Verifica se os valores padrão foram aplicados corretamente
    assert args.modo == "unico"
    assert args.loop == 30