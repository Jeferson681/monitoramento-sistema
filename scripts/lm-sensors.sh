#!/bin/bash

# Verifica se o comando 'sensors' está disponível
if ! command -v sensors &> /dev/null; then
    exit 1
fi

# Tenta extrair a temperatura do 'Package id 0'
TEMP=$(sensors | grep -m 1 'Package id 0:' | awk '{print $4}' | sed 's/+//;s/°C//')

# Se falhar, tenta 'Core 0'
if [ -z "$TEMP" ]; then
    TEMP=$(sensors | grep -m 1 'Core 0:' | awk '{print $3}' | sed 's/+//;s/°C//')
fi

# Se encontrou, imprime
if [ -n "$TEMP" ]; then
    echo "$TEMP"
    exit 0
else
    exit 2
fi