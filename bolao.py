import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone

# 1. CONFIGURAÇÃO DA PÁGINA (Tema Escuro Nativo)
st.set_page_config(page_title="Bolão da Família - Rumo ao Hexa!", page_icon="🇧🇷", layout="centered")

LINK_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1Z2I9Uu0wZvyDb4Fqyo-qgPKE8y4ga4279aj-VYfuXb0/edit?usp=sharing"

# ==================== ATENÇÃO: ATUALIZE ESSES NÚMEROS SE SEU NOVO FORMS NÃO SALVAR ====================
URL_FORM_POST = "https://docs.google.com/forms/d/e/1FAIpQLSe-pFE2N7hUNuJZf8rWXZMrlVkeDULySNF1LSQDUTNepOEJqw/formResponse"
# ATUALIZADO COM OS IDs CORRETOS
ENTRY_NOME = "entry.155949992"    
ENTRY_JOGO = "entry.1025675970"    
ENTRY_PALPITE = "entry.626328654"
# ======================================================================================================

# Define o fuso horário de Brasília (UTC-3) nativamente
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
        
        # Limpeza rigorosa
        df = df.dropna(subset=['Participante', 'Jogo', 'Palpite'])
        # Mantém apenas a última entrada de cada jogo para cada participante
        df = df.sort_values(by=['Participante', 'Jogo']).drop_duplicates(subset=['Participante', 'Jogo'], keep='last')
        
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

