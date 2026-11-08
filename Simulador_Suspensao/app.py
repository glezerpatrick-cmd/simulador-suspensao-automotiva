
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from simulador import (
    ParametrosSuspensao,
    PerfilPista,
    SimuladorSuspensao
)


# Configuração da página
st.set_page_config(
    page_title="Simulador de Suspensão Automotiva",
    page_icon="🚗",
    layout="wide"
)


# Título
st.title("🚗 Simulador de Suspensão Automotiva")

st.write(
    "Explore como diferentes parâmetros da suspensão "
    "influenciam o comportamento de um veículo ao passar "
    "por uma lombada."
)


# Painel lateral
st.sidebar.header("Parâmetros do veículo")

massa_suspensa = st.sidebar.slider(
    "Massa suspensa (kg)",
    150, 400, 250
)

massa_roda = st.sidebar.slider(
    "Massa da roda (kg)",
    20, 80, 40
)

rigidez = st.sidebar.slider(
    "Rigidez da suspensão (N/m)",
    5000, 30000, 15000, step=1000
)

amortecimento = st.sidebar.slider(
    "Amortecimento (Ns/m)",
    300, 4000, 1500, step=100
)

rigidez_pneu = st.sidebar.slider(
    "Rigidez do pneu (N/m)",
    80000, 250000, 150000, step=5000
)


st.sidebar.header("Parâmetros da pista")

altura = st.sidebar.slider(
    "Altura da lombada (cm)",
    2, 15, 8
)

comprimento = st.sidebar.slider(
    "Comprimento da lombada (m)",
    0.3, 2.0, 0.8, step=0.1
)

velocidade = st.sidebar.slider(
    "Velocidade do veículo (m/s)",
    1.0, 15.0, 5.0, step=0.5
)


# Botão de simulação
executar = st.button(
    "Executar simulação",
    type="primary"
)


if executar:

    parametros = ParametrosSuspensao(
        massa_suspensa,
        massa_roda,
        rigidez,
        amortecimento,
        rigidez_pneu
    )

    pista = PerfilPista(
        altura / 100,
        comprimento,
        velocidade
    )

    simulador = SimuladorSuspensao(
        parametros,
        pista
    )

    with st.spinner("Calculando o comportamento da suspensão..."):

        try:
            simulador.simular()

            st.success("Simulação concluída!")

            # Indicadores
            aceleracao_maxima = np.max(
                np.abs(simulador.aceleracao_carro)
            )

            deslocamento_maximo = np.max(
                np.abs(simulador.posicao_carro)
            )

            aceleracao_rms = np.sqrt(
                np.mean(simulador.aceleracao_carro ** 2)
            )

            st.subheader("Resultados da simulação")

            coluna1, coluna2, coluna3 = st.columns(3)

            coluna1.metric(
                "Aceleração máxima",
                f"{aceleracao_maxima:.3f} m/s²"
            )

            coluna2.metric(
                "Deslocamento máximo",
                f"{deslocamento_maximo * 100:.3f} cm"
            )

            coluna3.metric(
                "Aceleração RMS",
                f"{aceleracao_rms:.3f} m/s²"
            )

            # Gráfico 1: pista e roda
            st.subheader("1. Movimento da roda")

            deslocamento_pista = [
                pista.deslocamento(t) * 100
                for t in simulador.tempos
            ]

            fig1, ax1 = plt.subplots(figsize=(10, 4))

            ax1.plot(
                simulador.tempos,
                deslocamento_pista,
                label="Pista"
            )

            ax1.plot(
                simulador.tempos,
                simulador.posicao_roda * 100,
                label="Roda"
            )

            ax1.set_xlabel("Tempo (s)")
            ax1.set_ylabel("Deslocamento (cm)")
            ax1.legend()
            ax1.grid()

            st.pyplot(fig1)
            plt.close(fig1)

            # Gráfico 2: carroceria
            st.subheader("2. Movimento da carroceria")

            fig2, ax2 = plt.subplots(figsize=(10, 4))

            ax2.plot(
                simulador.tempos,
                simulador.posicao_carro * 100
            )

            ax2.set_xlabel("Tempo (s)")
            ax2.set_ylabel("Deslocamento (cm)")
            ax2.grid()

            st.pyplot(fig2)
            plt.close(fig2)

            # Gráfico 3: aceleração
            st.subheader("3. Aceleração da carroceria")

            fig3, ax3 = plt.subplots(figsize=(10, 4))

            ax3.plot(
                simulador.tempos,
                simulador.aceleracao_carro
            )

            ax3.set_xlabel("Tempo (s)")
            ax3.set_ylabel("Aceleração (m/s²)")
            ax3.grid()

            st.pyplot(fig3)
            plt.close(fig3)

        except Exception as erro:

            st.error(f"Erro durante a simulação: {erro}")

else:

    st.info(
        "Altere os parâmetros na barra lateral e clique "
        "em 'Executar simulação' para visualizar os resultados."
    )
