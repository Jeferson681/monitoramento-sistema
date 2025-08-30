from core.sistema import obter_disco_principal, ler_temperatura
import psutil

# 📡 Coleta métricas do sistema em tempo real
def metricas():
    mem = psutil.virtual_memory()  # dados de memória RAM
    disco = psutil.disk_usage(obter_disco_principal())  # uso do disco principal

    return {
        "cpu_total": psutil.cpu_percent(interval=None),  # uso total da CPU (%)
        "memoria_usada": mem.used / (1024 ** 3),         # memória usada (GB)
        "memoria_total": mem.total / (1024 ** 3),        # memória total (GB)
        "memoria_percent": mem.percent,                  # uso da memória (%)
        "disco_usado": disco.used / (1024 ** 3),         # disco usado (GB)
        "disco_total": disco.total / (1024 ** 3),        # disco total (GB)
        "disco_percent": disco.percent,                  # uso do disco (%)
        "temperatura": ler_temperatura()                 # temperatura (se disponível)
    }

# 🧾 Formata as métricas para exibição ou envio por e-mail
def formatar_metricas(dados, para_email=False):
    base = (
        f"CPU: {dados['cpu_total']:.1f}%\n"
        f"Memória: {dados['memoria_usada']:.1f} GB / {dados['memoria_total']:.1f} GB ({dados['memoria_percent']:.1f}%)\n"
        f"Disco: {dados['disco_usado']:.1f} GB / {dados['disco_total']:.1f} GB ({dados['disco_percent']:.1f}%)\n"
        f"Temperatura: {dados['temperatura'] or 'Indisponível'}"
    )

    # Se for para e-mail, inclui o timestamp no topo
    return f"📊 MÉTRICAS ({dados.get('timestamp', '')})\n{base}" if para_email else base