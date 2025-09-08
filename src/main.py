import time

from core.args import parse_args
from core.evaluator import verificar_metricas
from services.helpers import log_verbose


#  Executa o monitoramento conforme o modo escolhido
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
        # "Fim do Ciclo" só será exibido se o loop terminar normalmente (não por KeyboardInterrupt)
        else:
            print("Fim do Ciclo")
    else:
        verificar_metricas(args)


#  Ponto de entrada do sistema
if __name__ == "__main__":
    executar(parse_args())