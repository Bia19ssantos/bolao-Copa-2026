import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (Tema Verde e Amarelo via CSS)
st.set_page_config(page_title="Bolão da Família - Rumo ao Hexa!", page_icon="🇧🇷", layout="centered")

# Injeção de CSS para deixar o app com a cara da Seleção Brasileira
st.markdown("""
    <style>
        /* Fundo e textos gerais */
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

        /* Estilo dos botões */
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
        
        /* Destacando os palpites */
        .badge-palpite {
            background-color: #ffdf00;
            color: #002776;
            padding: 3px 10px;
            border-radius: 5px;
            font-weight: bold;
        }
    </style>
""", unsafe_scale=True, unsafe_allow_html=True)


# 2. BANCO DE DADOS INICIAL
if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "Jogo 1": {"confronto": "México 🇲🇽 X 🇿🇦 África do Sul", "limite": datetime(2026, 6, 11, 12, 0), "resultado": "2 X 0", "encerrado": True},
        "Jogo 2": {"confronto": "Coreia do Sul 🇰🇷 X 🇨🇿 Rep. Tcheca", "limite": datetime(2026, 6, 11, 15, 0), "resultado": "3 X 0", "encerrado": True},
        "Jogo 3": {"confronto": "Canadá 🇨🇦 X 🇧🇦 Bósnia", "limite": datetime(2026, 6, 12, 16, 0), "resultado": None, "encerrado": False},
        "Jogo 4": {"confronto": "Brasil 🇧🇷 X 🇭🇷 Croácia (Estreia rumo ao Hexa! ⭐)", "limite": datetime(2026, 6, 13, 16, 0), "resultado": None, "encerrado": False},
    }

