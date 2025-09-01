from config.settings import STATUS
from core.monitor import metricas, formatar_metricas
from core.system import estado_ram_limpa
from services.helpers import _eh_memoria
from services.logger import gerar_log, registrar_evento

# 🧠 Avalia métricas e toma decisões: alerta, limpeza, registro
class EstadoSistema:
    def __init__(self, dados, args):
        self.dados = dados
        self.args = args
        self.snapshot_inicial = formatar_metricas(dados)
        self.estado_critico = False
        self.comp_disparo = None
        self.valor_disparo = None
        self.houve_critico = False
        self.critico_memoria = False
        self.restaurado = False
        self.em_alerta_apos_limpeza = False
        self.valor_antes = None
        self.valor_depois = None
        self.estado_ping = None
        self.estado_latencia = None

    def detectar_estado_critico(self):
        for nome, valor in self.dados.items():
            if nome in STATUS and valor is not None:
                lim = STATUS[nome]
                if valor >= lim["critico"]:
                    self.estado_critico = True
                    self.comp_disparo = nome
                    self.valor_disparo = valor
                    break
        self.houve_critico = self.estado_critico
        self.valor_antes = self.valor_disparo

        # Informativo de estado para ping e latência
        self.estado_ping = self._avaliar_estado_ping()
        self.estado_latencia = self._avaliar_estado_latencia()

    def _avaliar_estado_ping(self):
        valor = self.dados.get("ping_ms")
        if valor is None:
            return "indisponível"
        lim = STATUS.get("ping_ms")
        if valor < lim["alerta"]:
            return "bom"
        elif valor < lim["critico"]:
            return "médio"
        else:
            return "ruim"

    def _avaliar_estado_latencia(self):
        valor = self.dados.get("latencia_tcp_ms")
        if valor is None:
            return "indisponível"
        lim = STATUS.get("latencia_tcp_ms")
        if valor < lim["alerta"]:
            return "bom"
        elif valor < lim["critico"]:
            return "médio"
        else:
            return "ruim"

    def tratar_critico(self):
        if not self.estado_critico:
            return
        if _eh_memoria(self.comp_disparo):
            self.critico_memoria = True
            lim_comp = STATUS[self.comp_disparo]
            # Correção: passa a função metricas como argumento
            novo_valor, self.restaurado, self.em_alerta_apos_limpeza = estado_ram_limpa(
                self.comp_disparo, self.valor_disparo, lim_comp["alerta"], lim_comp["critico"], metricas
            )
            self.dados[self.comp_disparo] = novo_valor
            snapshot_pos = formatar_metricas(self.dados)
            self.valor_depois = novo_valor
            gerar_log(
                "acao_limpeza_ram",
                self.comp_disparo,
                self.valor_antes,
                self.valor_depois,
                f"ANTES:\n{self.snapshot_inicial}\n---\nDEPOIS:\n{snapshot_pos}\n"
                f"restaurado={self.restaurado}, em_alerta={self.em_alerta_apos_limpeza}"
            )
            if novo_valor >= lim_comp["critico"]:
                registrar_evento("alerta_crítico", self.comp_disparo, self.valor_antes, novo_valor, self.args, snapshot_pos)
            elif self.em_alerta_apos_limpeza:
                registrar_evento(
                    "restaurado_para_alerta", self.comp_disparo, self.valor_antes, self.valor_depois, self.args,
                    f"Estava em crítico (memória), limpeza feita, permanece em ALERTA.\n{snapshot_pos}"
                )
            else:
                registrar_evento("restaurado", self.comp_disparo, self.valor_antes, self.valor_depois, self.args, snapshot_pos)
        else:
            registrar_evento("alerta_crítico", self.comp_disparo, self.valor_disparo, self.valor_disparo, self.args, self.snapshot_inicial)

    def avaliar_alerta(self):
        estado_alerta_atual = False
        comp_alerta = None
        valor_alerta = None
        for nome, valor in self.dados.items():
            if nome in STATUS and valor is not None:
                lim = STATUS[nome]
                if valor >= lim["alerta"]:
                    estado_alerta_atual = True
                    comp_alerta = nome
                    valor_alerta = valor
                    break
        snapshot_atual = formatar_metricas(self.dados)
        if estado_alerta_atual:
            registrar_evento(
                "alerta", comp_alerta, self.valor_depois if self.valor_depois is not None else valor_alerta,
                valor_alerta, self.args, snapshot_atual
            )
        # Apenas informativo de estado de ping e latência
        registrar_evento(
            "estado_ping", "ping_ms", None, self.dados.get("ping_ms"), self.args, f"Estado do ping: {self.estado_ping}"
        )
        registrar_evento(
            "estado_latencia", "latencia_tcp_ms", None, self.dados.get("latencia_tcp_ms"), self.args, f"Estado da latência: {self.estado_latencia}"
        )
        return estado_alerta_atual

    def avaliar_estavel(self, estado_alerta_atual):
        if not self.houve_critico and not estado_alerta_atual:
            registrar_evento("estavel", None, None, None, self.args, formatar_metricas(self.dados))

def verificar_metricas(args):
    dados = metricas()
    estado = EstadoSistema(dados, args)
    print(estado.snapshot_inicial)
    estado.detectar_estado_critico()
    estado.tratar_critico()
    alerta = estado.avaliar_alerta()
    estado.avaliar_estavel(alerta)
