
import numpy as np
from scipy.integrate import solve_ivp


class ParametrosSuspensao:

    def __init__(self, massa_suspensa, massa_roda,
                 rigidez_suspensao, amortecimento,
                 rigidez_pneu):

        self.massa_suspensa = massa_suspensa
        self.massa_roda = massa_roda
        self.rigidez_suspensao = rigidez_suspensao
        self.amortecimento = amortecimento
        self.rigidez_pneu = rigidez_pneu


class PerfilPista:

    def __init__(self, altura, comprimento, velocidade):

        self.altura = altura
        self.comprimento = comprimento
        self.velocidade = velocidade
        self.duracao = comprimento / velocidade

    def deslocamento(self, tempo):

        if 0 <= tempo <= self.duracao:

            return (self.altura / 2) * (
                1 - np.cos(2 * np.pi * tempo / self.duracao)
            )

        return 0


class SimuladorSuspensao:

    def __init__(self, parametros, pista):

        self.parametros = parametros
        self.pista = pista

    def equacoes_movimento(self, tempo, estado):

        p = self.parametros

        posicao_carro = estado[0]
        velocidade_carro = estado[1]

        posicao_roda = estado[2]
        velocidade_roda = estado[3]

        deslocamento_pista = self.pista.deslocamento(tempo)

        forca_suspensao = (
            p.rigidez_suspensao * (posicao_carro - posicao_roda)
            + p.amortecimento * (velocidade_carro - velocidade_roda)
        )

        forca_pneu = p.rigidez_pneu * (
            posicao_roda - deslocamento_pista
        )

        aceleracao_carro = (
            -forca_suspensao / p.massa_suspensa
        )

        aceleracao_roda = (
            forca_suspensao - forca_pneu
        ) / p.massa_roda

        return [
            velocidade_carro,
            aceleracao_carro,
            velocidade_roda,
            aceleracao_roda
        ]

    def simular(self, tempo_final=3):

        tempos = np.linspace(0, tempo_final, 1500)

        estado_inicial = [0, 0, 0, 0]

        resultado = solve_ivp(
            self.equacoes_movimento,
            [0, tempo_final],
            estado_inicial,
            t_eval=tempos,
            max_step=0.005
        )

        if not resultado.success:
            raise RuntimeError("Não foi possível concluir a simulação.")

        self.tempos = resultado.t
        self.posicao_carro = resultado.y[0]
        self.velocidade_carro = resultado.y[1]
        self.posicao_roda = resultado.y[2]
        self.velocidade_roda = resultado.y[3]

        self.aceleracao_carro = np.array([
            self.equacoes_movimento(t, resultado.y[:, i])[1]
            for i, t in enumerate(resultado.t)
        ])

        return resultado
