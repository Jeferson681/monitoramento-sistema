"""
Argumentos de linha de comando para o sistema de monitoramento.
Permite configurar modo de execução, intervalo, ciclos, destino de log, verbosidade e envio de e-mail.
Valores padrão podem ser definidos via variáveis de ambiente ou .env.
"""
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(
        description="Monitoramento do sistema",
        epilog="""
Exemplos de uso:
  python src/main.py --help
  python src/main.py --modo continuo --loop 10 --ciclos 20
  python src/main.py --modo unico --log console --verbose

No Docker:
  docker run --rm seu-usuario/monitoramento-sistema --help
  docker run --rm seu-usuario/monitoramento-sistema --modo continuo --loop 10 --ciclos 20
        """
    )

    # Modo de execução: único ou contínuo
    parser.add_argument(
        "--modo",
        choices=["unico", "continuo"],
        default=os.getenv("MODO_PADRAO", "unico"),
        help="Modo de execução: 'unico' (uma vez) ou 'continuo' (loop infinito)"
    )

    # Intervalo entre execuções no modo contínuo (segundos)
    parser.add_argument(
        "--loop",
        type=int,
        default=int(os.getenv("LOOP_SECONDS", "30")),
        help="Intervalo entre execuções no modo contínuo (segundos)"
    )

    # Número de ciclos antes de encerrar (apenas modo contínuo)
    parser.add_argument(
        "--ciclos",
        type=int,
        default=None,
        help="Número de ciclos no modo contínuo (None = infinito)"
    )

    # Destino dos logs: console ou arquivo
    parser.add_argument(
        "--log",
        choices=["console", "arquivo"],
        default=os.getenv("DESTINO_LOG", "arquivo"),
        help="Destino dos logs: 'console' ou 'arquivo'"
    )

    # Ativa logs detalhados (verbose)
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Ativa logs detalhados (verbose)"
    )

    # Ativa envio de e-mail em caso de evento
    parser.add_argument(
        "--enviar",
        action="store_true",
        help="Envia e-mail quando há evento crítico ou alerta"
    )

    return parser.parse_known_args()[0]