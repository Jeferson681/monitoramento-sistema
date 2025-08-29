from config.status import parse_args

def test_parse_args_default(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py"])
    args = parse_args()
    assert args.modo == "único"
    assert args.loop == 30