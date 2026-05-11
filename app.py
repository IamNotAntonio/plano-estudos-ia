import os
import streamlit as st
import anthropic
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Plano de Estudos com IA", page_icon="📚")
st.title("📚 Gerador de Plano de Estudos com IA")
st.write("Preencha os campos abaixo e receba um plano personalizado.")

with st.form("formulario"):
    materias = st.text_input("Quais matérias você quer estudar?", placeholder="ex: Python, Matemática, Física")
    objetivo = st.text_input("Qual é o seu objetivo?", placeholder="ex: passar no ENEM, entrar na faculdade")
    col1, col2 = st.columns(2)
    with col1:
        horas = st.slider("Horas por dia disponíveis", 1, 12, 4)
    with col2:
        semanas = st.slider("Quantas semanas?", 1, 24, 4)
    nivel = st.selectbox("Qual seu nível?", ["Iniciante", "Intermediário", "Avançado"])
    enviar = st.form_submit_button("Gerar meu plano de estudos")

if enviar:
    if not materias or not objetivo:
        st.warning("Por favor, preencha todos os campos.")
    else:
        with st.spinner("Gerando seu plano personalizado..."):
            try:
                cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                prompt = "Você é um especialista em pedagogia. Crie um plano de estudos para:\n"
                prompt += f"Matérias: {materias}\n"
                prompt += f"Objetivo: {objetivo}\n"
                prompt += f"Horas por dia: {horas}h\n"
                prompt += f"Prazo: {semanas} semanas\n"
                prompt += f"Nível: {nivel}\n"
                prompt += "Inclua: análise do perfil, ordem de estudo, cronograma semanal, distribuição diária, tópicos prioritários, dicas e como medir progresso."
                mensagem = cliente.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                plano = mensagem.content[0].text
                st.success("Plano gerado com sucesso!")
                st.markdown(plano)
                st.download_button(
                    label="Baixar plano em .txt",
                    data=plano,
                    file_name="meu_plano_de_estudos.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Erro: {e}")
