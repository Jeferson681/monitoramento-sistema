"""
Funções utilitárias para análise e extração de métricas dos logs do sistema.
Inclui cálculo de médias e parsing de linhas de log.
"""
import re
from datetime import datetime
import os
import json

def varrer_logs(diretorio_logs, padrao=(".log", ".jsonl")):
    """
    Retorna lista de arquivos de log encontrados no diretório e subdiretórios, conforme padrão.
    """
    if not os.path.isdir(diretorio_logs):
        return []
    arquivos = []
    for root, _, files in os.walk(diretorio_logs):
        for f in files:
            if any(f.endswith(ext) for ext in padrao):
                arquivos.append(os.path.join(root, f))
    return arquivos

def extrair_metricas_linha(linha):
    """
    Extrai métricas e valores relevantes de uma linha do log.
    Retorna lista de tuplas: (nome_metrica, valor, unidade).
    """
    if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", linha):
        linha = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s*", "", linha)
    resultados = []
    padrao = r"([A-Za-zÀ-ÿ\s\-]+):\s*([-\w\.]+)\s*(GB|MB|ms|%|°C)?"
    for nome, valor, unidade in re.findall(padrao, linha):
        try:
            if '.' in valor:
                v = float(valor)
            else:
                v = int(valor)
        except ValueError:
            v = valor
        u = unidade if unidade else ""
        resultados.append((nome.strip(), v, u))
    padrao_percent = r"([A-Za-zÀ-ÿ\s\-]+).*?\(([\d\.]+)%\)"
    for nome, valor in re.findall(padrao_percent, linha):
        resultados.append((nome.strip(), float(valor), "%"))
    return resultados

def calcular_media_logs_e_gerar_logs(diretorio_logs, log_text_path, log_json_path, tamanho_lote=20, padrao=(".log", ".jsonl")):
    """
    Calcula médias das métricas dos últimos logs, reconstrói o log e salva em arquivos .log e .jsonl.
    """
    arquivos = varrer_logs(diretorio_logs, padrao)
    if not arquivos:
        raise Exception("Nenhum arquivo de log encontrado para análise de médias.")
    linhas_logs = []
    for arquivo in arquivos:
        with open(arquivo, "r", encoding="utf-8") as f:
            linhas_logs.extend([linha for linha in f if linha.strip()])
    if not linhas_logs:
        raise Exception("Nenhuma linha de log encontrada para análise de médias.")

    metricas_lote = []
    for linha in linhas_logs[-tamanho_lote:]:
        metricas_lote.append(extrair_metricas_linha(linha))

    metricas_agregadas = {}
    for metricas in metricas_lote:
        for nome, valor, unidade in metricas:
            chave = (nome, unidade)
            metricas_agregadas.setdefault(chave, []).append(valor)

    metricas_media = []
    for (nome, unidade), valores in metricas_agregadas.items():
        valores_numericos = [v for v in valores if isinstance(v, (int, float))]
        if valores_numericos:
            media = sum(valores_numericos) / len(valores_numericos)
            metricas_media.append((nome, media, unidade))
        else:
            from collections import Counter
            mais_comum = Counter(valores).most_common(1)[0][0]
            metricas_media.append((nome, mais_comum, unidade))

    partes = []
    for nome, valor, unidade in metricas_media:
        if isinstance(valor, (int, float)):
            if unidade == "%":
                partes.append(f"{nome}: {valor:.2f}%")
            elif unidade == "GB":
                partes.append(f"{nome}: {valor:.2f} GB")
            elif unidade == "ms":
                partes.append(f"{nome}: {valor:.2f} ms")
            elif unidade == "°C":
                partes.append(f"{nome}: {valor:.2f}°C")
            else:
                partes.append(f"{nome}: {valor} {unidade}")
        else:
            partes.append(f"{nome}: {valor}{unidade}")
    log_linha = "\n".join(partes)

    with open(log_text_path, "w", encoding="utf-8") as f:
        f.write(log_linha + "\n")

    log_json = {
        "tipo": "media",
        "componente": None,
        "valor": None,
        "limite": None,
        "mensagem": log_linha,
        "timestamp": timestamp(),
    }
    with open(log_json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(log_json, ensure_ascii=False) + "\n")

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_verbose(msg, verbose=False):
    if verbose:
        print(f"[VERBOSE] {msg}")

def remover_logs_antigos(diretorio_logs, padrao=(".log", ".json"), dias=7):
    """
    Remove arquivos de log antigos (acima de 'dias') do diretório.
    Retorna quantidade removida.
    """
    if not os.path.isdir(diretorio_logs):
        return 0
    agora = datetime.now().timestamp()
    removidos = 0
    for f in os.listdir(diretorio_logs):
        if any(ext in f for ext in padrao):
            caminho_arquivo = os.path.join(diretorio_logs, f)
            try:
                mtime = os.path.getmtime(caminho_arquivo)
                if (agora - mtime) > dias * 86400:
                    os.remove(caminho_arquivo)
                    removidos += 1
            except Exception:
                pass
    return removidos