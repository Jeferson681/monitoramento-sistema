from core.monitor import metricas, formatar_metricas

# ✅ Garante que as chaves principais estão presentes nas métricas
def test_metricas_keys():
    dados = metricas()
    assert "cpu_total" in dados
    assert "memoria_usada" in dados
    assert "disco_total" in dados
    assert "temperatura_cpu" in dados
    assert "temperatura_motherboard" in dados
    assert "temperatura_gpu" in dados
    assert "ping_ms" in dados
    assert "latencia_tcp_ms" in dados
    assert "rede_bytes_enviados" in dados
    assert "rede_bytes_recebidos" in dados
    assert "timestamp" in dados

# 🧾 Verifica se a saída formatada contém os dados esperados
def test_formatar_metricas_output():
    dados = {
        "cpu_total": 50.0,
        "memoria_usada": 4.0,
        "memoria_total": 8.0,
        "memoria_percent": 50.0,
        "disco_usado": 100.0,
        "disco_total": 200.0,
        "disco_percent": 50.0,
        "temperatura_cpu": "45",
        "temperatura_motherboard": "40",
        "temperatura_gpu": "38",
        "ping_ms": 10,
        "latencia_tcp_ms": 12,
        "rede_bytes_enviados": 1024 * 1024 * 10,
        "rede_bytes_recebidos": 1024 * 1024 * 20,
        "timestamp": "2025-09-07 12:00:00"
    }
    texto = formatar_metricas(dados)
    assert "CPU: 50.0%" in texto
    assert "Memória: 4.0 GB / 8.0 GB (50.0%)" in texto
    assert "Disco: 100.0 GB / 200.0 GB (50.0%)" in texto
    assert "Temperatura CPU: 45°C" in texto
    assert "Temperatura Placa-mãe: 40°C" in texto
    assert "Temperatura GPU: 38°C" in texto
    assert ("Ping: 10 ms" in texto) or ("Ping: 10.0 ms" in texto)
    assert "Latência TCP: 12 ms" in texto
    assert "Rede: 10.0 MB enviados / 20.0 MB recebidos" in texto