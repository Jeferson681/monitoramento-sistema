import os
import json
import pytest
from services.helpers import (
    varrer_logs,
    extrair_metricas_linha,
    calcular_media_logs_e_gerar_logs,
    timestamp,
    log_verbose,
    remover_logs_antigos,
)

def test_varrer_logs(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir(exist_ok=True)
    (log_dir / "a.log").write_text("teste")
    (log_dir / "b.jsonl").write_text("teste")
    (log_dir / "c.txt").write_text("teste")
    arquivos = varrer_logs(str(log_dir))
    assert any("a.log" in a for a in arquivos)
    assert any("b.jsonl" in a for a in arquivos)
    assert not any("c.txt" in a for a in arquivos)
    assert varrer_logs(str(tmp_path / "nao_existe")) == []

def test_extrair_metricas_linha():
    linha = "2025-09-09 12:00:00 CPU: 80 % RAM: 2.5 GB Temp: 40°C (Uso 75%)"
    metricas = extrair_metricas_linha(linha)
    nomes = [m[0] for m in metricas]
    assert "CPU" in nomes
    assert "RAM" in nomes
    assert "Temp" in nomes
    assert any(m[2] == "%" for m in metricas)
    assert any(m[2] == "GB" for m in metricas)
    assert any(m[2] == "°C" for m in metricas)

def test_calcular_media_logs_e_gerar_logs(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir(exist_ok=True)
    linhas = [
        "CPU: 80 % RAM: 2 GB Temp: 40°C",
        "CPU: 60 % RAM: 4 GB Temp: 30°C",
        "CPU: 100 % RAM: 6 GB Temp: 50°C",
    ]
    log_file = log_dir / "a.log"
    with open(log_file, "w", encoding="utf-8") as f:
        for l in linhas:
            f.write(l + "\n")
    log_text_path = tmp_path / "media.log"
    log_json_path = tmp_path / "media.jsonl"
    calcular_media_logs_e_gerar_logs(str(log_dir), str(log_text_path), str(log_json_path), tamanho_lote=3)
    assert log_text_path.exists()
    assert log_json_path.exists()
    with open(log_text_path, "r", encoding="utf-8") as f:
        conteudo = f.read()
        assert "CPU" in conteudo
        assert "RAM" in conteudo
        assert "Temp" in conteudo
    with open(log_json_path, "r", encoding="utf-8") as f:
        obj = json.loads(f.readline())
        assert obj["tipo"] == "media"
        assert "timestamp" in obj
        # Testa tratamento de exceções e manipulação de arquivos antigos/inexistentes
        with pytest.raises(Exception):
            calcular_media_logs_e_gerar_logs(str(tmp_path / "vazio"), str(log_text_path), str(log_json_path))

def test_timestamp():
    ts = timestamp()
    assert isinstance(ts, str)
    assert len(ts) >= 19

def test_log_verbose(capsys):
    log_verbose("mensagem", verbose=True)
    out = capsys.readouterr().out
    assert "[VERBOSE] mensagem" in out
    log_verbose("mensagem", verbose=False)
    out = capsys.readouterr().out
    assert out == ""

def test_remover_logs_antigos(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "a.log"
    log_file.write_text("teste")
    monkeypatch.setattr(os.path, "getmtime", lambda f: 0)  # Simula arquivo antigo
    monkeypatch.setattr(os, "remove", lambda f: log_file.unlink())
    removidos = remover_logs_antigos(str(log_dir), dias=1)
    assert removidos == 1
    # Testa diretório inexistente
    assert remover_logs_antigos(str(tmp_path / "nao_existe")) == 0
