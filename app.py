import os
import base64
import unicodedata
import streamlit as st
import anthropic
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

st.set_page_config(page_title="Point.AI", page_icon="🎯", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .hero { text-align: center; padding: 4rem 0 2rem; }
    .hero h1 { font-size: 3.2rem; font-weight: 800; color: #1a1a2e; line-height: 1.2; margin-bottom: 1rem; }
    .hero h1 span { color: #2980b9; }
    .hero p { font-size: 1.2rem; color: #555; margin-bottom: 2rem; line-height: 1.7; }
    .badge { display: inline-block; background: #e8f4fd; color: #2980b9; padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin-bottom: 1.5rem; }
    .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 2rem 0; }
    .feature-card { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 16px rgba(0,0,0,0.06); text-align: center; border: 1px solid #f0f0f0; }
    .feature-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .feature-title { font-weight: 700; color: #1a1a2e; margin-bottom: 0.3rem; font-size: 0.95rem; }
    .feature-desc { color: #888; font-size: 0.82rem; line-height: 1.5; }
    .how-it-works { background: white; border-radius: 20px; padding: 2rem; margin: 2rem 0; box-shadow: 0 2px 16px rgba(0,0,0,0.06); }
    .step { display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1.2rem; }
    .step-num { background: #2980b9; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0; font-size: 0.9rem; }
    .step-content h4 { margin: 0 0 0.2rem; color: #1a1a2e; font-size: 0.95rem; }
    .step-content p { margin: 0; color: #888; font-size: 0.85rem; }
    .testimonial { background: #f8fbff; border-radius: 16px; padding: 1.5rem; margin: 1rem 0; border-left: 4px solid #2980b9; }
    .testimonial p { color: #333; font-style: italic; margin-bottom: 0.5rem; }
    .testimonial span { color: #888; font-size: 0.85rem; font-weight: 600; }
    .cta-box { background: linear-gradient(135deg, #2980b9, #1a6fa8); border-radius: 20px; padding: 3rem 2rem; text-align: center; margin: 2rem 0; }
    .cta-box h2 { color: white; font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem; }
    .cta-box p { color: rgba(255,255,255,0.85); margin-bottom: 1.5rem; }
    .stButton > button { background: #2980b9; color: white; border: none; border-radius: 10px; padding: 0.8rem 2rem; font-size: 1rem; font-weight: 600; width: 100%; }
    .stButton > button:hover { background: #1a6fa8; }
    .chat-msg-user { background: #2980b9; color: white; border-radius: 16px 16px 4px 16px; padding: 0.8rem 1.2rem; margin: 0.5rem 0; max-width: 80%; margin-left: auto; }
    .chat-msg-ai { background: #f0f4f8; color: #1a1a2e; border-radius: 16px 16px 16px 4px; padding: 0.8rem 1.2rem; margin: 0.5rem 0; max-width: 80%; }
    div[data-testid="stForm"] { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
    footer { text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 3rem; padding-bottom: 2rem; }
    .stat { text-align: center; }
    .stat-num { font-size: 2rem; font-weight: 800; color: #2980b9; }
    .stat-label { font-size: 0.85rem; color: #888; }
</style>
""", unsafe_allow_html=True)

def gerar_pdf(texto, nome):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "Point.AI - Plano de Estudos", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Aluno: {nome}", ln=True, align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 10)
    for linha in texto.split("\n"):
        linha_limpa = unicodedata.normalize("NFKD", linha).encode("ascii", "ignore").decode("ascii")
        if linha_limpa.startswith("###"):
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(0, 7, linha_limpa.replace("###", "").strip())
            pdf.set_font("Helvetica", "", 10)
        elif linha_limpa.startswith("##"):
            pdf.set_font("Helvetica", "B", 13)
            pdf.multi_cell(0, 7, linha_limpa.replace("##", "").strip())
            pdf.set_font("Helvetica", "", 10)
        elif linha_limpa.startswith("#"):
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(0, 7, linha_limpa.replace("#", "").strip())
            pdf.set_font("Helvetica", "", 10)
        else:
            pdf.multi_cell(0, 6, linha_limpa)
    return pdf.output()

if "plano_gerado" not in st.session_state:
    st.session_state.plano_gerado = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "perfil" not in st.session_state:
    st.session_state.perfil = {}
if "pagina" not in st.session_state:
    st.session_state.pagina = "home"

if st.session_state.pagina == "home":
    st.markdown("""
    <div class="hero">
        <span class="badge">🤖 Inteligência Artificial para Estudantes</span>
        <h1>Estude com um plano<br><span>feito só para você</span></h1>
        <p>O Point.AI analisa seu perfil, suas matérias e até suas provas antigas<br>para criar um plano de estudos 100% personalizado em segundos.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat"><div class="stat-num">100%</div><div class="stat-label">Personalizado para você</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat"><div class="stat-num">4</div><div class="stat-label">Ferramentas integradas</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat"><div class="stat-num">30s</div><div class="stat-label">Para gerar seu plano</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
    with col_btn2:
        if st.button("🚀 Criar meu plano agora — é grátis"):
            st.session_state.pagina = "app"
            st.rerun()

    st.markdown("""
    <div class="features">
        <div class="feature-card"><div class="feature-icon">📚</div><div class="feature-title">Plano Personalizado</div><div class="feature-desc">A IA analisa seu nível, tempo disponível e até fotos das suas provas para criar o plano ideal</div></div>
        <div class="feature-card"><div class="feature-icon">💬</div><div class="feature-title">Chat com IA</div><div class="feature-desc">Tire dúvidas, peça exercícios e ideias para trabalhos com um tutor disponível 24h</div></div>
        <div class="feature-card"><div class="feature-icon">📝</div><div class="feature-title">Simulados</div><div class="feature-desc">Questões geradas sob medida para suas matérias e nível de dificuldade</div></div>
        <div class="feature-card"><div class="feature-icon">🎥</div><div class="feature-title">Lições Complementares</div><div class="feature-desc">Explicações detalhadas com exercícios, recursos e canais do YouTube para cada matéria</div></div>
        <div class="feature-card"><div class="feature-icon">📸</div><div class="feature-title">Análise de Fotos</div><div class="feature-desc">Envie fotos do cronograma, ementa ou prova antiga e a IA adapta o plano ao conteúdo real</div></div>
        <div class="feature-card"><div class="feature-icon">📄</div><div class="feature-title">Export em PDF</div><div class="feature-desc">Baixe seu plano formatado em PDF para consultar offline quando e onde quiser</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="how-it-works">
        <h3 style="margin-bottom: 1.5rem; color: #1a1a2e;">⚡ Como funciona</h3>
        <div class="step"><div class="step-num">1</div><div class="step-content"><h4>Preencha seu perfil</h4><p>Informe suas matérias, objetivo, tempo disponível e nível atual</p></div></div>
        <div class="step"><div class="step-num">2</div><div class="step-content"><h4>Envie seus materiais (opcional)</h4><p>Fotos do cronograma, ementa ou provas antigas para personalização máxima</p></div></div>
        <div class="step"><div class="step-num">3</div><div class="step-content"><h4>Receba seu plano em segundos</h4><p>A IA gera um cronograma completo, semana a semana, com dicas específicas para você</p></div></div>
        <div class="step"><div class="step-num">4</div><div class="step-content"><h4>Use o chat para tirar dúvidas</h4><p>Pergunte qualquer coisa sobre suas matérias, peça exercícios ou ideias para trabalhos</p></div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h3 style="text-align: center; color: #1a1a2e; margin: 2rem 0 1rem;">💬 O que estudantes dizem</h3>
    <div class="testimonial"><p>"Estava perdido no 3º semestre de Engenharia com 5 matérias ao mesmo tempo. O Point.AI montou um plano realista que consegui seguir de verdade."</p><span>— Lucas M., Engenharia Elétrica — USP</span></div>
    <div class="testimonial"><p>"Enviei a foto da minha ementa de Cálculo III e ele montou o plano exato com os tópicos da minha professora. Incrível."</p><span>— Mariana S., Matemática — UNICAMP</span></div>
    <div class="testimonial"><p>"O chat de dúvidas salvou minha prova de Estrutura de Dados. Explica melhor que muito professor."</p><span>— Rafael T., Ciência da Computação — UFMG</span></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cta-box"><h2>Pronto para estudar do jeito certo?</h2><p>Crie seu plano personalizado agora. Gratuito, sem cadastro.</p></div>', unsafe_allow_html=True)

    col_btn4, col_btn5, col_btn6 = st.columns([1,2,1])
    with col_btn5:
        if st.button("🎯 Começar agora"):
            st.session_state.pagina = "app"
            st.rerun()

elif st.session_state.pagina == "app":
    col_back, col_title = st.columns([1,4])
    with col_back:
        if st.button("← Voltar"):
            st.session_state.pagina = "home"
            st.session_state.plano_gerado = None
            st.rerun()
    with col_title:
        st.markdown("### 🎯 Point.AI")

    if st.session_state.plano_gerado is None:
        with st.form("diagnostico"):
            st.markdown("### �� Seu diagnóstico de estudos")
            st.caption("Quanto mais detalhes, mais personalizado será seu plano.")
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Seu nome", placeholder="ex: João Silva")
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
            st.caption("Opcional — mas faz o plano muito mais preciso.")
            col5, col6 = st.columns(2)
            with col5:
                foto_cronograma = st.file_uploader("🗓 Cronograma", type=["jpg","jpeg","png"])
                foto_anotacoes = st.file_uploader("📝 Anotações", type=["jpg","jpeg","png"])
            with col6:
                foto_prova = st.file_uploader("📄 Prova anterior", type=["jpg","jpeg","png"])
                foto_ementa = st.file_uploader("📋 Ementa", type=["jpg","jpeg","png"])

            enviar = st.form_submit_button("🚀 Gerar meu plano personalizado")

        if enviar:
            if not materias or not objetivo or not nome:
                st.warning("Preencha pelo menos nome, matérias e objetivo.")
            else:
                with st.spinner("🧠 Analisando seu perfil e gerando seu plano..."):
                    try:
                        cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                        content = []
                        imagens_analisadas = []

                        for descricao, foto in [("Cronograma", foto_cronograma), ("Anotacoes", foto_anotacoes), ("Prova", foto_prova), ("Ementa", foto_ementa)]:
                            if foto is not None:
                                dados = base64.standard_b64encode(foto.read()).decode("utf-8")
                                content.append({"type": "image", "source": {"type": "base64", "media_type": foto.type, "data": dados}})
                                content.append({"type": "text", "text": f"Imagem: {descricao}."})
                                imagens_analisadas.append(descricao)

                        prompt = f"""Voce e um especialista em pedagogia universitaria.
PERFIL: {nome} | {curso} | {universidade} | {semestre} | Objetivo: {objetivo}
Materias: {materias} | {horas}h/dia | {semanas} semanas | {estilo} | {nivel}
Dificuldade: {dificuldade} | Provas: {provas}
Imagens: {', '.join(imagens_analisadas) if imagens_analisadas else 'nenhuma'}
Crie plano detalhado com: analise do perfil, cronograma semanal com checklists, tecnicas personalizadas, marcos de progresso, recursos recomendados e mensagem motivacional. Use emojis."""

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

        st.success(f"Plano gerado para {nome}!")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Horas/dia", f"{perfil.get('horas')}h")
        with col_b:
            st.metric("Semanas", perfil.get("semanas"))
        with col_c:
            st.metric("Universidade", perfil.get("universidade") or "-")

        tab1, tab2, tab3, tab4 = st.tabs(["📚 Meu Plano", "💬 Chat com IA", "📝 Simulado", "🎥 Videoaulas"])

        with tab1:
            st.markdown(st.session_state.plano_gerado)
            st.markdown("---")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button("📥 Baixar em .txt", data=st.session_state.plano_gerado, file_name=f"plano_{nome}.txt", mime="text/plain")
            with col_d2:
                pdf_bytes = gerar_pdf(st.session_state.plano_gerado, nome)
                st.download_button("📄 Baixar em PDF", data=bytes(pdf_bytes), file_name=f"plano_{nome}.pdf", mime="application/pdf")
            if st.button("🔄 Novo plano"):
                st.session_state.plano_gerado = None
                st.rerun()

        with tab2:
            st.markdown(f"### 💬 Tire suas duvidas, {nome}!")
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)

            with st.form("chat_form", clear_on_submit=True):
                pergunta = st.text_input("Sua pergunta...", placeholder="ex: Explica derivadas, me da exercicios...")
                enviar_chat = st.form_submit_button("Enviar")

            if enviar_chat and pergunta:
                with st.spinner("Pensando..."):
                    try:
                        cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                        contexto = f"Voce e tutor de {perfil.get('curso')} na {perfil.get('universidade') or 'faculdade'}. Materias: {perfil.get('materias')}. Seja didatico e use emojis."
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
                materia_simulado = st.selectbox("Materia", perfil.get("materias","").split(","))
                num_questoes = st.selectbox("Questoes", [3, 5, 10])
            with col_s2:
                dificuldade_sim = st.select_slider("Dificuldade", ["Facil", "Medio", "Dificil"])

            if st.button("🎯 Gerar simulado"):
                with st.spinner("Gerando questoes..."):
                    try:
                        cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                        prompt_sim = f"Crie {num_questoes} questoes de multipla escolha sobre {materia_simulado.strip()} para {perfil.get('curso')}, nivel {dificuldade_sim}. Formato: **Questao N:** enunciado, a) b) c) d), **Resposta:** letra - explicacao."
                        resp = cliente.messages.create(model="claude-sonnet-4-5", max_tokens=2000, messages=[{"role": "user", "content": prompt_sim}])
                        st.markdown(resp.content[0].text)
                    except Exception as e:
                        st.error(f"Erro: {e}")

        with tab4:
            st.markdown("### 🎥 Videoaulas e Licoes Complementares")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                materia_video = st.selectbox("Materia", perfil.get("materias","").split(","), key="mat_video")
                tipo_conteudo = st.selectbox("O que voce precisa?", ["Explicacao do zero", "Resumo rapido", "Exercicios resolvidos", "Mapa mental", "Dicas para a prova"])
            with col_v2:
                topico = st.text_input("Topico especifico", placeholder="ex: integrais por partes...")
                formato = st.selectbox("Formato", ["Texto explicativo", "Lista de topicos", "Exemplo pratico", "Analogia simples"])

            if st.button("🎓 Gerar licao"):
                with st.spinner("Preparando sua licao..."):
                    try:
                        cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                        prompt_video = f"Professor expert em {materia_video.strip()}. Crie licao para {nome} de {perfil.get('curso')}. Topico: {topico or 'geral'}. Tipo: {tipo_conteudo}. Formato: {formato}. Inclua: objetivo, explicacao, exemplos praticos, 3 exercicios com gabarito, 3 canais YouTube, 2 sites, 1 livro, dica de memorizacao."
                        resp = cliente.messages.create(model="claude-sonnet-4-5", max_tokens=2500, messages=[{"role": "user", "content": prompt_video}])
                        licao = resp.content[0].text
                        st.markdown(licao)
                        st.download_button("📥 Baixar licao", data=licao, file_name=f"licao_{materia_video.strip()}.txt", mime="text/plain")
                    except Exception as e:
                        st.error(f"Erro: {e}")

st.markdown("<footer>Point.AI 2025 - Feito para universitarios que levam os estudos a serio.</footer>", unsafe_allow_html=True)
