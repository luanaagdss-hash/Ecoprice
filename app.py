# app.py
import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")  # definir antes de rodar

st.set_page_config(page_title="EcoPrice - Otimizador de Preço", layout="centered")

st.title("EcoPrice — Otimizador Inteligente de Preços Sustentáveis")

with st.form("inputs"):
    st.subheader("Dados do produto / serviço")
    custo_variavel = st.number_input("Custo variável por unidade (R$)", min_value=0.0, value=20.0, step=0.5)
    custo_fixo_mensal = st.number_input("Custo fixo mensal (R$)", min_value=0.0, value=2000.0, step=50.0)
    preco_atual = st.number_input("Preço atual (R$)", min_value=0.0, value=45.0, step=0.5)
    volume_mensal = st.number_input("Volume mensal atual (unidades)", min_value=0, value=500, step=10)
    preco_media_concorrencia = st.number_input("Preço médio concorrência (R$) — opcional", min_value=0.0, value=44.0, step=0.5)
    submitted = st.form_submit_button("Gerar estratégia")

if submitted:
    # Cálculos básicos
    margem_unitaria = preco_atual - custo_variavel
    faturamento = preco_atual * volume_mensal
    lucro = faturamento - (custo_fixo_mensal + custo_variavel * volume_mensal)
    ponto_equilibrio_unidades = custo_fixo_mensal / max(margem_unitaria, 1e-6)
    # Simulação preços
    precos = np.linspace(max(0.5, custo_variavel*1.05), preco_atual*1.6, 20)
    lucros = []
    # Estimativa simples de elasticidade (palpite); pode ser substituído por dados
    # assumimos demanda Q = a - bP; calibramos com ponto atual (P0,Q0) e supomos elasticidade -1.2 if not provided
    elasticidade_guess = -1.2
    P0, Q0 = preco_atual, volume_mensal
    for p in precos:
        # modelo simplificado: Q = Q0 * (p / P0)**elasticidade
        q = Q0 * (p / P0) ** elasticidade_guess
        profit = (p - custo_variavel) * q - custo_fixo_mensal
        lucros.append(profit)
    # Resultado ótimo
    idx_best = int(np.argmax(lucros))
    preco_otimo = float(precos[idx_best])
    lucro_otimo = float(lucros[idx_best])

    # Mostrar métricas
    st.subheader("Métricas básicas")
    st.write(f"Margem unitária atual: R$ {margem_unitaria:.2f}")
    st.write(f"Faturamento atual mensal: R$ {faturamento:,.2f}")
    st.write(f"Lucro atual mensal aproximado: R$ {lucro:,.2f}")
    st.write(f"Ponto de equilíbrio (unidades): {ponto_equilibrio_unidades:,.0f}")

    st.subheader("Simulação de preços")
    fig, ax = plt.subplots()
    ax.plot(precos, lucros)
    ax.scatter([preco_otimo], [lucro_otimo], color='red')
    ax.set_xlabel("Preço (R$)")
    ax.set_ylabel("Lucro Mensal (R$)")
    st.pyplot(fig)

    st.markdown(f"**Preço sugerido:** R$ {preco_otimo:.2f} (lucro estimado R$ {lucro_otimo:,.2f})")

    # Geração de relatório com GPT
    prompt = f"""
    Você é um analista econômico. Dados: custo variável por unidade R$ {custo_variavel:.2f}, custo fixo mensal R$ {custo_fixo_mensal:.2f},
    preço atual R$ {preco_atual:.2f}, volume mensal {volume_mensal}, preço médio concorrência R$ {preco_media_concorrencia:.2f}.
    Estimativa de elasticidade utilizada: {elasticidade_guess}.
    A simulação indica preço ótimo R$ {preco_otimo:.2f} com lucro estimado R$ {lucro_otimo:.2f}.
    Produza um relatório curto (4 parágrafos) explicando:
    1) interpretação microeconômica (elasticidade, margem, ponto de equilíbrio),
    2) principais riscos e suposições,
    3) recomendação prática de precificação e ações para teste (A/B pricing),
    4) sugestões de métricas para acompanhar (CAC, LTV, churn, ticket médio).
    """
    try:
        res = openai.ChatCompletion.create(
            model="gpt-5",  # substitua pelo modelo disponível
            messages=[{"role":"user","content":prompt}],
            max_tokens=450,
            temperature=0.2
        )
        report = res['choices'][0]['message']['content']
    except Exception as e:
        report = f"Erro ao gerar relatório via API: {e}"

    st.subheader("Relatório gerado (IA)")
    st.write(report)

    # Opção de download do relatório
    st.download_button("Download relatório (.txt)", report, file_name="relatorio_ecoprice.txt")
