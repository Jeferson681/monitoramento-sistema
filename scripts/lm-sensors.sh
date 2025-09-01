#!/bin/bash

# Verifica se o comando 'sensors' está disponível
if ! command -v sensors &> /dev/null; then
    exit 1
fi

# Função para extrair temperatura de um label
get_temp() {
    local label="$1"
    sensors | grep -m 1 "$label" | awk '{for(i=1;i<=NF;i++) if($i ~ /\+[0-9]+/) print $i}' | sed 's/+//;s/°C//'
}

# CPU
CPU_TEMP=$(get_temp "Package id 0:")
[ -z "$CPU_TEMP" ] && CPU_TEMP=$(get_temp "Core 0:")

# GPU NVIDIA (se nvidia-smi disponível)
if command -v nvidia-smi &> /dev/null; then
    GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | head -n 1)
fi

# Placa-mãe (exemplo: temp1)
MB_TEMP=$(get_temp "temp1:")

# Disco (se smartctl disponível)
if command -v smartctl &> /dev/null; then
    DISK_TEMP=$(smartctl -A /dev/sda 2>/dev/null | awk '/Temperature_Celsius/ {print $10; exit}')
fi

# Exibe resultados encontrados
[ -n "$CPU_TEMP" ] && echo "CPU: $CPU_TEMP°C"
[ -n "$GPU_TEMP" ] && echo "GPU: $GPU_TEMP°C"
[ -n "$MB_TEMP" ] && echo "Motherboard: $MB_TEMP°C"
[ -n "$DISK_TEMP" ] && echo "Disk: $DISK_TEMP°C"

# Se nada foi encontrado, retorna erro
if [ -z "$CPU_TEMP" ] && [ -z "$GPU_TEMP" ] && [ -z "$MB_TEMP" ] && [ -z "$DISK_TEMP" ]; then
    exit 2
fi

exit 0