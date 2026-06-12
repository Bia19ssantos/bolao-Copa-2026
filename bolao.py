import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (Tema Verde e Amarelo)
st.set_page_config(page_title="Bolão da Família - Rumo ao Hexa!", page_icon="🇧🇷", layout="centered")

# Seu link real da planilha do Google já configurado:
LINK_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1Z2I9Uu0wZvyDb4Fqyo-qgPKE8y4ga4279aj-VYfuXb0/edit?usp=sharing"

# Injeção de CSS para unificar o padrão: Elementos escuros com letras brancas
st.markdown("""
    <style>
        /* Fundo geral do app ligeiramente acinzentado para destacar os blocos pretos */
        .stApp { background-color: #f4f4f9; }
        h1, h2, h3 { color: #002776 !important; font-family: 'Arial Black', sans-serif; }
        
        /* Cabeçalho personalizado */
        .header-bolao {
            background: linear-gradient(135deg, #009c3b 0%, #002776 100%);
            color: #ffdf00 !important;
            text-align: center;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-bottom: 25px;
        }
        .header-bolao h1 { color: #ffdf00 !important; margin: 0; font-size: 28px; }
        .header-bolao p { color: #ffffff; margin: 5px 0 0 0; font-weight: bold; font-size: 16px; }

        /* Abas de navegação */
        button[data-baseweb="tab"] {
            font-size: 14px !important;
            font-weight: bold !important;
            color: #002776 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #009c3b !important;
            border-bottom-color: #009c3b !important;
        }

        /* -------------------------------------------------------------
           PADRÃO SEU: TABELAS, COMBOS E CAIXAS PRETAS COM LETRAS BRANCAS
           ------------------------------------------------------------- */
        
        /* 1. CAIXAS DE SELEÇÃO (Combos) E INPUTS DE NÚMERO */
        div[data-baseweb="select"], div[data-baseweb="input"], input, .stNumberInput div {
            background-color: #1e222b !important;
            color: #ffffff !important;
            border-radius: 8px;
        }
        
        /* Forçar o texto dentro dos menus suspensos abertos a ficar BRANCO */
        div[ul], li, span, p, div[data-attributed="true"] {
            color: #ffffff !important;
        }
        
        /* Ajuste específico para rótulos/labels fora das caixas não sumirem */
        label p {
            color: #111111 !important;
            font-weight: bold !important;
        }

        /* 2. TABELAS (Tanto st.dataframe quanto st.table) */
        .stTable, table, data-grid-container, [data-testid="stTable"] {
            background-color: #1e222b !important;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        /* Forçar todas as células, linhas e textos das tabelas a ficarem brancos */
        table tr, table td, th, td, tr, .stTable td, .stTable th {
            background-color: #1e222b !important;
            color: #ffffff !important;
            font-size: 15px !important;
            border-bottom: 1px solid #2d323f !important;
        }
        
        /* Cabeçalho das tabelas ligeiramente destacado em cinza escuro */
        th, table th {
            background-color: #11151c !important;
            font-weight: bold !important;
            color: #ffdf00 !important; /* Destaque amarelo ouro para os títulos das colunas */
        }

        /* Estilo dos botões de envio */
        div.stButton > button:first-child {
            background-color: #009c3b !important;
            color: #ffdf00 !important;
            font-weight: bold !important;
            border: 2px solid #ffdf00 !important;
            border-radius: 10px !important;
            width: 100%;
            padding: 10px 20px !important;
            text-transform: uppercase;
        }
        div.stButton > button:first-child:hover {
            background-color: #002776 !important;
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)


# 2. FUNÇÃO PARA LER OS JOGOS DA SUA PLANILHA DO GOOGLE
def carregar_jogos():
    try:
        # Transforma o link normal em um link de leitura de dados em formato CSV
        url = LINK_DA_PLANILHA.replace('/edit?usp=sharing', '/gviz/tq?tqx=out:csv&sheet=jogos')
        df = pd.read_csv(url)
        jogos_dict = {}
        for _, row in df.iterrows():
            res = None if pd.isna(row['Resultado']) or str(row['Resultado']).strip() == '-' else str(row['Resultado']).strip()
            enc = True if str(row['Encerrado']).lower().strip() == 'true' else False
            jogos_dict[str(row['ID']).strip()] = {"confronto": row['Confronto'], "resultado": res, "encerrado": enc}
        return jogos_dict
    except:
        # Caso a planilha esteja offline ou sem a permissão correta, usa o plano B padrão
        return {
            "Jogo 1": {"confronto": "México 🇲🇽 X 🇿🇦 África do Sul", "resultado": "2 X 0", "encerrado": True},
            "Jogo 2": {"confronto": "Coreia do Sul 🇰🇷 X 🇨🇿 Rep. Tcheca", "resultado": "1 X 0", "encerrado": True},
            "Jogo 3": {"confronto": "Canadá 🇨🇦 X 🇧🇦 Bósnia", "resultado": None, "encerrado": False},
            "Jogo 4": {"confronto": "Brasil 🇧🇷 X 🇭🇷 Croácia", "resultado": None, "encerrado": False},
        }

st.session_state.jogos = carregar_jogos()


# 3. BANCO DE PALPITES (Histórico inicial corrigido)
if "palpites" not in st.session_state:
    st.session_state.palpites = [
        # Jogo 1
        {"Participante": "Samuel", "Jogo": "Jogo 1", "Palpite": "2 X 0"},
        {"Participante": "Balthazar", "Jogo": "Jogo 1", "Palpite": "2 X 1"},
        {"Participante": "Julien", "Jogo": "Jogo 1", "Palpite": "1 X 1"},
        {"Participante": "Liliane", "Jogo": "Jogo 1", "Palpite": "1 X 0"},
        {"Participante": "Thiago", "Jogo": "Jogo 1", "Palpite": "0 X 1"}, 
        # Jogo 2
        {"Participante": "Thiago", "Jogo": "Jogo 2", "Palpite": "3 X 0"},
        # Jogo 3
        {"Participante": "Samuel", "Jogo": "Jogo 3", "Palpite": "0 X 2"},
        {"Participante": "Julien", "Jogo": "Jogo 3", "Palpite": "3 X 0"},
        {"Participante": "Balthazar", "Jogo": "Jogo 3", "Palpite": "2 X 2"},
        {"Participante": "Thiago", "Jogo": "Jogo 3", "Palpite": "1 X 0"},
        {"Participante": "Bia", "Jogo": "Jogo 3", "Palpite": "2 X 0"},
    ]

participantes_lista = ["Samuel", "Balthazar", "Thiago", "Julien", "Liliane", "Katia", "Karol", "Bia"]


# 4. CABEÇALHO DO SITE
st.markdown("""
    <div class="header-bolao">
        <h1>🇧🇷 BOLÃO DA FAMÍLIA 🇧🇷</h1>
        <p>🏆 COPA DO MUNDO • RUMO AO HEXA! ⭐⭐⭐⭐⭐⭐</p>
    </div>
""", unsafe_allow_html=True)


# 5. ESTRUTURA DAS ABAS
tab1, tab2, tab3, tab4 = st.tabs(["✍️ Dar Palpite", "📊 Ver Palpites da Rodada", "🏆 Classificação Geral", "⚙️ Admin"])


# --- ABA 1: DAR PALPITE (Filtrado apenas para jogos Abertos) ---
with tab1:
    st.subheader("✍️ Deixe seu palpite pé-quente")
    
    nome = st.selectbox("Quem está jogando?", ["Selecione seu nome..."] + participantes_lista)
    
    # Mostra apenas os jogos da planilha cujo status 'Encerrado' é False
    jogos_abertos = {k: v for k, v in st.session_state.jogos.items() if not v['encerrado']}
    
    if not jogos_abertos:
        st.info("🎉 Todos os jogos cadastrados já aconteceram ou estão fechados no momento!")
    else:
        jogo_selecionado = st.selectbox(
            "Escolha o jogo:", 
            list(jogos_abertos.keys()), 
            format_func=lambda x: f"{x}: {jogos_abertos[x]['confronto']}"
        )
        
        if nome != "Selecione seu nome...":
            dados_jogo = jogos_abertos[jogo_selecionado]
            st.info(f"⏳ Registre seu palpite para este jogo antes do início da partida.")
            
            col1, col2 = st.columns(2)
            with col1:
                gols_1 = st.number_input(f"Gols: {dados_jogo['confronto'].split(' X ')[0]}", min_value=0, value=0, step=1, key="g1")
            with col2:
                gols_2 = st.number_input(f"Gols: {dados_jogo['confronto'].split(' X ')[1]}", min_value=0, value=0, step=1, key="g2")
                
            if st.button("Confirmar Palpite! ⚽"):
                placar_string = f"{gols_1} X {gols_2}"
                # Remove palpite antigo da mesma pessoa para o mesmo jogo se existir
                st.session_state.palpites = [p for p in st.session_state.palpites if not (p["Participante"] == nome and p["Jogo"] == jogo_selecionado)]
                
                st.session_state.palpites.append({
                    "Participante": nome,
                    "Jogo": jogo_selecionado,
                    "Palpite": placar_string
                })
                st.success(f"🔥 Boa! Palpite salvo para {nome}: {placar_string}. Boa sorte!")


# --- ABA 2: VER PALPITES DA GALERA ---
with tab2:
    st.subheader("📊 Placar da Galera")
    if st.session_state.palpites:
        df_palpites = pd.DataFrame(st.session_state.palpites)
        df_palpites["Confronto"] = df_palpites["Jogo"].map(lambda x: st.session_state.jogos.get(x, {}).get("confronto", "Jogo Desconhecido"))
        df_exibicao = df_palpites[["Participante", "Confronto", "Palpite"]].sort_values(by="Confronto")
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.write("Ninguém palpitou ainda.")


# --- ABA 3: CLASSIFICAÇÃO GERAL (Sistema de 10 e 4 pontos) ---
with tab3:
    st.subheader("🏆 Classificação Geral da Família")
    st.caption("🎯 Regras: Placar exato = 10 pontos | Acertou apenas Vitória/Empate/Derrota = 4 pontos")
    
    pontos = {nome: 0 for nome in participantes_lista}
    
    for p in st.session_state.palpites:
        jogo_id = p["Jogo"]
        if jogo_id in st.session_state.jogos:
            resultado_real = st.session_state.jogos[jogo_id]["resultado"]
            
            if resultado_real and p["Participante"] in pontos: 
                palpite_user = p["Palpite"]
                user = p["Participante"]
                
                if palpite_user == resultado_real:
                    pontos[user] += 10  # Cravou o Placar!
                else:
                    try:
                        g_p1, g_p2 = map(int, palpite_user.split(" X "))
                        g_r1, g_r2 = map(int, resultado_real.split(" X "))
                        
                        # Verifica se acertou a tendência (vitoria, empate ou derrota)
                        if (g_p1 > g_p2 and g_r1 > g_r2) or (g_p1 < g_p2 and g_r1 < g_r2) or (g_p1 == g_p2 and g_r1 == g_r2):
                            pontos[user] += 4  # Acertou o vencedor/empate
                    except:
                        pass
                    
    df_ranking = pd.DataFrame(list(pontos.items()), columns=["Participante", "Pontos"]).sort_values(by="Pontos", ascending=False)
    
    ranking_visual = []
    for idx, row in enumerate(df_ranking.itertuples(), start=1):
        medalha = "🥇 " if idx == 1 else "🥈 " if idx == 2 else "🥉 " if idx == 3 else f"{idx}º "
        ranking_visual.append({"Posição": medalha, "Nome": row.Participante, "Total Pontos": f"{row.Pontos} pts"})
        
    st.table(pd.DataFrame(ranking_visual))


# --- ABA 4: PAINEL DO ÁRBITRO ---
with tab4:
    st.subheader("⚙️ Painel do Árbitro")
    senha = st.text_input("Digite a senha de administrador para liberar:", type="password")
    
    if senha == "1234":
        st.success("🔓 Acesso Liberado!")
        st.info("💡 Como sua planilha do Google está vinculada, a forma definitiva de salvar os jogos para sempre é abrir o aplicativo do Google Planilhas no celular e preencher o resultado lá!")
        
        jogo_adm = st.selectbox("Visualizar jogo via App:", list(st.session_state.jogos.keys()), format_func=lambda x: st.session_state.jogos[x]['confronto'])
        st.write(f"Jogo selecionado: **{st.session_state.jogos[jogo_adm]['confronto']}**")
        st.write(f"Status atual na Planilha -> Resultado: `{st.session_state.jogos[jogo_adm]['resultado']}` | Encerrado: `{st.session_state.jogos[jogo_adm]['encerrado']}`")
    elif senha != "":
        st.error("❌ Senha incorreta!")
