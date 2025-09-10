# 🖥️ Monitoramento de Sistema

Este projeto realiza o monitoramento de recursos do sistema utilizando a biblioteca `psutil`, com suporte a execução contínua, alertas inteligentes e correções automáticas.

---

## 🚀 Funcionalidades

- 📊 Monitoramento de CPU, memória e disco em tempo real  
- ⚠️ Alertas configuráveis quando algum recurso ultrapassa limite definido  
- 🧹 Correções automáticas simples (ex.: limpar RAM)  
- 📝 Execução contínua com logs detalhados e envio por e-mail  
- 🐳 Suporte a execução local ou via Docker  

---

## 🛠️ Melhorias Futuras

- 🔧 Implementar mais recursos de correção automática (ex.: finalizar processos, reiniciar drivers)  
- 💻 Criação de interface gráfica  
- 🔗 Integração com scripts externos  

---

## 📋 Requisitos

- Python **3.9** ou superior  
- Bibliotecas listadas em `requirements.txt`  
- Docker (opcional, para containerização)  

---

## 🚀 Como executar

### Ambiente local

1. Clone o repositório:
```bash
git clone https://github.com/Jeferson681/monitoramento-sistema.git
cd monitoramento-sistema
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o script principal:
```bash
python monitor.py
```

### Docker

1. Construa a imagem:
```bash
docker build -t monitoramento-sistema .
```

2. Execute o container:
```bash
docker run -d --name monitoramento-sistema monitoramento-sistema
```

---

## 🔎 Fluxo do Programa

O monitoramento é realizado em ciclos, podendo operar em dois modos:

### 1. **Modo Único**
- Executa uma única coleta de métricas do sistema (CPU, memória, disco, rede, etc.).
- Avalia o estado do sistema (crítico, alerta, estável).
- Registra eventos em log (arquivo ou console).
- Pode disparar envio de e-mail se configurado.

### 2. **Modo Contínuo**
- Executa ciclos infinitos ou limitados (parâmetro `--ciclos`).
- A cada ciclo:
  - Coleta métricas em tempo real.
  - Avalia estados críticos e alerta.
  - Executa correções automáticas (limpeza de RAM, disco, etc.) se necessário.
  - Registra eventos em log (arquivo texto e JSONL).
  - Aguarda o intervalo definido (`--loop`).
- Após 500 ciclos:
  - Se houver ≥250 estados críticos ou ≥400 estados de alerta, dispara envio de e-mail com médias dos últimos ciclos.
  - Trava o envio de e-mail por 45 minutos para evitar spam.
  - Gera log de médias agregadas dos últimos ciclos.
  - Limpa acumuladores e reinicia contagem de ciclos.

### 3. **Alertas e Correções**
- Estados críticos disparam correções automáticas e registro detalhado.
- Estados de alerta são registrados e podem gerar alertas por e-mail.
- Estados estáveis também são registrados para histórico.

### 4. **Logs e Métricas**
- Logs detalhados em arquivos texto e JSONL, com rotação diária.
- Cálculo de médias dos últimos 60 ciclos para análise agregada.
- Suporte a visualização em console ou arquivo.

### 5. **Configuração**
- Parâmetros via linha de comando ou variáveis de ambiente:
  - `--modo`: único ou contínuo
  - `--loop`: intervalo entre ciclos
  - `--ciclos`: número de ciclos (None = infinito)
  - `--log`: destino dos logs
  - `--verbose`: ativa logs detalhados
  - `--enviar`: ativa envio de e-mail

---

## 📧 Contato

- **E-mail:** seuemail@exemplo.com
- **GitHub:** [Jeferson681](https://github.com/Jeferson681)

---

## 📝 Notas Finais

- Este projeto é uma solução pessoal para monitoramento de sistema, sinta-se à vontade para contribuir ou adaptar para suas necessidades.
- Documentação completa disponível em [docs/](docs/).