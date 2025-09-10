import sys
import pytest
import os
import json
import pytest
from services.utils import (
    enviar_email_alerta,
    debug_log,
    liberar_memoria_processo,
    log_tratamento,
    verificar_integridade_disco,
    limpar_arquivos_temporarios,
    registrar_top_processos_cpu,
    DATE_STR,
)

def test_debug_log(tmp_path):
    log_file = tmp_path / "debug.log"
    debug_log("mensagem de teste", arquivo=str(log_file))
    assert log_file.exists()
    with open(log_file, "r", encoding="utf-8") as f:
        assert "mensagem de teste" in f.read()

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
    log_json = json_dir / f"{nome}_{DATE_STR}.jsonl"
    log_txt = text_dir / f"{nome}_{DATE_STR}.log"
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

def test_enviar_email_alerta(monkeypatch):
    monkeypatch.setenv("EMAIL_USER", "user@example.com")
    monkeypatch.setenv("EMAIL_PASS", "senha")
    monkeypatch.setenv("EMAIL_TO", "dest@example.com")
    monkeypatch.setenv("EMAIL_HOST", "smtp.example.com")
    monkeypatch.setenv("EMAIL_PORT", "587")
    class DummySMTP:
        def __init__(self, host, port): pass
        def starttls(self): pass
        def login(self, u, p): pass
        def sendmail(self, f, t, m): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
    monkeypatch.setattr("smtplib.SMTP", DummySMTP)
    enviar_email_alerta("teste mensagem")

@pytest.mark.skipif(sys.platform != "win32", reason="Somente no Windows")
def test_liberar_memoria_processo_windows(monkeypatch):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    class DummyProc:
        info = {"pid": 1, "name": "python"}
        def memory_info(self):
            class Info: rss = 100 * 1024 * 1024
            return Info()
        def name(self): return "python"
    monkeypatch.setattr("psutil.process_iter", lambda attrs: [DummyProc()])
    monkeypatch.setattr("ctypes.windll.kernel32.OpenProcess", lambda *a, **kw: 1)
    monkeypatch.setattr("ctypes.windll.psapi.EmptyWorkingSet", lambda h: True)
    monkeypatch.setattr("ctypes.windll.kernel32.CloseHandle", lambda h: True)
    result = liberar_memoria_processo()
    assert isinstance(result, int)

def test_verificar_integridade_disco_windows(monkeypatch):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("platform.system", lambda: "Windows")
    class DummyResult:
        stdout = "não encontrou problemas"
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    verificar_integridade_disco()

def test_verificar_integridade_disco_linux(monkeypatch):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("platform.system", lambda: "Linux")
    class DummyResult:
        stdout = "clean"
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    verificar_integridade_disco()

def test_verificar_integridade_disco_erro(monkeypatch):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("platform.system", lambda: "Windows")
    def raise_exc(*a, **kw): raise Exception("erro")
    monkeypatch.setattr("subprocess.run", raise_exc)
    verificar_integridade_disco()

def test_limpar_arquivos_temporarios(monkeypatch, tmp_path):
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

def test_registrar_top_processos_cpu(monkeypatch):
    monkeypatch.setattr("services.utils.pode_executar_tratamento", lambda n: True)
    monkeypatch.setattr("services.utils.atualizar_cache_tratamento", lambda n: None)
    monkeypatch.setattr("psutil.cpu_count", lambda logical=True: 2)
    class DummyProc:
        info = {"pid": 1, "name": "python"}
        def cpu_percent(self, interval): return 80
        def status(self): return "running"
    monkeypatch.setattr("psutil.process_iter", lambda attrs: [DummyProc()])
    registrar_top_processos_cpu()
