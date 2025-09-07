# tests/test_logger.py
import os
import json
from services.logger import registrar_evento

class DummyArgs:
    log = "arquivo"
    verbose = True
    enviar = False

def test_registrar_evento_cria_logs(tmp_path, monkeypatch):
    # Redefine diretórios temporários para logs
    logs_dir = tmp_path / "Logs"
    json_dir = logs_dir / "json"
    text_dir = logs_dir / "log"
    json_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("services.logger.LOGS_JSON_DIR", str(json_dir))
    monkeypatch.setattr("services.logger.LOGS_TEXT_DIR", str(text_dir))
    monkeypatch.setattr("services.logger.LOG_JSON_FILE", str(json_dir / "log_metricas_test.jsonl"))
    monkeypatch.setattr("services.logger.LOG_FILE", str(text_dir / "log_test.log"))

    args = DummyArgs()
    registrar_evento(
        tipo="alerta",
        componente="cpu_total",
        valor=95,
        limite=90,
        args=args,
        mensagem="CPU acima do limite!"
    )

    # Verifica se os arquivos foram criados e contém a mensagem esperada
    assert os.path.exists(str(json_dir / "log_metricas_test.jsonl"))
    assert os.path.exists(str(text_dir / "log_test.log"))

    with open(str(json_dir / "log_metricas_test.jsonl"), "r", encoding="utf-8") as f:
        linha = f.readline()
        log_json = json.loads(linha)
        assert log_json["tipo"] == "alerta"
        assert log_json["componente"] == "cpu_total"
        assert log_json["valor"] == 95
        assert log_json["mensagem"] == "CPU acima do limite!"

    with open(str(text_dir / "log_test.log"), "r", encoding="utf-8") as f:
        conteudo = f.read()
        assert "CPU acima do limite!" in conteudo
        assert "ALERTA - CPU_TOTAL" in conteudo.upper()
