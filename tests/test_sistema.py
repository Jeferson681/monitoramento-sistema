import pytest

import core.sistema
import platform
import subprocess

#  Testa limpeza de RAM simulando ambiente Windows
@pytest.mark.skipif(platform.system() != "Windows", reason="Somente para Windows")
def test_limpar_ram_windows(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(core.sistema.ctypes.windll.kernel32, "OpenProcess", lambda *a, **k: 1)
    monkeypatch.setattr(core.sistema.ctypes.windll.psapi, "EmptyWorkingSet", lambda h: None)
    monkeypatch.setattr(core.sistema.ctypes.windll.kernel32, "CloseHandle", lambda h: None)
    monkeypatch.setattr(core.sistema.psutil, "process_iter", lambda attrs: [{"info": {"pid": 1234}}])
    core.sistema.limpar_ram_global()


#  Testa limpeza de RAM simulando ambiente Linux
def test_limpar_ram_linux(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(core.sistema.os, "system", lambda cmd: None)
    core.sistema.limpar_ram_global()

#  Testa leitura de temperatura com saída válida
def test_ler_temperatura_ok(monkeypatch):
    class Resultado:
        returncode = 0
        stdout = "55"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Resultado())
    temp = core.sistema.ler_temperatura()
    assert temp == "55°C"

#  Testa leitura de temperatura com falha
def test_ler_temperatura_falha(monkeypatch):
    class Resultado:
        returncode = 1
        stdout = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Resultado())
    temp = core.sistema.ler_temperatura()
    assert temp is None