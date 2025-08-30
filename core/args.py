import argparse
import os

# 🔧 Função que define os argumentos de execução do sistema
def parse_args():
    parser = argparse.ArgumentParser(description="Monitoramento do sistema")

    # --modo: define se roda uma vez ou em loop contínuo
    parser.add_argument(
        "--modo",
        choices=["unico", "continuo"],
        default=os.getenv("MODO_PADRAO", "unico"),  # pode vir do .env
        help="Modo de execução"
    )

    # --loop: intervalo entre execuções no modo contínuo
    parser.add_argument(
        "--loop",
        type=int,
        default=int(os.getenv("LOOP_SECONDS", "30")),  # pode vir do .env
        help="Intervalo em segundos no modo contínuo"
    )
    # --ciclos: número de execuções antes de encerrar (modo contínuo)
    parser.add_argument(
        "--ciclos",
        type=int,
        default=None,  # None = infinito
        help="Número de ciclos no modo contínuo (None = infinito)"
    )

    # --log: define onde os logs vão aparecer (console ou arquivo)
    parser.add_argument(
        "--log",
        choices=["console", "arquivo"],
        default=os.getenv("DESTINO_LOG", "console"),  # pode vir do .env
        help="Destino do log"
    )

    # --verbose: ativa logs detalhados
    parser.add_argument("--verbose", action="store_true", help="Ativa logs verbosos")

    # --enviar: ativa envio de e-mail em caso de evento
    parser.add_argument("--enviar", action="store_true", help="Envia e-mail quando há evento")

    return parser.parse_args()