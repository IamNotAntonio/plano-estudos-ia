import os
import base64
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
    .stButton > button { background: #2980b9; color: white; border: none; border-radius: 10px; padding: 0.7rem 2rem; font-size: 1rem; font-weight: 600; width: 100%; }
    .stButton > button:hover { background: #1a6fa8; }
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

    materias = st.text_area("Quais matérias precisa estudar?", placeholder="ex: Cálculo II, Física III, POO", height=80)

    col3, col4 = st.columns(2)
    with col3:
        horas = st.slider("Horas disponíveis por dia", 1, 12, 3)
        semanas = st.slider("Semanas até a prova/objetivo", 1, 16, 4)
    with col4:
        estilo = st.selectbox("Como você aprende melhor?", ["Lendo e resumindo", "Resolvendo exercícios", "Assistindo videoaulas", "Mistura de tudo"])
        nivel = st.selectbox("Nível geral nas matérias", ["Iniciante — muita dificuldade", "Básico — entendo pouco", "Intermediário — entendo razoável", "Avançado — só revisar"])

    dificuldade = st.text_area("Qual sua maior dificuldade hoje?", placeholder="ex: Não consigo manter foco, deixo tudo para última hora...", height=80)
    provas = st.text_input("Tem provas marcadas? (opcional)", placeholder="ex: Cálculo dia 20/06, Física dia 25/06")

    st.markdown("---")
    st.markdown("### 📸 Envie fotos para personalização avançada")
    st.caption("A IA vai analisar seus materiais reais e criar um plano ainda mais preciso.")

    col5, col6 = st.columns(2)
    with col5:
        foto_cronograma = st.file_uploader("🗓 Cronograma da faculdade", type=["jpg","jpeg","png"], help="Foto do calendário acadêmico ou grade de provas")
        foto_anotacoes = st.file_uploader("📝 Suas anotações ou resumos", type=["jpg","jpeg","png"], help="Foto do seu caderno ou resumos feitos")
    with col6:
        foto_prova = st.file_uploader("📄 Prova ou exercício anterior", type=["jpg","jpeg","png"], help="Foto de uma prova antiga para entender o nível exigido")
        foto_ementa = st.file_uploader("📋 Ementa da disciplina", type=["jpg","jpeg","png"], help="Foto da ementa para montar o plano com os tópicos exatos")

    enviar = st.form_submit_button("🚀 Gerar meu plano personalizado")

if enviar:
    if not materias or not objetivo or not nome:
        st.warning("Por favor, preencha pelo menos seu nome, matérias e objetivo.")
    else:
        with st.spinner("🧠 Analisando seu perfil e materiais... isso pode levar alguns segundos."):
            try:
                cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

                imagens_analisadas = []
                uploads = {
                    "Cronograma da faculdade": foto_cronograma,
                    "Anotações do aluno": foto_anotacoes,
                    "Prova ou exercício anterior": foto_prova,
                    "Ementa da disciplina": foto_ementa
                }

                content = []

                for descricao, foto in uploads.items():
                    if foto is not None:
                        dados = base64.standard_b64encode(foto.read()).decode("utf-8")
                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": foto.type,
                                "data": dados
                            }
                        })
                        content.append({
                            "type": "text",
                            "text": f"A imagem acima é: {descricao}. Analise-a cuidadosamente para personalizar o plano."
                        })
                        imagens_analisadas.append(descricao)

                fotos_txt = f"Imagens enviadas para análise: {', '.join(imagens_analisadas)}" if imagens_analisadas else "Nenhuma imagem enviada — use apenas as informações textuais."

                prompt = f"""Você é um especialista em pedagogia universitária e coach de estudos com visão computacional.

Crie um plano de estudos ALTAMENTE PERSONALIZADO para este estudante, analisando todas as imagens enviadas:

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
- {fotos_txt}

INSTRUÇÕES:
1. Se houver imagens, analise-as primeiro e extraia informações relevantes (datas, tópicos, nível de dificuldade, padrões de questões)
2. Mencione explicitamente o que encontrou nas imagens e como isso influenciou o plano
3. Comece com análise personalizada do perfil de {nome}
4. Crie cronograma semana a semana detalhado com base nos materiais reais
5. Distribua as horas diárias por matéria
6. Sugira técnicas específicas para o estilo de aprendizado
7. Crie marcos de progresso mensuráveis
8. Dê dicas específicas para a dificuldade relatada
9. Termine com mensagem motivacional personalizada

Use emojis para organizar visualmente. Seja específico e use o nome do aluno."""

                content.append({"type": "text", "text": prompt})

                mensagem = cliente.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": content}]
                )

                plano = mensagem.content[0].text

                st.success(f"✅ Plano gerado com sucesso para {nome}!")

                if imagens_analisadas:
                    st.info(f"📸 Imagens analisadas: {', '.join(imagens_analisadas)}")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("⏱ Horas/dia", f"{horas}h")
                with col_b:
                    st.metric("📅 Semanas", semanas)
                with col_c:
                    st.metric("📸 Fotos analisadas", len(imagens_analisadas))

                st.markdown("---")
                st.markdown(plano)
                st.markdown("---")

                st.download_button(
                    label="📥 Baixar meu plano em .txt",
                    data=plano,
                    file_name=f"plano_{nome.lower().replace(' ','_')}.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Erro ao gerar o plano: {e}")

st.markdown("""
<footer>
    StudyAI © 2025 — Feito para universitários que levam os estudos a sério.
</footer>
""", unsafe_allow_html=True)
