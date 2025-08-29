import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Monitoramento do sistema")
    parser.add_argument(
        "--modo",
        choices=["unico", "continuo"],
        default=os.getenv("MODO_PADRAO", "unico"),
        help="Modo de execução"
    )
    parser.add_argument(
        "--loop",
        type=int,
        default=int(os.getenv("LOOP_SECONDS", "30")),
        help="Intervalo em segundos no modo contínuo"
    )
    parser.add_argument(
        "--log",
        choices=["console", "arquivo"],
        default=os.getenv("DESTINO_LOG", "console"),
        help="Destino do log"
    )
    parser.add_argument("--verbose", action="store_true", help="Ativa logs verbosos")
    parser.add_argument("--enviar", action="store_true", help="Envia e-mail quando há evento")
    return parser.parse_args()