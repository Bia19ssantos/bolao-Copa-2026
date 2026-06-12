import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone

# 1. CONFIGURAÇÃO DA PÁGINA (Tema Escuro Nativo)
st.set_page_config(page_title="Bolão da Família - Rumo ao Hexa!", page_icon="🇧🇷", layout="centered")

LINK_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1Z2I9Uu0wZvyDb4Fqyo-qgPKE8y4ga4279aj-VYfuXb0/edit?usp=sharing"

# ==================== ATENÇÃO: ATUALIZE ESSES NÚMEROS SE SEU NOVO FORMS NÃO SALVAR ====================
URL_FORM_POST = "https://docs.google.com/forms/d/e/1FAIpQLSe-pFE2N7hUNuJZf8rWXZMrlVkeDULySNF1LSQDUTNepOEJqw/formResponse"
ENTRY_NOME = "entry.1221199580"    
ENTRY_JOGO = "entry.1843232675"    
ENTRY_PALPITE = "entry.880496180"   
# ======================================================================================================

fuso_br = timezone(timedelta(hours=-3))
agora_br = datetime.now(fuso_br)

# Injeção de CSS para garantir o Tema Escuro Lindo e Letras Visíveis
st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"] { background-color: #0e1117 !important; }
        .header-bolao {
            background: linear-gradient(135deg, #009c3b 0%, #002776 100%);
            color: #ffdf00 !important;
            text-align: center; padding: 25px; border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-bottom: 25px;
        }
        .header-bolao h1 { color: #ffdf00 !important; margin: 0; font-size: 28px; }
        .header-bolao p { color: #ffffff; margin: 5px 0 0 0; font-weight: bold; font-size: 16px; }
        
        .caixa-legenda {
            background-color: #1f232a;
            border-left: 5px solid #009c3b;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
            border: 1px solid #3f4756;
        }
        .caixa-legenda h4 { color: #ffdf00 !important; margin-top: 0; margin-bottom: 8px; font-weight: bold; }
        .caixa-legenda ul { margin: 0; padding-left: 20px; color: #ffffff !important; }
        .caixa-legenda li { margin-bottom: 5px; color: #ffffff !important; }
        
        h1, h2, h3, h4, h5, h6, span, p, label, .stMarkdown, [data-testid="stWidgetLabel"] p { 
            color: #ffffff !important; 
            font-family: 'Arial', sans-serif; 
        }
        
        button[data-baseweb="tab"] { font-size: 14px !important; font-weight: bold !important; color: #8a94a6 !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #ffdf00 !important; border-bottom-color: #ffdf00 !important; }
        
        div[data-baseweb="select"], div[data-baseweb="input"], input, .stNumberInput div { 
            background-color: #1f232a !important; 
            color: #ffffff !important; 
            border: 1px solid #3f4756 !important; 
            border-radius: 8px; 
        }
        div[role="listbox"], li, div[role="option"] { background-color: #1f232a !important; color: #ffffff !important; }
        
        .stTable, table, [data-testid="stTable"] { background-color: #1f232a !important; border-radius: 10px; overflow: hidden; border: 1px solid #3f4756 !important; }
        table tr, table td, th, td, tr, .stTable td, .stTable th { background-color: #1f232a !important; color: #ffffff !important; font-size: 15px !important; border-bottom: 1px solid #3f4756 !important; text-align: center !important; }
        th, table th { background-color: #11151c !important; font-weight: bold !important; color: #ffdf00 !important; }
        
        div.stButton > button:first-child { background-color: #009c3b !important; color: #ffdf00 !important; font-weight: bold !important; border: 2px solid #ffdf00 !important; border-radius: 10px !important; width: 100%; padding: 10px 20px !important; text-transform: uppercase; }
        div.stButton > button:first-child:hover { background-color: #002776 !important; color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# 2. FUNÇÃO PARA LER OS JOGOS DA PLANILHA
def carregar_jogos():
    try:
        import time
        url = LINK_DA_PLANILHA.replace('/edit?usp=sharing', f'/gviz/tq?tqx=out:csv&sheet=jogos&nocache={time.time()}')
        df = pd.read_csv(url)
        df.columns = [str(col).strip() for col in df.columns]
        
        jogos_dict = {}
        for _, row in df.iterrows():
            if pd.isna(row['Confronto']) or pd.isna(row['Data']):
                continue
                
            res = str(row['Resultado']).strip().upper().replace(" ", "") if not pd.isna(row['Resultado']) else ""
            if res == "" or res == "-" or "NAN" in res:
                res = None
                
            enc = True if str(row['Encerrado']).lower().strip() == 'true' else False
            
            data_hora_jogo = datetime.strptime(str(row['Data']).strip(), "%Y-%m-%d %H:%M")
            data_hora_jogo = data_hora_jogo.replace(tzinfo=fuso_br)
            
            jogos_dict[str(row['Id']).strip()] = {
                "confronto": str(row['Confronto']).strip(), 
                "resultado": res, 
                "encerrado": enc,
                "data_completa": data_hora_jogo
            }
        return jogos_dict
    except:
        return {}

# 3. FUNÇÃO PARA CARREGAR OS PALPITES REAIS
def carregar_palpites():
    try:
        import time
        url = LINK_DA_PLANILHA.replace('/edit?usp=sharing', f'/gviz/tq?tqx=out:csv&sheet=Form_Responses&nocache={time.time()}')
        df = pd.read_csv(url)
        df.columns = [str(col).strip() for col in df.columns]
        
        df = df.dropna(subset=['Participante', 'Jogo', 'Palpite'])
        df = df.drop_duplicates(subset=['Participante', 'Jogo'], keep='last')
        
        lista_palpites = []
        for _, row in df.iterrows():
            lista_palpites.append({
                "Participante": str(row['Participante']).strip(),
                "Jogo": str(row['Jogo']).strip(),
                "Palpite": str(row['Palpite']).strip().upper().replace(" ", "")
            })
        return lista_palpites
    except:
        return []

st.session_state.jogos = carregar_jogos()
st.session_state.palpites = carregar_palpites()

participantes_lista = ["Samuel", "Balthazar", "Thiago", "Julien", "Liliane", "Katia", "Karol", "Bia"]

st.markdown('<div class="header-bolao"><h1>🇧🇷 BOLÃO DA FAMÍLIA 🇧🇷</h1><p>🏆 JOGOS DA RODADA • COPA DO MUNDO</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["✍️ Dar Palpite", "📊 Ver Palpites da Rodada", "🏆 Classificação Geral", "⚙️ Admin"])

# --- ABA 1: PALPITES ---
with tab1:
    st.markdown("""
        <div class="caixa-legenda">
            <h4>🎯 Sistema de Pontuação do Bolão:</h4>
            <ul>
                <li><strong>Placar Exato (Craque da Rodada):</strong> Ganha <strong>10 pontos</strong>.</li>
                <li><strong>Acertou a Tendência (Vencedor ou Empate):</strong> Ganha <strong>4 pontos</strong>.</li>
                <li><strong>Errou tudo:</strong> Ganha <strong>0 pontos</strong>.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("✍️ Escolha um jogo para palpitar")
    nome = st.selectbox("Quem está jogando?", ["Selecione seu nome..."] + participantes_lista)
    
    jogos_disponiveis = {k: v for k, v in st.session_state.jogos.items() if agora_br < v["data_completa"] and not v["encerrado"]}
    
    if not jogos_disponiveis:
        st.info("📆 Não existem partidas abertas para receber palpites no momento!")
    else:
        jogo_selecionado = st.selectbox(
            "Escolha o jogo:", 
            list(jogos_disponiveis.keys()), 
            format_func=lambda x: f"{jogos_disponiveis[x]['confronto']} ({jogos_disponiveis[x]['data_completa'].strftime('%d/%m - %H:%M')})"
        )
        
        if nome != "Selecione seu nome...":
            dados_jogo = jogos_disponiveis[jogo_selecionado]
            
            col1, col2 = st.columns(2)
            with col1:
                gols_1 = st.number_input(f"Gols: {dados_jogo['confronto'].split(' X ')[0]}", min_value=0, value=0, step=1, key="g1")
            with col2:
                gols_2 = st.number_input(f"Gols: {dados_jogo['confronto'].split(' X ')[1]}", min_value=0, value=0, step=1, key="g2")
                
            if st.button("Confirmar Palpite! ⚽"):
                nome_confronto = dados_jogo['confronto']
                placar_string = f"{gols_1} X {gols_2}"
                
                dados_envio = {ENTRY_NOME: nome, ENTRY_JOGO: nome_confronto, ENTRY_PALPITE: placar_string}
                resposta = requests.post(URL_FORM_POST, data=dados_envio)
                
                if resposta.status_code == 200 or "formResponse" in resposta.url:
                    st.success(f"🔥 Perfeito {nome}! Seu palpite ({placar_string}) foi salvo!")
                    st.session_state.palpites = carregar_palpites()
                else:
                    st.error("❌ Erro técnico ao salvar palpite no banco de dados do Google.")

# --- ABA 2: PALPITES DA GALERA ---
with tab2:
    st.subheader("📊 Placar da Galera")
    if st.session_state.palpites:
        df_palpites = pd.DataFrame(st.session_state.palpites)
        st.dataframe(df_palpites[["Participante", "Jogo", "Palpite"]], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum palpite válido encontrado.")

# --- ABA 3: CLASSIFICAÇÃO GERAL ---
with tab3:
    st.subheader("🏆 Classificação Geral da Família")
    pontos = {nome: 0 for nome in participantes_lista}
    
    mapa_jogos = {}
    for j_id, info in st.session_state.jogos.items():
        mapa_jogos[j_id.upper().strip()] = info
        mapa_jogos[info["confronto"].upper().strip()] = info

    for p in st.session_state.palpites:
        jogo_chave = p["Jogo"].upper().strip()
        if jogo_chave in mapa_jogos:
            info_jogo = mapa_jogos[jogo_chave]
            resultado_real = info_jogo["resultado"]
            
            # Só calcula pontuação se o resultado real existir e não for nulo
            if resultado_real and p["Participante"] in pontos:
                res_real_limpo = str(resultado_real).upper().replace(" ", "")
                palpite_limpo = p["Palpite"]
                
                if palpite_limpo == res_real_limpo:
                    pontos[p["Participante"]] += 10
                else:
                    try:
                        g_p1, g_p2 = map(int, palpite_limpo.split("X"))
                        g_r1, g_r2 = map(int, res_real_limpo.split("X"))
                        if (g_p1 > g_p2 and g_r1 > g_r2) or (g_p1 < g_p2 and g_r1 < g_r2) or (g_p1 == g_p2 and g_r1 == g_r2):
                            pontos[p["Participante"]] += 4
                    except: pass
                    
    df_ranking = pd.DataFrame(list(pontos.items()), columns=["Participante", "Pontos"]).sort_values(by="Pontos", ascending=False)
    ranking_visual = [{"Posição": f"{i+1}º 🏅" if i<3 else f"{i+1}º ", "Nome": r.Participante, "Total Pontos": f"{r.Pontos} pts"} for i, r in enumerate(df_ranking.itertuples())]
    st.table(pd.DataFrame(ranking_visual))

# --- ABA 4: ADMIN ---
with tab4:
    st.subheader("⚙️ Painel do Árbitro")
    senha = st.text_input("Senha de administrador:", type="password")
    if senha == "1234":
        st.success("🔓 Acesso Liberado!")
        
        st.markdown("---")
        st.subheader("📝 Inserir Palpite Manual (Retroativo)")
        adm_nome = st.selectbox("Participante:", participantes_lista, key="adm_n")
        adm_jogo_id = st.selectbox("Escolha o Jogo antigo:", list(st.session_state.jogos.keys()), format_func=lambda x: f"{x}: {st.session_state.jogos[x]['confronto']}", key="adm_j")
        
        col_a1, col_a2 = st.columns(2)
        with col_a1: adm_g1 = st.number_input("Gols Time 1:", min_value=0, value=0, step=1, key="adm_g1")
        with col_a2: adm_g2 = st.number_input("Gols Time 2:", min_value=0, value=0, step=1, key="adm_g2")
        
        if st.button("Gravar na Planilha Manualmente 💾"):
            confronto_texto = st.session_state.jogos[adm_jogo_id]['confronto']
            placar_manual = f"{adm_g1} X {adm_g2}"
            
            dados_envio_manual = {ENTRY_NOME: adm_nome, ENTRY_JOGO: confronto_texto, ENTRY_PALPITE: placar_manual}
            requests.post(URL_FORM_POST, data=dados_envio_manual)
            st.success(f"Palpite enviado!")
            st.session_state.palpites = carregar_palpites()