# --- ABA 1: PALPITES (Filtrado apenas para os Jogos do Dia) ---
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
    
    # --- LÓGICA PARA FILTRAR APENAS JOGOS DE HOJE ---
  
    inicio_hoje = agora_br.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_hoje = agora_br.replace(hour=23, minute=59, second=59, microsecond=999999)
    limite_tempo = timedelta(minutes=10)
    
  jogos_disponiveis = {
        k: v for k, v in st.session_state.jogos.items() 
        if inicio_hoje <= v["data_completa"] <= fim_hoje 
        and not v["encerrado"] 
        and agora_br < (v["data_completa"] - limite_tempo)
    }
    
    if not jogos_disponiveis:
        st.info("📆 Não existem partidas abertas acontecendo hoje!")
    else:
        jogo_selecionado = st.selectbox(
            "Escolha o jogo:", 
            list(jogos_disponiveis.keys()), 
            format_func=lambda x: f"{jogos_disponiveis[x]['confronto']} ({jogos_disponiveis[x]['data_completa'].strftime('%H:%M')})"
        )
        
        if nome != "Selecione seu nome...":
            dados_jogo = jogos_disponiveis[jogo_selecionado]
            nome_confronto = dados_jogo['confronto']
            
            # --- VALIDAÇÃO SE O USUÁRIO JÁ PALPITOU ---
            ja_palpitou = False
            palpite_anterior = ""
            
            for p in st.session_state.palpites:
                if p["Participante"].lower() == nome.lower() and p["Jogo"].upper().strip() == nome_confronto.upper().strip():
                    ja_palpitou = True
                    palpite_anterior = p["Palpite"]
                    break
            
            if ja_palpitou:
                st.warning(f"⚠️ **{nome}**, você já cadastrou um palpite para este jogo! Seu palpite salvo é: **{palpite_anterior}**.")
                st.info("Não é permitido alterar o palpite após o envio.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    gols_1 = st.number_input(f"Gols: {nome_confronto.split(' X ')[0]}", min_value=0, value=0, step=1, key="g1")
                with col2:
                    gols_2 = st.number_input(f"Gols: {nome_confronto.split(' X ')[1]}", min_value=0, value=0, step=1, key="g2")
                    
                if st.button("Confirmar Palpite! ⚽"):
                    placar_string = f"{gols_1} X {gols_2}"
                    
                    dados_envio = {ENTRY_NOME: nome, ENTRY_JOGO: nome_confronto, ENTRY_PALPITE: placar_string}
                    resposta = requests.post(URL_FORM_POST, data=dados_envio)
                    
                    if resposta.status_code == 200 or "formResponse" in resposta.url:
                        st.success(f"🔥 Perfeito {nome}! Seu palpite ({placar_string}) foi salvo!")
                        st.session_state.palpites = carregar_palpites()
                        st.rerun()
                    else:
                        st.error("❌ Erro técnico ao salvar palpite no banco de dados do Google.")

# --- ABA 2: VER PALPITES DA RODADA ---
with tab2:
    st.subheader("🔍 Buscar Palpites da Galera")
    
    # 1. Filtro por Nome do Participante (Corrigido para evitar NameError)
    opcoes_filtro = ["Todos"] + list(participantes_lista)
    busca_nome = st.selectbox("Filtrar por participante:", opcoes_filtro)
    
    # Criamos um mapa dos resultados dos jogos para conseguir comparar linha por linha
    mapa_resultados = {}
    for j_id, info in st.session_state.jogos.items():
        chave_jogo = str(info["confronto"]).upper().strip()
        if info["resultado"]:
            mapa_resultados[chave_jogo] = {
                "placar": str(info["resultado"]).upper().replace(" ", ""),
                "encerrado": info.get("encerrado", False)
            }
        else:
            mapa_resultados[chave_jogo] = {
                "placar": None,
                "encerrado": info.get("encerrado", False)
            }

    # 2. Filtrar a lista de palpites com base na escolha do usuário
    palpites_filtrados = []
    for p in st.session_state.palpites:
        if busca_nome == "Todos" or p["Participante"].lower() == busca_nome.lower():
            palpites_filtrados.append(p)
            
    # 3. Processar e exibir os palpites com os ícones de acerto
    if len(palpites_filtrados) > 0:
        dados_tabela = []
        
        for p in palpites_filtrados:
            nome_jogo = str(p["Jogo"]).upper().strip()
            palpite_limpo = str(p["Palpite"]).upper().replace(" ", "")
            
            # Ícone padrão caso o jogo ainda não tenha acontecido ou não tenha resultado
            status_icone = "⏳ Aguardando Jogo"
            
            # Se o jogo já tem resultado na planilha, calculamos o ícone
            if nome_jogo in mapa_resultados and mapa_resultados[nome_jogo]["placar"]:
                res_real = mapa_resultados[nome_jogo]["placar"]
                
                # Cenário 1: Acertou o Placar Exato (🟢 Ganhador de 10 pontos)
                if palpite_limpo == res_real:
                    status_icone = "🟢 Placar Exato (+10 pts)"
                else:
                    # Cenário 2: Verificar se acertou a tendência (🟡 Vencedor ou Empate)
                    try:
                        g_p1, g_p2 = map(int, palpite_limpo.split("X"))
                        g_r1, g_r2 = map(int, res_real.split("X"))
                        
                        vencedor_p = 1 if g_p1 > g_p2 else (2 if g_p2 > g_p1 else 0)
                        vencedor_r = 1 if g_r1 > g_r2 else (2 if g_r2 > g_r1 else 0)
                        
                        if vencedor_p == vencedor_r:
                            status_icone = "🟡 Acertou o Vencedor/Empate (+4 pts)"
                        else:
                            # Cenário 3: Errou tudo (🔴 0 pontos)
                            status_icone = "🔴 Errou o palpite (0 pts)"
                    except:
                        status_icone = "❌ Erro no formato do palpite"
            
            # Monta a linha bonita para exibir na tela
            dados_tabela.append({
                "Participante": p["Participante"],
                "Jogo": p["Jogo"],
                "Palpite": p["Palpite"],
                "Desempenho": status_icone
            })
            
        # Transforma em DataFrame e exibe como uma tabela limpa
        df_palpites = pd.DataFrame(dados_tabela)
        st.dataframe(df_palpites, use_container_width=True, hide_index=True)
        
    else:
        st.warning("Nenhum palpite encontrado para os critérios selecionados.")

# --- ABA 3: CLASSIFICAÇÃO GERAL ---
with tab3:
    st.subheader("🏆 Classificação Geral da Família")
    pontos = {nome: 0 for nome in participantes_lista}
    
    # Criamos um mapa de resultados limpos
    mapa_resultados = {}
    for j_id, info in st.session_state.jogos.items():
        if info["resultado"]:
            chave = str(info["confronto"]).upper().strip()
            # Removemos todos os espaços do resultado (ex: "2 X 0" vira "2X0")
            mapa_resultados[chave] = str(info["resultado"]).upper().replace(" ", "")

    for p in st.session_state.palpites:
        chave_palpite = str(p["Jogo"]).upper().strip()
        # Removemos todos os espaços do palpite do usuário
        palpite_limpo = str(p["Palpite"]).upper().replace(" ", "")
        
        if chave_palpite in mapa_resultados:
            res_real = mapa_resultados[chave_palpite]
            
            # 1. Placar Exato (10 pontos)
            if palpite_limpo == res_real:
                pontos[p["Participante"]] += 10
            else:
                # 2. Acertou a tendência (4 pontos)
                try:
                    # Tenta dividir "2X0" em gols
                    g_p1, g_p2 = map(int, palpite_limpo.split("X"))
                    g_r1, g_r2 = map(int, res_real.split("X"))
                    
                    # Verifica vencedor (1=Time1, 2=Time2, 0=Empate)
                    vencedor_p = 1 if g_p1 > g_p2 else (2 if g_p2 > g_p1 else 0)
                    vencedor_r = 1 if g_r1 > g_r2 else (2 if g_r2 > g_r1 else 0)
                    
                    if vencedor_p == vencedor_r:
                        pontos[p["Participante"]] += 4
                except: pass
                    
    # Exibe ranking
    df_ranking = pd.DataFrame(list(pontos.items()), columns=["Participante", "Pontos"]).sort_values(by="Pontos", ascending=False)
    st.table(df_ranking)

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
