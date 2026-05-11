import os
import base64
import streamlit as st
import anthropic
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Point.AI", page_icon="🎯", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .hero { text-align: center; padding: 2rem 0 1rem; }
    .hero h1 { font-size: 2.8rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.3rem; }
    .hero p { font-size: 1.1rem; color: #666; margin-bottom: 2rem; }
    .badge { display: inline-block; background: #e8f4fd; color: #2980b9; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-bottom: 1rem; }
    .stButton > button { background: #2980b9; color: white; border: none; border-radius: 10px; padding: 0.7rem 2rem; font-size: 1rem; font-weight: 600; width: 100%; }
    .chat-msg-user { background: #2980b9; color: white; border-radius: 16px 16px 4px 16px; padding: 0.8rem 1.2rem; margin: 0.5rem 0; max-width: 80%; margin-left: auto; }
    .chat-msg-ai { background: #f0f4f8; color: #1a1a2e; border-radius: 16px 16px 16px 4px; padding: 0.8rem 1.2rem; margin: 0.5rem 0; max-width: 80%; }
    div[data-testid="stForm"] { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
    footer { text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 3rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None
if "plano_gerado" not in st.session_state:
    st.session_state.plano_gerado = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "perfil" not in st.session_state:
    st.session_state.perfil = {}

params = st.query_params
if "access_token" in params and st.session_state.user is None:
    try:
        user = supabase.auth.get_user(params["access_token"])
        st.session_state.user = user.user
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Erro no login: {e}")

if st.session_state.user is None:
    st.markdown("""
    <div class="hero">
        <span class="badge">🤖 Powered by IA</span>
        <h1>🎯 Point.AI</h1>
        <p>Planos de estudo personalizados para universitários.<br>Gerado por IA em segundos.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### Entre para começar")
        if st.button("🔑 Entrar com Google"):
            try:
                redirect_url = "https://plano-estudos-iagit-kexcfvfuuztcf6tztfipif.streamlit.app/"
                data = supabase.auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {
                        "redirect_to": redirect_url,
                        "skip_http_redirect": True
                    }
                })
                st.link_button("✅ Clique aqui para fazer login com Google", url=data.url)
            except Exception as e:
                st.error(f"Erro: {e}")

else:
    user = st.session_state.user
    nome_user = user.user_metadata.get("full_name", "Estudante")
    email_user = user.email

    with st.sidebar:
        st.markdown(f"**{nome_user}**")
        st.caption(email_user)
        if st.button("🚪 Sair"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.session_state.plano_gerado = None
            st.rerun()

    st.markdown("""
    <div class="hero">
        <span class="badge">🤖 Powered by IA</span>
        <h1>�� Point.AI</h1>
        <p>Planos de estudo personalizados para universitários.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.plano_gerado is None:
        with st.form("diagnostico"):
            st.markdown("### 📋 Seu diagnóstico de estudos")
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Seu nome", value=nome_user)
                curso = st.text_input("Seu curso", placeholder="ex: Engenharia de Software")
                universidade = st.text_input("Sua universidade", placeholder="ex: USP, UNICAMP...")
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

            dificuldade = st.text_area("Qual sua maior dificuldade?", height=80)

            st.markdown("---")
            st.markdown("### 📸 Envie fotos para personalização avançada")
            col5, col6 = st.columns(2)
            with col5:
                foto_cronograma = st.file_uploader("🗓 Cronograma", type=["jpg","jpeg","png"])
                foto_anotacoes = st.file_uploader("📝 Anotações", type=["jpg","jpeg","png"])
            with col6:
                foto_prova = st.file_uploader("📄 Prova anterior", type=["jpg","jpeg","png"])
                foto_ementa = st.file_uploader("📋 Ementa", type=["jpg","jpeg","png"])

            enviar = st.form_submit_button("🚀 Gerar meu plano personalizado")

        if enviar:
            if not materias or not objetivo:
                st.warning("Preencha pelo menos matérias e objetivo.")
            else:
                with st.spinner("🧠 Analisando seu perfil..."):
                    try:
                        cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                        content = []
                        imagens_analisadas = []

                        for descricao, foto in [("Cronograma", foto_cronograma), ("Anotações", foto_anotacoes), ("Prova", foto_prova), ("Ementa", foto_ementa)]:
                            if foto is not None:
                                dados = base64.standard_b64encode(foto.read()).decode("utf-8")
                                content.append({"type": "image", "source": {"type": "base64", "media_type": foto.type, "data": dados}})
                                content.append({"type": "text", "text": f"Imagem: {descricao}."})
                                imagens_analisadas.append(descricao)

                        prompt = f"""Você é um especialista em pedagogia universitária.
PERFIL: {nome} | {curso} | {universidade} | {semestre} | Objetivo: {objetivo}
Matérias: {materias} | {horas}h/dia | {semanas} semanas | {estilo} | {nivel}
Dificuldade: {dificuldade} | Provas: {provas}
Imagens: {', '.join(imagens_analisadas) if imagens_analisadas else 'nenhuma'}
Crie plano detalhado com: análise do perfil, cronograma semanal com checklists, técnicas personalizadas, marcos de progresso, recursos recomendados e mensagem motivacional. Use emojis."""

                        content.append({"type": "text", "text": prompt})
                        mensagem = cliente.messages.create(model="claude-sonnet-4-5", max_tokens=4000, messages=[{"role": "user", "content": content}])

                        st.session_state.plano_gerado = mensagem.content[0].text
                        st.session_state.perfil = {"nome": nome, "curso": curso, "universidade": universidade, "materias": materias, "objetivo": objetivo, "horas": horas, "semanas": semanas, "nivel": nivel, "estilo": estilo, "imagens": imagens_analisadas}
                        st.rerun()

                    except Exception as e:
                        st.error(f"Erro: {e}")

    else:
        perfil = st.session_state.perfil
        nome = perfil.get("nome", "")

        st.success(f"✅ Plano gerado para {nome}!")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("⏱ Horas/dia", f"{perfil.get('horas')}h")
        with col_b:
            st.metric("📅 Semanas", perfil.get("semanas"))
        with col_c:
            st.metric("🎓", perfil.get("universidade") or "—")

        tab1, tab2, tab3, tab4 = st.tabs(["📚 Meu Plano", "💬 Chat com IA", "📝 Simulado", "🎥 Videoaulas"])

        with tab1:
            st.markdown(st.session_state.plano_gerado)
            st.download_button("📥 Baixar plano", data=st.session_state.plano_gerado, file_name=f"plano_{nome}.txt", mime="text/plain")
            if st.button("🔄 Novo plano"):
                st.session_state.plano_gerado = None
                st.rerun()

        with tab2:
            st.markdown(f"### 💬 Tire suas dúvidas, {nome}!")
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)

            with st.form("chat_form", clear_on_submit=True):
                pergunta = st.text_input("Sua pergunta...", placeholder="ex: Explica derivadas, me dá exercícios...")
                enviar_chat = st.form_submit_button("Enviar →")

            if enviar_chat and pergunta:
                with st.spinner("🧠 Pensando..."):
                    try:
                        cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                        contexto = f"Você é tutor de {perfil.get('curso')} na {perfil.get('universidade') or 'faculdade'}. Matérias: {perfil.get('materias')}. Seja didático e use emojis."
                        historico = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history[-10:]]
                        historico.append({"role": "user", "content": pergunta})
                        resposta = cliente.messages.create(model="claude-sonnet-4-5", max_tokens=1500, system=contexto, messages=historico)
                        st.session_state.chat_history.append({"role": "user", "content": pergunta})
                        st.session_state.chat_history.append({"role": "assistant", "content": resposta.content[0].text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

        with tab3:
            st.markdown("### 📝 Simulado Personalizado")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                materia_simulado = st.selectbox("Matéria", perfil.get("materias","").split(","))
                num_questoes = st.selectbox("Questões", [3, 5, 10])
            with col_s2:
                dificuldade_sim = st.select_slider("Dificuldade", ["Fácil", "Médio", "Difícil"])

            if st.button("🎯 Gerar simulado"):
                with st.spinner("Gerando questões..."):
                    try:
                        cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                        prompt_sim = f"Crie {num_questoes} questões de múltipla escolha sobre {materia_simulado.strip()} para {perfil.get('curso')}, nível {dificuldade_sim}. Formato: **Questão N:** enunciado, a) b) c) d), **Resposta:** letra — explicação."
                        resp = cliente.messages.create(model="claude-sonnet-4-5", max_tokens=2000, messages=[{"role": "user", "content": prompt_sim}])
                        st.markdown(resp.content[0].text)
                    except Exception as e:
                        st.error(f"Erro: {e}")

        with tab4:
            st.markdown("### 🎥 Videoaulas e Lições Complementares")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                materia_video = st.selectbox("Matéria", perfil.get("materias","").split(","), key="mat_video")
                tipo_conteudo = st.selectbox("O que você precisa?", ["Explicação do zero", "Resumo rápido", "Exercícios resolvidos", "Mapa mental", "Dicas para a prova"])
            with col_v2:
                topico = st.text_input("Tópico específico", placeholder="ex: integrais por partes...")
                formato = st.selectbox("Formato", ["Texto explicativo", "Lista de tópicos", "Exemplo prático", "Analogia simples"])

            if st.button("🎓 Gerar lição"):
                with st.spinner("Preparando sua lição..."):
                    try:
                        cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                        prompt_video = f"Professor expert em {materia_video.strip()}. Crie lição para {nome} de {perfil.get('curso')}. Tópico: {topico or 'geral'}. Tipo: {tipo_conteudo}. Formato: {formato}. Inclua: objetivo, explicação, exemplos práticos, 3 exercícios com gabarito, 3 canais YouTube, 2 sites, 1 livro, dica de memorização."
                        resp = cliente.messages.create(model="claude-sonnet-4-5", max_tokens=2500, messages=[{"role": "user", "content": prompt_video}])
                        licao = resp.content[0].text
                        st.markdown(licao)
                        st.download_button("📥 Baixar lição", data=licao, file_name=f"licao_{materia_video.strip()}.txt", mime="text/plain")
                    except Exception as e:
                        st.error(f"Erro: {e}")

st.markdown("<footer>Point.AI © 2025 — Feito para universitários que levam os estudos a sério.</footer>", unsafe_allow_html=True)
