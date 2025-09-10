def test_metricas_media_log_jsonl(tmp_path, monkeypatch):
    # Redefine diretórios temporários para logs
    logs_dir = tmp_path / "Logs"
    json_dir = logs_dir / "json"
    text_dir = logs_dir / "log"
    json_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("services.logger.LOGS_JSON_DIR", str(json_dir))
    monkeypatch.setattr("services.logger.LOGS_TEXT_DIR", str(text_dir))
    monkeypatch.setattr("services.logger.LOG_FILE", str(text_dir / "log_test.log"))
    # Cria 60 blocos de log completos no padrão real
    with open(str(text_dir / "log_test.log"), "w", encoding="utf-8") as f:
        for v in range(60):
            f.write("-"*70 + "\n")
            f.write(f"CPU: {v}.0%\n")
            f.write(f"Memória: {v}.0 GB / 100.0 GB ({v}.0%)\n")
            f.write(f"Disco: {v}.0 GB / 200.0 GB ({v}.0%)\n")
            f.write(f"Temperatura CPU: Indisponível°C\n")
            f.write(f"Temperatura Placa-mãe: Indisponível°C\n")
            f.write(f"Temperatura GPU: Indisponível°C\n")
            f.write(f"Ping: {v}.0 ms\n")
            f.write(f"Latência TCP: {v}.0 ms\n")
            f.write(f"Rede: {v}.0 MB enviados / {v}.0 MB recebidos\n")
            f.write("-"*70 + "\n")
    from services.logger import calcular_media_ultimos_blocos_log, DATE_STR
    media = calcular_media_ultimos_blocos_log()
    # Verifica se os arquivos foram criados
    metricas_media_log = text_dir / f"metricas_media_{DATE_STR}.log"
    metricas_media_json = json_dir / f"metricas_media_{DATE_STR}.jsonl"
    assert metricas_media_log.exists()
    assert metricas_media_json.exists()
    # Verifica conteúdo do log texto
    with open(metricas_media_log, "r", encoding="utf-8") as f:
        conteudo = f.read()
        # Deve conter bloco de média reconstruído
        assert "CPU:" in conteudo
        assert "Memória:" in conteudo
        assert "Disco:" in conteudo
        assert "Ping:" in conteudo
        assert "Latência TCP:" in conteudo
        assert "Rede:" in conteudo
        # A média dos valores deve ser 29.5 para cada métrica (média de 0 a 59)
        assert "29.5" in conteudo
    # Verifica conteúdo do log jsonl
    with open(metricas_media_json, "r", encoding="utf-8") as f:
        obj = json.loads(f.readline())
        # Médias esperadas por campo
        esperados = {
            "cpu": 29.5,
            "mem_usada": 29.5,
            "mem_total": 100.0,
            "mem_percent": 29.5,
            "disco_usado": 29.5,
            "disco_total": 200.0,
            "disco_percent": 29.5,
            "ping": 29.5,
            "latencia": 29.5,
            "rede_enviados": 29.5,
            "rede_recebidos": 29.5
        }
        for k, v in obj["media"].items():
            if v is not None:
                assert abs(v - esperados[k]) < 0.01, f"Campo {k}: {v} != {esperados[k]}"
        assert obj["ciclos"] == 60
        assert "timestamp" in obj
import pytest
from services import logger

def test_enviar_alerta_media_criticos_email(monkeypatch, tmp_path):
    # Simula 20 logs críticos
    logger.LOG_JSON_FILE = tmp_path / "log_metricas_test.jsonl"
    for v in range(20):
        with open(logger.LOG_JSON_FILE, "a", encoding="utf-8") as f:
            f.write('{"valor": 99, "tipo": "critico"}\n')
    called = {}
    def fake_email(msg):
        called["sent"] = msg
    monkeypatch.setattr(logger, "enviar_email_alerta", fake_email)
    logger.enviar_alerta_media_criticos([], None)
    assert "Alerta de média dos últimos estados críticos" in called["sent"]
    assert "99" in called["sent"]

def test_enviar_alerta_media_alertas_email(monkeypatch, tmp_path):
    # Simula 20 logs de alerta
    logger.LOG_JSON_FILE = tmp_path / "log_metricas_test.jsonl"
    for v in range(20):
        with open(logger.LOG_JSON_FILE, "a", encoding="utf-8") as f:
            f.write('{"valor": 88, "tipo": "alerta"}\n')
    called = {}
    def fake_email(msg):
        called["sent"] = msg
    monkeypatch.setattr(logger, "enviar_email_alerta", fake_email)
    logger.enviar_alerta_media_alertas([], None)
    assert "Alerta de média dos últimos estados de alerta" in called["sent"]
    assert "88" in called["sent"]
    # Testa criação e conteúdo dos logs temporários
import os
import json
from services.logger import registrar_evento

class DummyArgs:
    log = "arquivo"
    verbose = True
    enviar = False

def test_registrar_evento_cria_logs(tmp_path, monkeypatch):
    # Redefine diretórios temporários para logs para evitar efeitos colaterais
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
