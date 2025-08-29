# tests/conftest.py
import pytest

@pytest.fixture(autouse=True)
def _no_real_ram_clean(monkeypatch):
    monkeypatch.setattr("core.sistema.limpar_ram_global", lambda: None)