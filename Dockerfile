# 1. Imagem base
FROM python:3.10.9-slim

# 2. Diretório de trabalho no container
WORKDIR /app

# 3. Copiar os arquivos de dependência primeiro
COPY requirements.txt .

# 4. Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar o restante do projeto
COPY . .

# 6. Comando padrão
CMD ["python", "main.py"]