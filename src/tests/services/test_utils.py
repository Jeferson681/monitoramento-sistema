import os
import pytest
import time
import json
from services.utils import (
    debug_log, pode_executar_tratamento, atualizar_cache_tratamento,
    enviar_email_alerta, liberar_memoria_processo, log_tratamento,
    liberar_ram_global, verificar_integridade_disco, limpar_arquivos_temporarios, registrar_top_processos_cpu,
    LOGS_JSON_DIR, LOGS_LOG_DIR
)
from services.helpers import timestamp, log_verbose

def test_timestamp_format():
    ts = timestamp()
    import re
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", ts)

def test_log_verbose_true(capsys):
    log_verbose("Mensagem de teste", True)
    captured = capsys.readouterr()
    assert "[VERBOSE] Mensagem de teste" in captured.out

def test_log_verbose_false(capsys):
    log_verbose("Mensagem de teste", False)
    captured = capsys.readouterr()
    assert captured.out == ""

def test_debug_log(tmp_path):
    arquivo = tmp_path / "debug_test.log"
    debug_log("Linha de debug", arquivo=str(arquivo))
    with open(arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read()
    assert "Linha de debug" in conteudo

def test_enviar_email_alerta_sem_mensagem(capsys):
    enviar_email_alerta("")
    captured = capsys.readouterr()
    assert "⚠️ Nenhuma mensagem para enviar." in captured.out

def test_enviar_email_alerta_sem_config(monkeypatch, capsys):
    monkeypatch.delenv("EMAIL_USER", raising=False)
    monkeypatch.delenv("EMAIL_PASS", raising=False)
    monkeypatch.delenv("EMAIL_TO", raising=False)
    enviar_email_alerta("Mensagem de teste")
    captured = capsys.readouterr()
    assert "⚠ Configurações de e-mail ausentes." in captured.out

def test_log_tratamento(tmp_path):
    logs_dir = tmp_path / "Logs"
    json_dir = logs_dir / "json"
    text_dir = logs_dir / "log"
    json_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    nome = "teste_log"
    log_data = {"teste": 123}
    texto = "Texto de log"
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("services.utils.LOGS_JSON_DIR", str(json_dir))
    monkeypatch.setattr("services.utils.LOGS_LOG_DIR", str(text_dir))
    log_tratamento(nome, log_data, texto)
    monkeypatch.undo()
    log_json = json_dir / f"{nome}.jsonl"
    log_txt = text_dir / f"{nome}.log"
    assert log_json.exists()
    assert log_txt.exists()
    with open(log_json, "r", encoding="utf-8") as f:
        linha = f.readline()
        obj = json.loads(linha)
        assert obj["teste"] == 123
        assert "timestamp" in obj
    with open(log_txt, "r", encoding="utf-8") as f:
        conteudo = f.read()
        assert "Texto de log" in conteudo

def test_pode_executar_tratamento_e_atualizar_cache():
    nome = "liberar_ram_global"
    assert pode_executar_tratamento(nome)
    atualizar_cache_tratamento(nome)
    assert not pode_executar_tratamento(nome)
    time.sleep(1)
    old_time = time.time() - 1801
    from services import utils
    utils.tratamento_cache[nome]["last_used"] = old_time
    assert pode_executar_tratamento(nome)

def test_liberar_memoria_processo_invalid_pid():
    assert liberar_memoria_processo(-1) is False

def test_liberar_ram_global(monkeypatch, capsys):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("psutil.virtual_memory", lambda: type("mem", (), {"percent": 50})())
    class DummyProc:
        info = {"pid": 1, "name": "python"}
    monkeypatch.setattr("psutil.process_iter", lambda attrs: [DummyProc()])
    monkeypatch.setattr("services.utils.liberar_memoria_processo", lambda pid: True)
    liberar_ram_global()
    captured = capsys.readouterr()
    assert "RAM antes:" in captured.out

def test_verificar_integridade_disco_windows(monkeypatch, capsys):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("platform.system", lambda: "Windows")
    class DummyResult:
        stdout = "não encontrou problemas"
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    verificar_integridade_disco()
    captured = capsys.readouterr()
    assert "Status: OK" in captured.out

def test_verificar_integridade_disco_linux(monkeypatch, capsys):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("platform.system", lambda: "Linux")
    class DummyResult:
        stdout = "clean"
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    verificar_integridade_disco()
    captured = capsys.readouterr()
    assert "Status: OK" in captured.out

def test_verificar_integridade_disco_erro(monkeypatch, capsys):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("platform.system", lambda: "Windows")
    def raise_exc(*a, **kw): raise Exception("erro")
    monkeypatch.setattr("subprocess.run", raise_exc)
    verificar_integridade_disco()
    captured = capsys.readouterr()
    assert "Status: ERRO" in captured.out

def test_limpar_arquivos_temporarios(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("platform.system", lambda: "Windows")
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    arquivo = temp_dir / "tempfile.txt"
    arquivo.write_text("abc")
    monkeypatch.setattr("tempfile.gettempdir", lambda: str(temp_dir))
    monkeypatch.setattr("os.walk", lambda d: [(str(temp_dir), [], ["tempfile.txt"])])
    monkeypatch.setattr("os.path.getsize", lambda f: 3)
    monkeypatch.setattr("os.remove", lambda f: None)
    limpar_arquivos_temporarios()
    captured = capsys.readouterr()
    assert "Arquivos removidos: 1" in captured.out

def test_registrar_top_processos_cpu(monkeypatch, capsys):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("psutil.cpu_count", lambda logical=True: 2)
    class DummyProc:
        info = {"pid": 1, "name": "python"}
        def cpu_percent(self, interval): return 80
        def status(self): return "running"
    monkeypatch.setattr("psutil.process_iter", lambda attrs: [DummyProc()])
    registrar_top_processos_cpu()
    captured = capsys.readouterr()
    assert "Top processos por uso de CPU" in captured.out