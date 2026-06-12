import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

# 1. CONFIGURAÇÃO DA PÁGINA (Tema Escuro Nativo)
st.set_page_config(page_title="Bolão da Família - Rumo ao Hexa!", page_icon="🇧🇷", layout="centered")

LINK_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1Z2I9Uu0wZvyDb4Fqyo-qgPKE8y4ga4279aj-VYfuXb0/edit?usp=sharing"

# Ajuste de Fuso Horário de Brasília (UTC-3) nativo
fuso_br = timezone(timedelta(hours=-3))
agora_br = datetime.now(fuso_br)
hoje_str = agora_br.strftime("%Y-%m-%d")

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

# 2. FUNÇÃO PARA LER OS JOGOS DA PLANILHA (Forçando tempo real)
def carregar_jogos():
    try:
        # Mudamos o link para exportação limpa e adicionamos um marcador aleatório para burlar o cache do Google
        import time
        url = LINK_DA_PLANILHA.replace('/edit?usp=sharing', f'/gviz/tq?tqx=out:csv&sheet=jogos&nocache={time.time()}')
        df = pd.read_csv(url)
        
        # Limpa espaços ocultos nos cabeçalhos
        df.columns = [str(col).strip() for col in df.columns]
        
        jogos_dict = {}
        for _, row in df.iterrows():
            if pd.isna(row['Confronto']) or pd.isna(row['Data']):
                continue
                
            res = None if pd.isna(row['Resultado']) or str(row['Resultado']).strip() == '-' else str(row['Resultado']).strip()
            enc = True if str(row['Encerrado']).lower().strip() == 'true' else False
            
            data_hora_jogo = datetime.strptime(str(row['Data']).strip(), "%Y-%m-%d %H:%M")
            data_hora_jogo = data_hora_jogo.replace(tzinfo=fuso_br)
            data_dia_jogo = data_hora_jogo.strftime("%Y-%m-%d")
            
            jogos_dict[str(row['Id']).strip()] = {
                "confronto": str(row['Confronto']).strip(), 
                "resultado": res, 
                "encerrado": enc,
                "data_completa": data_hora_jogo,
                "dia": data_dia_jogo
            }
        return jogos_dict
    except Exception as e:
        # Plano B de segurança
        return {
            "Jogo 3": {"confronto": "Canadá 🇨🇦 X 🇧🇦 Bósnia", "resultado": None, "encerrado": False, "data_completa": datetime(2026, 6, 12, 16, 0, tzinfo=fuso_br), "dia": "2026-06-12"},
            "Jogo 4": {"confronto": "Estados Unidos 🇺🇸 X 🇵🇾 Paraguai", "resultado": None, "encerrado": False, "data_completa": datetime(2026, 6, 12, 22, 0, tzinfo=fuso_br), "dia": "2026-06-12"},
        }

st.session_state.jogos = carregar_jogos()

# Histórico de palpites salvos na memória
if "palpites" not in st.session_state:
    st.session_state.palpites = [
        {"Participante": "Samuel", "Jogo": "Jogo 1", "Palpite": "2 X 0"},
        {"Participante": "Balthazar", "Jogo": "Jogo 1", "Palpite": "2 X 1"},
        {"Participante": "Julien", "Jogo": "Jogo 1", "Palpite": "1 X 1"},
        {"Participante": "Liliane", "Jogo": "Jogo 1", "Palpite": "1 X 0"},
        {"Participante": "Thiago", "Jogo": "Jogo 1", "Palpite": "0 X 1"}, 
        {"Participante": "Thiago", "Jogo": "Jogo 2", "Palpite": "3 X 0"},
        {"Participante": "Samuel", "Jogo": "Jogo 3", "Palpite": "0 X 2"},
        {"Participante": "Julien", "Jogo": "Jogo 3", "Palpite": "3 X 0"},
        {"Participante": "Balthazar", "Jogo": "Jogo 3", "Palpite": "2 X 2"},
        {"Participante": "Thiago", "Jogo": "Jogo 3", "Palpite": "1 X 0"},
        {"Participante": "Bia", "Jogo": "Jogo 3", "Palpite": "2 X 0"},
    ]

participantes_lista = ["Samuel", "Balthazar", "Thiago", "Julien", "Liliane", "Katia", "Karol", "Bia"]