if "palpites" not in st.session_state:
    st.session_state.palpites = [
        # Jogo 1
        {"Participante": "Samuel", "Jogo": "Jogo 1", "Palpite": "2 X 0"},
        {"Participante": "Balthazar", "Jogo": "Jogo 1", "Palpite": "2 X 1"},
        {"Participante": "Thiago", "Jogo": "Jogo 1", "Palpite": "0 X 0"}, 
        {"Participante": "Julien", "Jogo": "Jogo 1", "Palpite": "1 X 1"},
        {"Participante": "Liliane", "Jogo": "Jogo 1", "Palpite": "1 X 0"},
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


# 3. CABEÇALHO DA SELEÇÃO
st.markdown("""
    <div class="header-bolao">
        <h1>🇧🇷 BOLÃO DA FAMÍLIA 🇧🇷</h1>
        <p>🏆 COPA DO MUNDO 2026 • RUMO AO HEXA! ⭐️⭐️⭐️⭐️⭐️⭐️</p>
    </div>
""", unsafe_allow_html=True)


# 4. CRIAÇÃO DAS ABAS
tab1, tab2, tab3 = st.tabs(["✍️ Dar Palpite", "📊 Ver Palpites da Rodada", "🏆 Classificação Geral"])

# --- ABA 1: REGISTRAR PALPITE ---
with tab1:
    st.subheader("✍️ Deixe seu palpite pé-quente")
    
    nome = st.selectbox("Quem está jogando?", ["Selecione seu nome..."] + participantes_lista)
    
    # Criar uma lista amigável de opções mostrando se o jogo está aberto ou fechado
    opcoes_jogos = {}
    horario_atual = datetime.now()
    
    for k, v in st.session_state.jogos.items():
        status = "🔒 FECHADO" if (horario_atual > v["limite"] or v["encerrado"]) else "⏳ ABERTO"
        destaque_brasil = "⭐ " if "Brasil" in v["confronto"] else ""
        opcoes_jogos[k] = f"{destaque_brasil}{k}: {v['confronto']} ({status})"
        
    jogo_selecionado = st.selectbox("Escolha o jogo:", list(opcoes_jogos.keys()), format_func=lambda x: opcoes_jogos[x])
    
    if nome != "Selecione seu nome...":
        dados_jogo = st.session_state.jogos[jogo_selecionado]
        
        # Validação do Horário Limite
        if horario_atual > dados_jogo["limite"] or dados_jogo["encerrado"]:
            st.error(f"❌ O tempo acabou! Esse jogo fechou em: {dados_jogo['limite'].strftime('%d/%m/%Y %H:%M')}")
        else:
            st.info(f"⏳ Você tem até {dados_jogo['limite'].strftime('%d/%m às %H:%M')} para registrar seu placar.")
            
            # Inputs lado a lado para o placar
            col1, col2 = st.columns(2)
            with col1:
                gols_1 = st.number_input(f"Gols: {dados_jogo['confronto'].split(' X ')[0]}", min_value=0, value=0, step=1, key="g1")
            with col2:
                gols_2 = st.number_input(f"Gols: {dados_jogo['confronto'].split(' X ')[1].split(' (')[0]}", min_value=0, value=0, step=1, key="g2")
                
            if st.button("Confirmar Palpite! ⚽"):
                placar_string = f"{gols_1} X {gols_2}"
                
                # Evita duplicados (remove palpite antigo se o mesmo usuário alterar antes do prazo)
                st.session_state.palpites = [p for p in st.session_state.palpites if not (p["Participante"] == nome and p["Jogo"] == jogo_selecionado)]
                
                # Salva o palpite
                st.session_state.palpites.append({
                    "Participante": nome,
                    "Jogo": jogo_selecionado,
                    "Palpite": placar_string
                })
                st.success(f"🔥 Boa! Palpite salvo para {nome}: {placar_string}. Bora buscar esse Hexa! 🇧🇷")

# --- ABA 2: VER PALPITES ---
with tab2:
    st.subheader("📊 Placar da Galera")
    if st.session_state.palpites:
        df_palpites = pd.DataFrame(st.session_state.palpites)
        df_palpites["Confronto"] = df_palpites["Jogo"].map(lambda x: st.session_state.jogos[x]["confronto"])
        
        # Reorganizando as colunas para exibição bonita
        df_exibicao = df_palpites[["Participante", "Confronto", "Palpite"]].sort_values(by="Confronto")
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.write("Ninguém palpitou ainda.")

# --- ABA 3: RANKING ---
with tab3:
    st.subheader("🏆 Classificação da Família")
    st.caption("🎯 Regras: Placar em cheio = 3 pontos | Acertou Vencedor/Empate = 1 ponto")
    
    # Dicionário de pontos zerado para todos
    pontos = {nome: 0 for nome in participantes_lista}
    
    for p in st.session_state.palpites:
        jogo_id = p["Jogo"]
        resultado_real = st.session_state.jogos[jogo_id]["resultado"]
        
        if resultado_real and p["Participante"] in pontos: 
            palpite_user = p["Palpite"]
            user = p["Participante"]
            
            if palpite_user == resultado_real:
                pontos[user] += 3  # Cravou o placar
            else:
                # Venceu o time certo ou deu o empate certo
                try:
                    g_p1, g_p2 = map(int, palpite_user.split(" X "))
                    g_r1, g_r2 = map(int, resultado_real.split(" X "))
                    
                    if (g_p1 > g_p2 and g_r1 > g_r2) or (g_p1 < g_p2 and g_r1 < g_r2) or (g_p1 == g_p2 and g_r1 == g_r2):
                        pontos[user] += 1
                except:
                    pass
                    
    # Formatação da tabela de Ranking
    df_ranking = pd.DataFrame(list(pontos.items()), columns=["Participante", "Pontos"]).sort_values(by="Pontos", ascending=False)
    
    # Adicionando medalhas visuais para o Top 3
    ranking_visual = []
    for idx, row in enumerate(df_ranking.itertuples(), start=1):
        medalha = "🥇 " if idx == 1 else "🥈 " if idx == 2 else "🥉 " if idx == 3 else f"{idx}º "
        ranking_visual.append({"Posição": medalha, "Nome": row.Participante, "Total Pontos": f"{row.Pontos} pts"})
        
    st.table(pd.DataFrame(ranking_visual))