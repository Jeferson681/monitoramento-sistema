"""
Lógica de avaliação de métricas, estados críticos/alerta/estável e tratamentos do sistema.
Centraliza controle de ciclo, registro de eventos e disparo de alertas.
"""
import time
from config.settings import STATUS
from core.monitor import metricas, formatar_metricas
from services.logger import registrar_evento
from services.utils import (
    liberar_memoria_processo,
    limpar_arquivos_temporarios,
    verificar_integridade_disco
)

class EstadoSistema:
    ultimo_envio_email = 0
    """
    Representa o estado do sistema monitorado, incluindo métricas do ciclo atual e controle de eventos.
    Usada em cada ciclo para avaliar, tratar e registrar estados críticos, alerta e estável.
    """
    ultima_limpeza = 0
    ultima_integridade = 0
    ultima_memoria = 0
    estados_criticos_antes = []
    estados_criticos_depois = []
    estados_alerta = []
    estados_alerta_antes = []
    estados_alerta_depois = []
    ciclos_total = 0
    def __init__(self, dados, args):
        self.dados = dados
        self.args = args
        self.snapshot_inicial = formatar_metricas(dados)
        self.estado_critico = False
        self.comp_disparo = None
        self.valor_disparo = None
        self.houve_critico = False

    def avaliar_metrica(self, valor, chave_status):
        """
        Avalia uma métrica individual segundo os limites definidos em STATUS.
        Usada principalmente em testes para garantir a lógica de classificação das métricas.
        """
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
        return "ruim"

    def detectar_estado_critico(self):
        """
        Detecta se há estado crítico em alguma métrica do ciclo atual.
        Executa tratamento específico, registra eventos antes/depois e dispara alerta por e-mail se necessário.
        Usada em cada ciclo pelo fluxo principal (verificar_metricas).
        """
        critico_antes = None
        for nome, valor in self.dados.items():
            if nome in STATUS and valor is not None:
                lim = STATUS[nome]
                if isinstance(valor, (int, float)) and valor >= lim["critico"]:
                    critico_antes = (nome, valor)
                    break
        self.estado_critico = bool(critico_antes)
        self.comp_disparo = critico_antes[0] if critico_antes else None
        self.valor_disparo = critico_antes[1] if critico_antes else None
        self.houve_critico = self.estado_critico

        if self.estado_critico:
            snapshot_antes = formatar_metricas(self.dados)
            EstadoSistema.estados_criticos_antes.append(self.dados.copy())
            registrar_evento(
                "estado_critico",
                self.comp_disparo,
                self.valor_disparo,
                STATUS[self.comp_disparo]["critico"] if self.comp_disparo else None,
                self.args,
                f"Estado crítico valores>>> Antes do tratamento: {snapshot_antes}"
            )
            agora = time.time()
            if self.comp_disparo == "disco_percent":
                if agora - EstadoSistema.ultima_limpeza > 30:
                    limpar_arquivos_temporarios()
                    EstadoSistema.ultima_limpeza = agora
                if agora - EstadoSistema.ultima_integridade > 30:
                    verificar_integridade_disco()
                    EstadoSistema.ultima_integridade = agora
            elif self.comp_disparo == "memoria_percent":
                if agora - EstadoSistema.ultima_memoria > 30:
                    liberar_memoria_processo()
                    EstadoSistema.ultima_memoria = agora
            time.sleep(5)
            critico_depois = None
            for nome, valor in self.dados.items():
                if nome in STATUS and valor is not None:
                    lim = STATUS[nome]
                    if isinstance(valor, (int, float)) and valor >= lim["critico"]:
                        critico_depois = (nome, valor)
                        break
            self.estado_critico = bool(critico_depois)
            self.comp_disparo = critico_depois[0] if critico_depois else None
            self.valor_disparo = critico_depois[1] if critico_depois else None
            self.houve_critico = self.estado_critico

            snapshot_depois = formatar_metricas(self.dados)
            EstadoSistema.estados_criticos_depois.append(self.dados.copy())

            if self.estado_critico:
                registrar_evento(
                    "estado_critico",
                    self.comp_disparo,
                    self.valor_disparo,
                    STATUS[self.comp_disparo]["critico"] if self.comp_disparo else None,
                    self.args,
                    f"Estado crítico valores>>> Permaneceu crítico após tratamento. Depois: {snapshot_depois}"
                )
            else:
                registrar_evento(
                    "estado_critico",
                    critico_antes[0] if critico_antes else None,
                    critico_antes[1] if critico_antes else None,
                    STATUS[critico_antes[0]]["critico"] if critico_antes else None,
                    self.args,
                    f"Estado crítico valores>>> Corrigido após tratamento. Antes: {snapshot_antes} | Depois: {snapshot_depois}"
                )

    def avaliar_alerta(self):
        """
        Avalia se há estado de alerta em alguma métrica do ciclo atual.
        Executa tratamento específico, registra eventos antes/depois e retorna se houve alerta.
        """
        alerta_antes = None
        for nome, valor in self.dados.items():
            if nome in STATUS and valor is not None:
                lim = STATUS[nome]
                if isinstance(valor, (int, float)) and lim["alerta"] <= valor < lim["critico"]:
                    alerta_antes = (nome, valor)
                    break
        estado_alerta_atual = bool(alerta_antes)
        comp_alerta = alerta_antes[0] if alerta_antes else None
        valor_alerta = alerta_antes[1] if alerta_antes else None

        if estado_alerta_atual:
            snapshot = formatar_metricas(self.dados)
            EstadoSistema.estados_alerta.append(self.dados.copy())
            EstadoSistema.estados_alerta_depois.append(self.dados.copy())
            registrar_evento(
                "estado_alerta",
                comp_alerta,
                valor_alerta,
                STATUS[comp_alerta]["alerta"] if comp_alerta else None,
                self.args,
                f"Estado alerta valores>>> {snapshot}"
            )
        return estado_alerta_atual

    def avaliar_estavel(self, estado_alerta_atual):
        """
        Avalia se o sistema está em estado estável (sem crítico ou alerta) e registra evento.
        Usada em cada ciclo pelo fluxo principal (verificar_metricas).
        """
        if not self.houve_critico and not estado_alerta_atual:
            for nome, valor in self.dados.items():
                if nome in STATUS:
                    lim = STATUS[nome]
                    registrar_evento(
                        "estavel",
                        nome,
                        valor,
                        lim.get("alerta"),
                        self.args,
                        formatar_metricas(self.dados)
                    )


