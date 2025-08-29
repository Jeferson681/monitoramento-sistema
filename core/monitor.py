from core.sistema import obter_disco_principal, ler_temperatura
import psutil

def metricas():
    mem = psutil.virtual_memory()
    disco = psutil.disk_usage(obter_disco_principal())
    return {
        "cpu_total": psutil.cpu_percent(interval=None),
        "memoria_usada": mem.used / (1024 ** 3),
        "memoria_total": mem.total / (1024 ** 3),
        "memoria_percent": mem.percent,
        "disco_usado": disco.used / (1024 ** 3),
        "disco_total": disco.total / (1024 ** 3),
        "disco_percent": disco.percent,
        "temperatura": ler_temperatura()
    }

def formatar_metricas(dados, para_email=False):
    base = (
        f"CPU: {dados['cpu_total']:.1f}%\n"
        f"Memória: {dados['memoria_usada']:.1f} GB / {dados['memoria_total']:.1f} GB ({dados['memoria_percent']:.1f}%)\n"
        f"Disco: {dados['disco_usado']:.1f} GB / {dados['disco_total']:.1f} GB ({dados['disco_percent']:.1f}%)\n"
        f"Temperatura: {dados['temperatura'] or 'Indisponível'}"
    )
    return f"📊 MÉTRICAS ({dados.get('timestamp', '')})\n{base}" if para_email else base