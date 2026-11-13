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


def executar_modelo(
    massa_suspensa,
    massa_roda,
    rigidez,
    amortecimento,
    rigidez_pneu,
    altura,
    comprimento,
    velocidade
):
    """Executa uma simulação e retorna os resultados principais."""
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

    simulador = SimuladorSuspensao(parametros, pista)
    simulador.simular()

    aceleracao_maxima = np.max(np.abs(simulador.aceleracao_carro))
    deslocamento_maximo = np.max(np.abs(simulador.posicao_carro))
    aceleracao_rms = np.sqrt(np.mean(simulador.aceleracao_carro ** 2))

    return simulador, pista, {
        "Aceleração máxima (m/s²)": aceleracao_maxima,
        "Deslocamento máximo (cm)": deslocamento_maximo * 100,
        "Aceleração RMS (m/s²)": aceleracao_rms
    }


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
    with st.spinner("Calculando as simulações..."):
        try:
            simulador, pista, resultados_principais = executar_modelo(
                massa_suspensa,
                massa_roda,
                rigidez,
                amortecimento,
                rigidez_pneu,
                altura,
                comprimento,
                velocidade
            )

            st.success("Simulação concluída!")

            # Resultados da simulação principal
            st.subheader("Resultados da simulação principal")

            coluna1, coluna2, coluna3 = st.columns(3)

            coluna1.metric(
                "Aceleração máxima",
                f"{resultados_principais['Aceleração máxima (m/s²)']:.3f} m/s²"
            )

            coluna2.metric(
                "Deslocamento máximo",
                f"{resultados_principais['Deslocamento máximo (cm)']:.3f} cm"
            )

            coluna3.metric(
                "Aceleração RMS",
                f"{resultados_principais['Aceleração RMS (m/s²)']:.3f} m/s²"
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

            # Comparação de amortecimento
            st.header("4. Comparação entre diferentes amortecimentos")
            st.write(
                "Nesta análise, o amortecimento é alterado enquanto os "
                "demais parâmetros permanecem iguais aos escolhidos na barra lateral."
            )

            valores_amortecimento = [500, 1500, 3000]
            resultados_amortecimento = []

            for valor in valores_amortecimento:
                _, _, metricas = executar_modelo(
                    massa_suspensa,
                    massa_roda,
                    rigidez,
                    valor,
                    rigidez_pneu,
                    altura,
                    comprimento,
                    velocidade
                ) 
                resultados_amortecimento.append({
                    "Amortecimento (Ns/m)": valor,
                    **metricas
                })

            st.table(resultados_amortecimento)

            fig4, ax4 = plt.subplots(figsize=(9, 4))
            ax4.plot(
                valores_amortecimento,
                [r["Aceleração RMS (m/s²)"] for r in resultados_amortecimento],
                marker="o"
            )
            ax4.set_xlabel("Amortecimento (Ns/m)")
            ax4.set_ylabel("Aceleração RMS (m/s²)")
            ax4.set_title("Aceleração RMS para diferentes amortecimentos")
            ax4.grid()
            st.pyplot(fig4)
            plt.close(fig4)

            # Comparação de rigidez
            st.header("5. Comparação entre diferentes rigidezes")
            st.write(
                "Nesta análise, a rigidez da suspensão é alterada enquanto "
                "os demais parâmetros permanecem iguais aos escolhidos na barra lateral."
            )

            valores_rigidez = [10000, 15000, 20000]
            resultados_rigidez = []

            for valor in valores_rigidez:
                _, _, metricas = executar_modelo(
                    massa_suspensa,
                    massa_roda,
                    valor,
                    amortecimento,
                    rigidez_pneu,
                    altura,
                    comprimento,
                    velocidade
                )

                resultados_rigidez.append({
                    "Rigidez (N/m)": valor,
                    **metricas
                })

            st.table(resultados_rigidez)

            fig5, ax5 = plt.subplots(figsize=(9, 4))
            ax5.plot(
                valores_rigidez,
                [r["Aceleração RMS (m/s²)"] for r in resultados_rigidez],
                marker="o"
            )
            ax5.set_xlabel("Rigidez da suspensão (N/m)")
            ax5.set_ylabel("Aceleração RMS (m/s²)")
            ax5.set_title("Aceleração RMS para diferentes rigidezes")
            ax5.grid()
            st.pyplot(fig5)
            plt.close(fig5)

            st.caption(
                "Observação: a aceleração RMS é um indicador numérico usado "
                "neste projeto para comparar as simulações. Ela não representa, "
                "por si só, uma avaliação completa do conforto ou da segurança "
                "de um veículo real."
            )

        except Exception as erro:
            st.error(f"Erro durante a simulação: {erro}")

else:     
    st.info(
        "Altere os parâmetros na barra lateral e clique "
        "em 'Executar simulação' para visualizar os resultados."
    )