def verificar_metricas(args, ciclo_atual=None):
    """
    Função principal chamada a cada ciclo de monitoramento.
    Coleta métricas, avalia estados, executa tratamentos e registra eventos.
    Responsável por disparar alertas de resumo quando acumuladores atingem limites.
    """
    dados = metricas()
    estado = EstadoSistema(dados, args)
    print(formatar_metricas(dados, ciclo_atual=ciclo_atual))
    EstadoSistema.ciclos_total += 1
    estado.detectar_estado_critico()
    alerta = estado.avaliar_alerta()
    estado.avaliar_estavel(alerta)
    if EstadoSistema.ciclos_total >= 500:
        from services.logger import calcular_media_ultimas_linhas_jsonl, calcular_media_ultimos_blocos_log, enviar_email_alerta
        agora = time.time()
        pode_enviar = (agora - getattr(EstadoSistema, 'ultimo_envio_email', 0)) >= 45*60
        if pode_enviar:
            if len(EstadoSistema.estados_criticos_depois) >= 250:
                medias_jsonl = calcular_media_ultimas_linhas_jsonl()
                media_log = calcular_media_ultimos_blocos_log()
                mensagem = f"Alerta de média dos últimos estados críticos!\nMédias JSONL: {medias_jsonl}\nMédia LOG: {media_log}"
                enviar_email_alerta(mensagem)
                EstadoSistema.ultimo_envio_email = agora
            elif len(EstadoSistema.estados_alerta_depois) >= 400:
                medias_jsonl = calcular_media_ultimas_linhas_jsonl()
                media_log = calcular_media_ultimos_blocos_log()
                mensagem = f"Alerta de média dos últimos estados de alerta!\nMédias JSONL: {medias_jsonl}\nMédia LOG: {media_log}"
                enviar_email_alerta(mensagem)
                EstadoSistema.ultimo_envio_email = agora
        EstadoSistema.estados_criticos_depois.clear()
        EstadoSistema.estados_alerta_depois.clear()
        EstadoSistema.ciclos_total = 0
