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
    # --- 1️⃣ Cálculos básicos ---
    margem_unitaria = preco_atual - custo_variavel
    faturamento = preco_atual * volume_mensal
    lucro = faturamento - (custo_fixo_mensal + custo_variavel * volume_mensal)
    ponto_equilibrio_unidades = custo_fixo_mensal / max(margem_unitaria, 1e-6)

    # --- 2️⃣ Simulação de preços e lucros ---
    precos = np.linspace(max(0.5, custo_variavel * 1.05), preco_atual * 1.6, 20)
    lucros = []
    elasticidade_guess = -1.2
    P0, Q0 = preco_atual, volume_mensal

    for p in precos:
        q = Q0 * (p / P0) ** elasticidade_guess
        profit = (p - custo_variavel) * q - custo_fixo_mensal
        lucros.append(profit)

    idx_best = int(np.argmax(lucros))
    preco_otimo = float(precos[idx_best])
    lucro_otimo = float(lucros[idx_best])

    # --- 3️⃣ Mostrar métricas ---
    st.subheader("📈 Métricas básicas")
    st.write(f"Margem unitária atual: R$ {margem_unitaria:.2f}")
    st.write(f"Faturamento atual mensal: R$ {faturamento:,.2f}")
    st.write(f"Lucro atual mensal aproximado: R$ {lucro:,.2f}")
    st.write(f"Ponto de equilíbrio (unidades): {ponto_equilibrio_unidades:,.0f}")

    # --- 4️⃣ (opcional) Mostrar gráfico de lucro vs preço ---
    fig, ax = plt.subplots()
    ax.plot(precos, lucros)
    ax.scatter([preco_otimo], [lucro_otimo], color="red")
    ax.set_xlabel("Preço (R$)")
    ax.set_ylabel("Lucro mensal (R$)")
    st.pyplot(fig)

    st.markdown(f"**💰 Preço ótimo sugerido:** R$ {preco_otimo:.2f} — Lucro estimado: R$ {lucro_otimo:,.2f}")

    # --- 5️⃣ Gerar relatório com IA ---
    prompt = f"""
    Você é um analista econômico. 
    Dados do produto:
    - Custo variável por unidade: R$ {custo_variavel:.2f}
    - Custo fixo mensal: R$ {custo_fixo_mensal:.2f}
    - Preço atual: R$ {preco_atual:.2f}
    - Volume mensal atual: {volume_mensal}
    - Preço médio da concorrência: R$ {preco_media_concorrencia:.2f}

    A simulação indica:
    - Preço ótimo sugerido: R$ {preco_otimo:.2f}
    - Lucro estimado: R$ {lucro_otimo:,.2f}

    Produza um relatório curto e técnico (4 parágrafos) explicando:
    1) A interpretação microeconômica dos resultados (elasticidade, margem, ponto de equilíbrio);
    2) Os principais riscos e suposições dessa simulação;
    3) Uma recomendação prática de precificação e ações de teste (A/B pricing), com uma métrica para medir sucesso;
    4) Quais métricas financeiras acompanhar (CAC, LTV, ticket médio, margem, churn).

    Seja claro, direto e use linguagem de negócios.
    """

try:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=450,
        temperature=0.3
    )
    report = response["choices"][0]["message"]["content"]
except Exception as e:
    report = f"Erro ao gerar o relatório via OpenAI API: {e}"


    st.subheader("📊 Relatório gerado pela IA")
    st.write(report)

    st.download_button(
        label="Baixar relatório (.txt)",
        data=report,
        file_name="relatorio_ecoprice.txt",
        mime="text/plain"
    )
    
st.markdown("---")
st.caption("🧠 Projeto EcoPrice — Otimizador Inteligente de Preços Sustentáveis")
