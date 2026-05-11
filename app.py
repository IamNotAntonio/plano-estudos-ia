import os
import streamlit as st
import anthropic
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="StudyAI — Seu Plano de Estudos Personalizado",
    page_icon="🎓",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .hero { text-align: center; padding: 2rem 0 1rem; }
    .hero h1 { font-size: 2.8rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.3rem; }
    .hero p { font-size: 1.1rem; color: #666; margin-bottom: 2rem; }
    .badge { display: inline-block; background: #e8f4fd; color: #2980b9; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-bottom: 1rem; }
    
    .card { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 24px rgba(0,0,0,0.08); margin-bottom: 1.5rem; }
    
    .step { display: flex; align-items: center; gap: 12px; margin-bottom: 1rem; }
    .step-num { background: #2980b9; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; flex-shrink: 0; }
    
    .plan-box { background: #f8fbff; border-left: 4px solid #2980b9; border-radius: 8px; padding: 1.5rem; margin-top: 1rem; }
    
    .stButton > button { background: #2980b9; color: white; border: none; border-radius: 10px; padding: 0.7rem 2rem; font-size: 1rem; font-weight: 600; width: 100%; transition: all 0.2s; }
    .stButton > button:hover { background: #1a6fa8; transform: translateY(-1px); }
    
    .metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
    .metric { flex: 1; background: #f0f7ff; border-radius: 10px; padding: 1rem; text-align: center; }
    .metric-val { font-size: 1.5rem; font-weight: 700; color: #2980b9; }
    .metric-label { font-size: 0.75rem; color: #888; margin-top: 2px; }
    
    div[data-testid="stForm"] { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
    
    footer { text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 3rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <span class="badge">🤖 Powered by IA</span>
    <h1>🎓 StudyAI</h1>
    <p>Planos de estudo personalizados para universitários.<br>Gerado por IA em segundos.</p>
</div>
""", unsafe_allow_html=True)

with st.form("diagnostico"):
    st.markdown("### 📋 Seu diagnóstico de estudos")
    st.caption("Quanto mais detalhes, mais personalizado será seu plano.")

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Seu nome", placeholder="ex: João Silva")
        curso = st.text_input("Seu curso", placeholder="ex: Engenharia de Software")
    with col2:
        semestre = st.selectbox("Semestre atual", [f"{i}º semestre" for i in range(1, 11)])
        objetivo = st.text_input("Objetivo principal", placeholder="ex: passar em Cálculo II")

    materias = st.text_area("Quais matérias precisa estudar?", placeholder="ex: Cálculo II, Física III, Programação Orientada a Objetos", height=80)

    col3, col4 = st.columns(2)
    with col3:
        horas = st.slider("Horas disponíveis por dia", 1, 12, 3)
        semanas = st.slider("Semanas até a prova/objetivo", 1, 16, 4)
    with col4:
        estilo = st.selectbox("Como você aprende melhor?", ["Lendo e resumindo", "Resolvendo exercícios", "Assistindo videoaulas", "Mistura de tudo"])
        nivel = st.selectbox("Nível geral nas matérias", ["Iniciante — muita dificuldade", "Básico — entendo pouco", "Intermediário — entendo razoável", "Avançado — só revisar"])

    dificuldade = st.text_area("Qual sua maior dificuldade hoje?", placeholder="ex: Não consigo manter foco, deixo tudo para última hora, não entendo derivadas...", height=80)

    provas = st.text_input("Tem provas marcadas? (opcional)", placeholder="ex: Cálculo dia 20/06, Física dia 25/06")

    enviar = st.form_submit_button("🚀 Gerar meu plano personalizado")

if enviar:
    if not materias or not objetivo or not nome:
        st.warning("Por favor, preencha pelo menos seu nome, matérias e objetivo.")
    else:
        with st.spinner("🧠 Analisando seu perfil e gerando seu plano..."):
            try:
                cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

                prompt = f"""Você é um especialista em pedagogia universitária e coach de estudos.

Crie um plano de estudos ALTAMENTE PERSONALIZADO para este estudante:

PERFIL DO ALUNO:
- Nome: {nome}
- Curso: {curso} — {semestre}
- Objetivo: {objetivo}
- Matérias: {materias}
- Horas disponíveis: {horas}h por dia
- Prazo: {semanas} semanas
- Estilo de aprendizado: {estilo}
- Nível atual: {nivel}
- Maior dificuldade: {dificuldade}
- Provas marcadas: {provas if provas else 'Não informado'}

INSTRUÇÕES PARA O PLANO:
1. Comece com uma análise do perfil de {nome} — seja direto e empático, mencione o nome
2. Identifique os pontos críticos baseado na dificuldade relatada
3. Crie um cronograma semana a semana detalhado
4. Para cada semana, distribua as horas diárias por matéria
5. Sugira técnicas de estudo específicas para o estilo de aprendizado informado
6. Crie marcos de progresso — como {nome} vai saber se está evoluindo
7. Dê dicas específicas para a dificuldade relatada
8. Termine com uma mensagem motivacional personalizada

Seja específico, use o nome do aluno, e faça o plano parecer feito especialmente para ele.
Use emojis para deixar mais visual e organizado."""

                mensagem = cliente.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=3000,
                    messages=[{"role": "user", "content": prompt}]
                )

                plano = mensagem.content[0].text

                st.success(f"✅ Plano gerado com sucesso para {nome}!")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("⏱ Horas/dia", f"{horas}h")
                with col_b:
                    st.metric("📅 Semanas", semanas)
                with col_c:
                    st.metric("📚 Matérias", len(materias.split(",")))

                st.markdown("---")
                st.markdown(plano)
                st.markdown("---")

                st.download_button(
                    label="📥 Baixar meu plano em .txt",
                    data=plano,
                    file_name=f"plano_estudos_{nome.lower().replace(' ','_')}.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Erro ao gerar o plano: {e}")

st.markdown("""
<footer>
    StudyAI © 2025 — Feito para universitários que levam os estudos a sério.
</footer>
""", unsafe_allow_html=True)
