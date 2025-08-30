import time

from core.args import parse_args
from services.logger import registrar_evento, gerar_log
from core.monitor import metricas, formatar_metricas
from core.sistema import estado_ram_limpa
from services.helpers import enviar_email_alerta, log_verbose, timestamp

# 🔍 Identifica se o componente é relacionado à memória
def _eh_memoria(nome):
    return str(nome).lower() in {"memoria", "memória", "ram"}

# 🧠 Avalia métricas e toma decisões: alerta, limpeza, registro
def verificar_metricas(args):
    from config.settings import STATUS

    # 📍 Coleta inicial
    dados = metricas()
    snapshot_inicial = formatar_metricas(dados)
    print(snapshot_inicial)

    # 📍 Detecta estado inicial
    estado_critico = False
    comp_disparo = None
    valor_disparo = None

    for nome, valor in dados.items():
        if nome in STATUS and valor is not None:
            lim = STATUS[nome]
            if valor >= lim["critico"]:
                estado_critico, comp_disparo, valor_disparo = True, nome, valor
                break
            elif lim["alerta"] <= valor < lim["critico"] and not estado_critico:
                comp_disparo, valor_disparo = nome, valor

    # Flags de controle
    houve_critico = estado_critico
    critico_memoria = False
    restaurado = False
    em_alerta_apos_limpeza = False
    valor_antes = valor_disparo
    valor_depois = None

    # ===============================
    # 📍 TRATAMENTO CRÍTICO
    # ===============================
    if estado_critico:
        if _eh_memoria(comp_disparo):
            critico_memoria = True
            lim_comp = STATUS[comp_disparo]

            # Tenta corrigir via limpeza
            novo_valor, restaurado, em_alerta_apos_limpeza = estado_ram_limpa(
                comp_disparo, valor_disparo, lim_comp["alerta"], lim_comp["critico"]
            )
            dados[comp_disparo] = novo_valor
            snapshot_pos = formatar_metricas(dados)
            valor_depois = novo_valor

            # Log da ação corretiva
            gerar_log(
                "acao_limpeza_ram",
                comp_disparo,
                valor_antes,
                valor_depois,
                f"ANTES:\n{snapshot_inicial}\n---\nDEPOIS:\n{snapshot_pos}\n"
                f"restaurado={restaurado}, em_alerta={em_alerta_apos_limpeza}"
            )

            # Decide o tipo de evento após tentativa de correção
            if novo_valor >= lim_comp["critico"]:
                registrar_evento("alerta_crítico", comp_disparo, valor_antes, novo_valor, args, snapshot_pos)
            elif em_alerta_apos_limpeza:
                registrar_evento(
                    "restaurado_para_alerta", comp_disparo, valor_antes, valor_depois, args,
                    f"Estava em crítico (memória), limpeza feita, permanece em ALERTA.\n{snapshot_pos}"
                )
            else:
                registrar_evento("restaurado", comp_disparo, valor_antes, valor_depois, args, snapshot_pos)

        else:
            # Crítico não relacionado à memória
            registrar_evento("alerta_crítico", comp_disparo, valor_disparo, valor_disparo, args, snapshot_inicial)

    # ===============================
    # 📍 REAVALIAÇÃO ALERTA ATUAL
    # ===============================
    estado_alerta_atual = False
    comp_alerta = None
    valor_alerta = None

    for nome, valor in dados.items():
        if nome in STATUS and valor is not None:
            lim = STATUS[nome]
            if lim["alerta"] <= valor < lim["critico"]:
                estado_alerta_atual, comp_alerta, valor_alerta = True, nome, valor
                break

    snapshot_atual = formatar_metricas(dados)

    if estado_alerta_atual:
        if houve_critico and not critico_memoria:
            pass  # já tratado
        elif houve_critico and critico_memoria and restaurado and em_alerta_apos_limpeza:
            registrar_evento(
                "restaurado_para_alerta", comp_alerta,
                valor_depois if valor_depois is not None else valor_alerta,
                valor_alerta, args,
                f"Tentativa de limpeza → permanece em ALERTA.\n{snapshot_atual}"
            )
        elif not houve_critico:
            registrar_evento("alerta_atenção", comp_alerta, valor_alerta, valor_alerta, args, snapshot_atual)

    # ===============================
    # 📍 ESTÁVEL
    # ===============================
    if not houve_critico and not estado_alerta_atual:
        registrar_evento("sistema_estável", "todas", None, None, args, snapshot_inicial)

#  Executa o monitoramento conforme o modo escolhido
def executar(args):
    if args.modo == "contínuo":
        log_verbose(f"Iniciando monitoramento com intervalo {args.loop}s", args.verbose)
        try:
            while True:
                verificar_metricas(args)
                time.sleep(args.loop)
        except KeyboardInterrupt:
            print("\n[INFO] Monitoramento interrompido.")
    else:
        verificar_metricas(args)

#  Ponto de entrada do sistema
if __name__ == "__main__":
    executar(parse_args())