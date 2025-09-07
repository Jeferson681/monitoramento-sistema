from src.config.settings import STATUS
from src.core.monitor import metricas, formatar_metricas
from src.services.logger import registrar_evento
from src.services.utils import enviar_email_alerta
from src.core.system import medir_ping, medir_latencia

# 🧠 Avalia métricas e toma decisões: alerta, registro e envio de e-mails
class EstadoSistema:
    def __init__(self, dados, args):
        self.dados = dados
        self.args = args
        self.snapshot_inicial = formatar_metricas(dados)
        self.estado_critico = False
        self.comp_disparo = None
        self.valor_disparo = None
        self.houve_critico = False

    def _avaliar_metrica(self, valor, chave_status):
        if valor is None or isinstance(valor, dict):
            return "indisponível"
        lim = STATUS.get(chave_status)
        if lim is None or not isinstance(lim, dict):
            return "indisponível"
        if not isinstance(valor, (int, float)):
            return "indisponível"
        if valor < lim["alerta"]:
            return "bom"
        elif valor < lim["critico"]:
            return "médio"
        else:
            return "ruim"

    def detectar_estado_critico(self):
        for nome, valor in self.dados.items():
            if nome in STATUS and valor is not None:
                lim = STATUS[nome]
                if isinstance(valor, (int, float)) and valor >= lim["critico"]:
                    self.estado_critico = True
                    self.comp_disparo = nome
                    self.valor_disparo = valor
                    break
        self.houve_critico = self.estado_critico
        # Envia e-mail apenas em estado crítico
        if self.estado_critico:
            snapshot_atual = formatar_metricas(self.dados)
            enviar_email_alerta(
                f"🚨 Estado CRÍTICO detectado para {self.comp_disparo}!\n\n{snapshot_atual}"
            )

    def avaliar_alerta(self):
        estado_alerta_atual = False
        comp_alerta = None
        valor_alerta = None
        for nome, valor in self.dados.items():
            if nome in STATUS and valor is not None:
                lim = STATUS[nome]
                if isinstance(valor, (int, float)) and valor >= lim["alerta"]:
                    estado_alerta_atual = True
                    comp_alerta = nome
                    valor_alerta = valor
                    break
        snapshot_atual = formatar_metricas(self.dados)
        if estado_alerta_atual:
            registrar_evento(
                "alerta", comp_alerta, valor_alerta, valor_alerta, self.args, snapshot_atual
            )
        # Estado de ping e latência agora é exibido junto com as métricas formatadas
        return estado_alerta_atual

    def avaliar_estavel(self, estado_alerta_atual):
        if not self.houve_critico and not estado_alerta_atual:
            registrar_evento("estavel", None, None, None, self.args, formatar_metricas(self.dados))


def verificar_metricas(args):
    dados = metricas()
    estado = EstadoSistema(dados, args)
    print(formatar_metricas(dados))  # Exibe todas as métricas formatadas, incluindo ping e latência
    estado.detectar_estado_critico()
    alerta = estado.avaliar_alerta()
    estado.avaliar_estavel(alerta)
