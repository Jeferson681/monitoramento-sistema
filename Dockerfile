# Imagem base
FROM python:3.10.9-slim

# Diretório de trabalho
WORKDIR /app

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Adiciona instruções de uso ao Dockerfile
LABEL org.opencontainers.image.description="Monitoramento de Sistema: execute 'python src/main.py --help' para instruções."

# Comando padrão para execução contínua
ENTRYPOINT ["python", "src/main.py"]
CMD ["--modo", "continuo", "--loop", "30"]