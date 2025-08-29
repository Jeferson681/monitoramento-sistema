# 🖥️ Monitoramento de Sistema

Este projeto realiza o monitoramento de recursos do sistema utilizando a biblioteca `psutil`, com suporte a execução contínua, alertas inteligentes e correções automáticas.

---

## 🚀 Funcionalidades

- Monitoramento de CPU, memória e disco em tempo real  
- Alertas configuráveis quando algum recurso ultrapassa limite  
- Correções automáticas simples (ex.: limpar RAM)  
- Execução contínua com logs detalhados e envio por e-mail  
- Suporte a execução local ou via Docker  

---

## 🛠️ Melhorias Futuras

- Implementar mais recursos de correção automática (ex.: finalizar processos, reiniciar drivers)  
- Criação de interface gráfica  
- Integração com scripts externos  

---

## 🛠️ Requisitos

- Python 3.9 ou superior  
- Bibliotecas listadas em `requirements.txt`  
- Docker (opcional, para containerização)  

---

## 🚀 Como executar

### Ambiente local

1. Instale as dependências:

```bash
pip install -r requirements.txt
