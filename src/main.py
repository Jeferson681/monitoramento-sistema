import time

from core.args import parse_args
from core.evaluator import verificar_metricas
from services.helpers import log_verbose


#  Executa o monitoramento conforme o modo escolhido
"""
Executa o monitoramento conforme o modo escolhido.
Gerencia modo contínuo e único, controle de ciclos e interrupções.
"""
def executar(args):
    if args.modo == "continuo":
        contador = 0
        try:
            while True:
                log_verbose(f"Iniciando monitoramento com intervalo {getattr(args, 'loop', 1)}s", args.verbose)
                contador += 1
                verificar_metricas(args, ciclo_atual=contador)
                if getattr(args, 'ciclos', None) is not None and args.ciclos > 0 and contador >= args.ciclos:
                    break
                time.sleep(getattr(args, 'loop', 1))
        except KeyboardInterrupt:
            print("\n[INFO] Monitoramento interrompido.")
        else:
            print("Fim do Ciclo")
    else:
        verificar_metricas(args)


#  Ponto de entrada do sistema
"""
Ponto de entrada do sistema.
"""
if __name__ == "__main__":
    args = parse_args()
    executar(args)