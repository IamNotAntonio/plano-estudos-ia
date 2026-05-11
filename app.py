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
    .chat-msg-user { background: #2980b9; color: white; border-radius: 16px 16px 4px 16px; padding: 0.8rem 1.2rem; margin: 0.5rem 0; max-width: 80%; margin-left: auto; }
    .chat-msg-ai { background: #f0f4f8; color: #1a1a2e; border-radius: 16px 16px 16px 4px; padding: 0.8rem 1.2rem; margin: 0.5rem 0; max-width: 80%; }
    .progress-bar { background: #e0e0e0; border-radius: 10px; height: 8px; margin: 4px 0; }
    .progress-fill { background: #2980b9; border-radius: 10px; height: 8px; }
    div[data-testid="stForm"] { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
    footer { text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 3rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

if "plano_gerado" not in st.session_state:
    st.session_state.plano_gerado = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "perfil" not in st.session_state:
    st.session_state.perfil = {}
if "checklist" not in st.session_state:
    st.session_state.checklist = {}

st.markdown("""
<div class="hero">
    <span class="badge">🤖 Powered by IA</span>
    <h1>🎓 StudyAI</h1>
    <p>Planos de estudo personalizados para universitários.<br>Gerado por IA em segundos.</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.plano_gerado is None:
    with st.form("diagnostico"):
        st.markdown("### 📋 Seu diagnóstico de estudos")
        st.caption("Quanto mais detalhes, mais personalizado será seu plano.")

        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Seu nome", placeholder="ex: João Silva")
            curso = st.text_input("Seu curso", placeholder="ex: Engenharia de Software")
            universidade = st.text_input("Sua universidade", placeholder="ex: USP, UNICAMP, UFMG...")
        with col2:
            semestre = st.selectbox("Semestre atual", [f"{i}º semestre" for i in range(1, 11)])
            objetivo = st.text_input("Objetivo principal", placeholder="ex: passar em Cálculo II")
            provas = st.text_input("Provas marcadas?", placeholder="ex: Cálculo dia 20/06")

        materias = st.text_area("Quais matérias precisa estudar?", placeholder="ex: Cálculo II, Física III, POO", height=80)

        col3, col4 = st.columns(2)
        with col3:
            horas = st.slider("Horas disponíveis por dia", 1, 12, 3)
            semanas = st.slider("Semanas até a prova", 1, 16, 4)
        with col4:
            estilo = st.selectbox("Como você aprende melhor?", ["Lendo e resumindo", "Resolvendo exercícios", "Assistindo videoaulas", "Mistura de tudo"])
            nivel = st.selectbox("Nível geral nas matérias", ["Iniciante — muita dificuldade", "Básico — entendo pouco", "Intermediário — entendo razoável", "Avançado — só revisar"])

        dificuldade = st.text_area("Qual sua maior dificuldade?", placeholder="ex: Não consigo manter foco, não entendo derivadas...", height=80)

        st.markdown("---")
        st.markdown("### 📸 Envie fotos para personalização avançada")
        st.caption("A IA analisa seus materiais reais e detecta automaticamente suas dificuldades.")

        col5, col6 = st.columns(2)
        with col5:
            foto_cronograma = st.file_uploader("🗓 Cronograma da faculdade", type=["jpg","jpeg","png"])
            foto_anotacoes = st.file_uploader("📝 Suas anotações", type=["jpg","jpeg","png"])
        with col6:
            foto_prova = st.file_uploader("📄 Prova anterior", type=["jpg","jpeg","png"])
            foto_ementa = st.file_uploader("📋 Ementa da disciplina", type=["jpg","jpeg","png"])

        enviar = st.form_submit_button("🚀 Gerar meu plano personalizado")

    if enviar:
        if not materias or not objetivo or not nome:
            st.warning("Preencha pelo menos nome, matérias e objetivo.")
        else:
            with st.spinner("🧠 Analisando seu perfil e materiais..."):
                try:
                    cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                    content = []
                    imagens_analisadas = []

                    uploads = {
                        "Cronograma da faculdade": foto_cronograma,
                        "Anotações do aluno": foto_anotacoes,
                        "Prova anterior": foto_prova,
                        "Ementa da disciplina": foto_ementa
                    }

                    for descricao, foto in uploads.items():
                        if foto is not None:
                            dados = base64.standard_b64encode(foto.read()).decode("utf-8")
                            content.append({"type": "image", "source": {"type": "base64", "media_type": foto.type, "data": dados}})
                            content.append({"type": "text", "text": f"Imagem: {descricao}. Analise e extraia informações relevantes."})
                            imagens_analisadas.append(descricao)

                    fotos_txt = f"Imagens enviadas: {', '.join(imagens_analisadas)}" if imagens_analisadas else "Sem imagens."

                    prompt = f"""Você é um especialista em pedagogia universitária.

PERFIL:
- Nome: {nome} | Curso: {curso} | Universidade: {universidade if universidade else 'Não informada'}
- Semestre: {semestre} | Objetivo: {objetivo}
- Matérias: {materias}
- Horas/dia: {horas}h | Prazo: {semanas} semanas
- Estilo: {estilo} | Nível: {nivel}
- Dificuldade: {dificuldade}
- Provas: {provas if provas else 'Não informado'}
- {fotos_txt}

INSTRUÇÕES:
1. Se houver imagens, analise e mencione o que encontrou
2. Detecte automaticamente o nível de dificuldade de cada matéria
3. Análise personalizada do perfil de {nome}
4. Cronograma SEMANA A SEMANA detalhado
5. Para cada semana liste os tópicos diários como checklist no formato:
   - [ ] Tópico 1
   - [ ] Tópico 2
6. Técnicas específicas para o estilo de aprendizado
7. Marcos de progresso mensuráveis
8. Sugestões de recursos (livros, sites, canais YouTube) para cada matéria
9. Mensagem motivacional personalizada para {nome}

Use emojis. Seja específico e detalhado."""

                    content.append({"type": "text", "text": prompt})

                    mensagem = cliente.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=4000,
                        messages=[{"role": "user", "content": content}]
                    )

                    st.session_state.plano_gerado = mensagem.content[0].text
                    st.session_state.perfil = {
                        "nome": nome, "curso": curso, "universidade": universidade,
                        "materias": materias, "objetivo": objetivo, "horas": horas,
                        "semanas": semanas, "nivel": nivel, "estilo": estilo,
                        "imagens": imagens_analisadas
                    }
                    st.session_state.chat_history = []
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro: {e}")

else:
    perfil = st.session_state.perfil
    nome = perfil.get("nome", "")

    st.success(f"✅ Plano gerado para {nome}!")

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("⏱ Horas/dia", f"{perfil.get('horas')}h")
    with col_b:
        st.metric("📅 Semanas", perfil.get("semanas"))
    with col_c:
        st.metric("🎓 Universidade", perfil.get("universidade") or "—")
    with col_d:
        st.metric("📸 Fotos", len(perfil.get("imagens", [])))

    tab1, tab2, tab3 = st.tabs(["📚 Meu Plano", "💬 Chat com IA", "📝 Simulado"])

    with tab1:
        st.markdown(st.session_state.plano_gerado)
        st.markdown("---")
        st.download_button(
            label="📥 Baixar plano em .txt",
            data=st.session_state.plano_gerado,
            file_name=f"plano_{nome.lower().replace(' ','_')}.txt",
            mime="text/plain"
        )
        if st.button("🔄 Gerar novo plano"):
            st.session_state.plano_gerado = None
            st.session_state.chat_history = []
            st.rerun()

    with tab2:
        st.markdown(f"### 💬 Tire suas dúvidas, {nome}!")
        st.caption("Pergunte sobre qualquer matéria, peça exercícios, ideias para trabalhos ou explique um conceito.")

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            pergunta = st.text_input("Sua pergunta...", placeholder="ex: Explica derivadas, me dá exercícios de Cálculo, ideias para TCC sobre IA...")
            enviar_chat = st.form_submit_button("Enviar →")

        if enviar_chat and pergunta:
            with st.spinner("🧠 Pensando..."):
                try:
                    cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

                    contexto = f"""Você é um tutor universitário especialista ajudando {nome}, 
estudante de {perfil.get('curso')} na {perfil.get('universidade') or 'faculdade'}.
Matérias em estudo: {perfil.get('materias')}.
Objetivo: {perfil.get('objetivo')}.
Seja didático, use exemplos práticos e emojis para organizar."""

                    historico = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history[-10:]]
                    historico.append({"role": "user", "content": pergunta})

                    resposta = cliente.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=1500,
                        system=contexto,
                        messages=historico
                    )

                    resposta_txt = resposta.content[0].text
                    st.session_state.chat_history.append({"role": "user", "content": pergunta})
                    st.session_state.chat_history.append({"role": "assistant", "content": resposta_txt})
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro: {e}")

    with tab3:
        st.markdown("### 📝 Simulado Personalizado")
        st.caption("Gere questões baseadas nas suas matérias para testar seus conhecimentos.")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            materia_simulado = st.selectbox("Matéria", perfil.get("materias","").split(","))
        with col_s2:
            num_questoes = st.selectbox("Número de questões", [3, 5, 10])

        dificuldade_sim = st.select_slider("Dificuldade", ["Fácil", "Médio", "Difícil"])

        if st.button("🎯 Gerar simulado"):
            with st.spinner("Gerando questões..."):
                try:
                    cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

                    prompt_sim = f"""Crie um simulado com {num_questoes} questões de múltipla escolha sobre {materia_sim} 
para um estudante de {perfil.get('curso')} de nível {dificuldade_sim}.
Formato para cada questão:
**Questão N:** enunciado
a) opção
b) opção
c) opção
d) opção
**Resposta:** letra correta — breve explicação

Seja específico e educativo."""

                    resposta_sim = cliente.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=2000,
                        messages=[{"role": "user", "content": prompt_sim}]
                    )
                    st.markdown(resposta_sim.content[0].text)

                except Exception as e:
                    st.error(f"Erro: {e}")

st.markdown("""
<footer>StudyAI © 2025 — Feito para universitários que levam os estudos a sério.</footer>
""", unsafe_allow_html=True)