st.markdown('<div class="header-bolao"><h1>🇧🇷 BOLÃO DA FAMÍLIA 🇧🇷</h1><p>🏆 JOGOS DE HOJE • COPA DO MUNDO</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["✍️ Dar Palpite", "📊 Ver Palpites da Rodada", "🏆 Classificação Geral", "⚙️ Admin"])

# --- ABA 1: PALPITES APENAS DO DIA ---
with tab1:
    st.subheader("✍️ Palpites para os jogos de Hoje")
    st.write(f"📅 Data de hoje no sistema: **{agora_br.strftime('%d/%m/%Y')}**")
    
    nome = st.selectbox("Quem está jogando?", ["Selecione seu nome..."] + participantes_lista)
    
    # Filtra apenas partidas programadas para a data de hoje
    jogos_de_hoje = {k: v for k, v in st.session_state.jogos.items() if v['dia'] == hoje_str}
    
    if not jogos_de_hoje:
        st.info("📆 Não existem partidas agendadas para o dia de hoje na sua planilha!")
    else:
        jogo_selecionado = st.selectbox(
            "Escolha o jogo de hoje:", 
            list(jogos_de_hoje.keys()), 
            format_func=lambda x: f"{jogos_de_hoje[x]['confronto']} ({jogos_de_hoje[x]['data_completa'].strftime('%H:%M')})"
        )
        
        if nome != "Selecione seu nome...":
            dados_jogo = jogos_de_hoje[jogo_selecionado]
            
            # Bloqueia o palpite se o relógio passou do horário de início do jogo
            if agora_br > dados_jogo["data_completa"] or dados_jogo["encerrado"]:
                st.error("❌ Bloqueado! Esta partida já começou ou foi encerrada. Não é mais possível registrar palpites para ela.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    gols_1 = st.number_input(f"Gols: {dados_jogo['confronto'].split(' X ')[0]}", min_value=0, value=0, step=1, key="g1")
                with col2:
                    gols_2 = st.number_input(f"Gols: {dados_jogo['confronto'].split(' X ')[1]}", min_value=0, value=0, step=1, key="g2")
                    
                if st.button("Confirmar Palpite! ⚽"):
                    placar_string = f"{gols_1} X {gols_2}"
                    st.session_state.palpites = [p for p in st.session_state.palpites if not (p["Participante"] == nome and p["Jogo"] == jogo_selecionado)]
                    st.session_state.palpites.append({"Participante": nome, "Jogo": jogo_selecionado, "Palpite": placar_string})
                    st.success(f"🔥 Palpite salvo para {nome}: {placar_string}!")

# --- ABA 2: PALPITES DA GALERA ---
with tab2:
    st.subheader("📊 Placar da Galera")
    if st.session_state.palpites:
        df_palpites = pd.DataFrame(st.session_state.palpites)
        df_palpites["Confronto"] = df_palpites["Jogo"].map(lambda x: st.session_state.jogos.get(x, {}).get("confronto", "Outras Rodadas"))
        st.dataframe(df_palpites[["Participante", "Confronto", "Palpite"]], use_container_width=True, hide_index=True)

# --- ABA 3: CLASSIFICAÇÃO GERAL ---
with tab3:
    st.subheader("🏆 Classificação Geral da Família")
    pontos = {nome: 0 for nome in participantes_lista}
    
    for p in st.session_state.palpites:
        jogo_id = p["Jogo"]
        if jogo_id in st.session_state.jogos:
            resultado_real = st.session_state.jogos[jogo_id]["resultado"]
            if resultado_real and p["Participante"] in pontos: 
                if p["Palpite"] == resultado_real:
                    pontos[p["Participante"]] += 10
                else:
                    try:
                        g_p1, g_p2 = map(int, p["Palpite"].split(" X "))
                        g_r1, g_r2 = map(int, resultado_real.split(" X "))
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
        jogo_adm = st.selectbox("Verificar jogo:", list(st.session_state.jogos.keys()), format_func=lambda x: st.session_state.jogos[x]['confronto'])
        st.write(f"Status -> Placar: `{st.session_state.jogos[jogo_adm]['resultado']}` | Fechado: `{st.session_state.jogos[jogo_adm]['encerrado']}`")
