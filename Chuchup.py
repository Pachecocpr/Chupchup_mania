import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão Chup Chup Mania - NextGen", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- APLICAÇÃO DE CSS FUTURISTA (DARK NEON TECH) ---
st.markdown("""
    <style>
    /* Oculta marcas d'água e elementos nativos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Estilização e Destaque do Botão Sanduíche (Sidebar Toggle) */
    button[data-testid="stHeaderIconButton"] {
        color: #00F0FF !important;
        background-color: rgba(0, 240, 255, 0.1) !important;
        border: 1px solid #00F0FF !important;
        border-radius: 8px !important;
    }

    /* Fundo Geral da Aplicação */
    .stApp {
        background: linear-gradient(135deg, #0A0E17 0%, #161F33 100%) !important;
        font-family: 'Segoe UI', Roboto, sans-serif !important;
        color: #E2E8F0 !important;
    }

    /* Cards e Containers Futuristas */
    div[data-testid="stForm"], div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.75) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        border: 1px solid rgba(0, 240, 255, 0.2) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 240, 255, 0.1) !important;
        backdrop-filter: blur(12px) !important;
    }

    /* Títulos em Neon */
    h1, h2, h3 {
        color: #00F0FF !important;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.4) !important;
        font-weight: 700 !important;
    }

    /* Botão Principal em Gradiente Neon */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(90deg, #7928CA 0%, #FF0080 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 15px rgba(255, 0, 128, 0.4) !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 25px rgba(255, 0, 128, 0.7) !important;
    }

    /* Barra Lateral Futurista */
    section[data-testid="stSidebar"] {
        background-color: #0D1117 !important;
        border-right: 1px solid rgba(0, 240, 255, 0.2) !important;
    }

    section[data-testid="stSidebar"] *, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
    }

    /* Cards de Métricas */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        border: 1px solid rgba(255, 0, 128, 0.3) !important;
        box-shadow: 0 0 12px rgba(255, 0, 128, 0.15) !important;
    }

    /* Inputs e Selects com Borda Glow */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #090D16 !important;
        color: #00F0FF !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
    }

    /* Imagens com Borda Neon */
    img {
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SENHA DO ADMINISTRADOR ---
SENHA_ADMIN = "1234"

# --- ARQUIVOS DE IMAGENS LOCAL ---
NOME_BANNER = "banner.jpg"
NOME_PIX = "pix.png"

# --- ARQUIVOS DE DADOS ---
ARQUIVO_ESTOQUE = "estoque_chupchup.csv"
ARQUIVO_VENDAS = "historico_vendas.csv"
ARQUIVO_PEDIDOS = "pedidos_pendentes.csv"
ARQUIVO_CONFIG = "config_pix.json"

COLUNAS_ESTOQUE = ["Sabor", "Categoria", "Estoque", "Preco"]
COLUNAS_VENDAS = ["ID", "Data_Hora", "Cliente", "Sabor", "Quantidade", "Valor_Total", "Forma_Pagamento"]
COLUNAS_PEDIDOS = ["ID", "Data_Hora", "Cliente", "Sabor", "Quantidade", "Valor_Total", "Forma_Pagamento", "Status"]

# --- FUNÇÕES DE CARREGAMENTO E SALVAMENTO ---

def inicializar_arquivos():
    if not os.path.exists(ARQUIVO_ESTOQUE):
        estoque_inicial = pd.DataFrame([
            {"Sabor": "Coco c/ abacaxi", "Categoria": "Gourmet", "Estoque": 15, "Preco": 5.00},
            {"Sabor": "Coco", "Categoria": "Tradicional", "Estoque": 15, "Preco": 4.00},
            {"Sabor": "Chocolate c/ avelã", "Categoria": "Gourmet", "Estoque": 20, "Preco": 6.00},
            {"Sabor": "Chocolate", "Categoria": "Ao Leite", "Estoque": 15, "Preco": 5.00},
            {"Sabor": "Maracujá", "Categoria": "Fruta", "Estoque": 15, "Preco": 4.00},
            {"Sabor": "Ninho c/ morango", "Categoria": "Gourmet", "Estoque": 20, "Preco": 6.00},
            {"Sabor": "Ninho c/ nutella", "Categoria": "Gourmet", "Estoque": 20, "Preco": 6.00},
            {"Sabor": "Amendoim", "Categoria": "Gourmet", "Estoque": 15, "Preco": 5.00},
        ])
        estoque_inicial.to_csv(ARQUIVO_ESTOQUE, index=False)

    if not os.path.exists(ARQUIVO_VENDAS):
        pd.DataFrame(columns=COLUNAS_VENDAS).to_csv(ARQUIVO_VENDAS, index=False)

    if not os.path.exists(ARQUIVO_PEDIDOS):
        pd.DataFrame(columns=COLUNAS_PEDIDOS).to_csv(ARQUIVO_PEDIDOS, index=False)

    if not os.path.exists(ARQUIVO_CONFIG):
        config_inicial = {
            "chave_pix": "31993507169",
            "nome_recebedor": "CHUP CHUP MANIA",
            "cidade_recebedor": "BELO HORIZONTE"
        }
        with open(ARQUIVO_CONFIG, "w") as f:
            json.dump(config_inicial, f)

def carregar_dados():
    estoque = pd.read_csv(ARQUIVO_ESTOQUE)
    vendas = pd.read_csv(ARQUIVO_VENDAS)
    pedidos = pd.read_csv(ARQUIVO_PEDIDOS)
    with open(ARQUIVO_CONFIG, "r") as f:
        config = json.load(f)
    return estoque, vendas, pedidos, config

def salvar_estoque(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

def salvar_vendas(df):
    df.to_csv(ARQUIVO_VENDAS, index=False)

def salvar_pedidos(df):
    df.to_csv(ARQUIVO_PEDIDOS, index=False)

def salvar_config(config):
    with open(ARQUIVO_CONFIG, "w") as f:
        json.dump(config, f)

# --- GERADOR DE PIX E QR CODE ---

def calcular_crc16(payload):
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            if (crc & 0x8000) != 0:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"

def gerar_payload_pix(chave, nome, cidade, valor, txid="***"):
    nome = nome[:25].upper()
    cidade = cidade[:15].upper()
    valor_str = f"{valor:.2f}"
    
    gui = "0014br.gov.bcb.pix"
    key = f"01{len(chave):02d}{chave}"
    merchant_account = f"26{len(gui + key):02d}{gui}{key}"
    
    cat = "52040000"
    currency = "5303986"
    amount = f"54{len(valor_str):02d}{valor_str}"
    country = "5802BR"
    merchant_name = f"59{len(nome):02d}{nome}"
    merchant_city = f"60{len(cidade):02d}{cidade}"
    
    txid_str = f"05{len(txid):02d}{txid}"
    additional_data = f"62{len(txid_str):02d}{txid_str}"
    
    payload_sem_crc = (
        f"000201{merchant_account}{cat}{currency}{amount}{country}"
        f"{merchant_name}{merchant_city}{additional_data}6304"
    )
    
    crc = calcular_crc16(payload_sem_crc)
    return payload_sem_crc + crc

def obter_url_qr_code(texto):
    texto_encoded = urllib.parse.quote(texto)
    return f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={texto_encoded}"

# --- CARREGAMENTO INICIAL ---
inicializar_arquivos()
estoque_df, vendas_df, pedidos_df, config_pix = carregar_dados()

try:
    eh_cliente = st.query_params.get("modo") == "cliente"
except Exception:
    eh_cliente = False

# ==========================================
# 📱 INTERFACE DO CLIENTE
# ==========================================
if eh_cliente:
    if os.path.exists(NOME_BANNER):
        st.image(NOME_BANNER, use_container_width=True)

    st.header("🍦 Faça seu Pedido Online")
    st.write("Escolha seus sabores preferidos e garanta o seu geladinho!")

    estoque_disponivel = estoque_df[estoque_df["Estoque"] > 0]

    if estoque_disponivel.empty:
        st.warning("Desculpe, todos os nossos chup chups estão esgotados no momento! 😢")
    else:
        with st.form("form_pedido"):
            cliente_nome = st.text_input("Seu Nome:")
            
            sabor_selecionado = st.selectbox("Escolha o Sabor:", estoque_disponivel["Sabor"].unique())
            
            detalhes_item = estoque_disponivel[estoque_disponivel["Sabor"] == sabor_selecionado].iloc[0]
            preco_unitario = float(detalhes_item["Preco"])
            max_qtd = int(detalhes_item["Estoque"])
            
            st.info(f"Categoria: **{detalhes_item['Categoria']}** | Preço Unitário: **R$ {preco_unitario:.2f}**")

            quantidade = st.number_input("Quantidade:", min_value=1, max_value=max_qtd, value=1)
            forma_pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Dinheiro", "Cartão de Crédito/Débito"])

            valor_total = preco_unitario * quantidade
            st.markdown(f"### **Total: R$ {valor_total:.2f}**")

            btn_confirmar = st.form_submit_button("🛒 Confirmar Pedido")

        if btn_confirmar:
            if not cliente_nome.strip():
                st.error("Por favor, informe seu nome para identificarmos o pedido.")
            else:
                novo_id = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                novo_pedido = {
                    "ID": novo_id,
                    "Data_Hora": data_hora,
                    "Cliente": cliente_nome,
                    "Sabor": sabor_selecionado,
                    "Quantidade": quantidade,
                    "Valor_Total": valor_total,
                    "Forma_Pagamento": forma_pagamento,
                    "Status": "Pendente"
                }

                pedidos_df = pd.concat([pedidos_df, pd.DataFrame([novo_pedido])], ignore_index=True)
                salvar_pedidos(pedidos_df)

                st.success("✅ Pedido enviado com sucesso!")

                if forma_pagamento == "Pix":
                    st.subheader("📲 Pagamento via Pix")
                    st.write("Escaneie o QR Code abaixo com o aplicativo do seu banco para realizar o pagamento:")
                    
                    payload = gerar_payload_pix(
                        chave=config_pix["chave_pix"],
                        nome=config_pix["nome_recebedor"],
                        cidade=config_pix["cidade_recebedor"],
                        valor=valor_total,
                        txid=novo_id[-10:]
                    )
                    
                    url_qr = obter_url_qr_code(payload)
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(url_qr, width=220)
                    with col2:
                        st.write(f"**Chave Pix:** {config_pix['chave_pix']}")
                        st.write(f"**Valor:** R$ {valor_total:.2f}")
                        st.text_area("Copia e Cola Pix:", payload, height=100)

# ==========================================
# 📊 GESTÃO CHUP CHUP MANIA (MODO ADM)
# ==========================================
else:
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        if os.path.exists(NOME_BANNER):
            st.image(NOME_BANNER, width=110)
    with col_titulo:
        st.title("⚡ Gestão Chup Chup Mania")
        st.write("Sistema Integrado de Vendas, Pedidos e Controle de Estoque")

    st.divider()

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_login, _ = st.columns([2, 1])
        with col_login:
            with st.form("form_login"):
                st.subheader("🔑 Acesso Restrito")
                senha_input = st.text_input("Senha de Acesso:", type="password")
                btn_entrar = st.form_submit_button("Acessar Painel")

                if btn_entrar:
                    if senha_input == SENHA_ADMIN:
                        st.session_state["autenticado"] = True
                        st.success("Acesso autorizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Senha de acesso incorreta.")
    else:
        st.sidebar.title("⚙️ Painel de Gestão")
        
        if os.path.exists(NOME_BANNER):
            st.sidebar.image(NOME_BANNER, use_container_width=True)

        if st.sidebar.button("🚪 Sair do Sistema"):
            st.session_state["autenticado"] = False
            st.rerun()

        opcao_menu = st.sidebar.radio(
            "Navegação",
            ["📋 Fila de Pedidos", "📦 Controle de Estoque", "📊 Relatório de Vendas", "⚙️ Configurações & QR Code"]
        )

        # 1. FILA DE PEDIDOS
        if opcao_menu == "📋 Fila de Pedidos":
            st.header("📋 Fila de Pedidos Recebidos")
            
            pedidos_pendentes = pedidos_df[pedidos_df["Status"] == "Pendente"]

            if pedidos_pendentes.empty:
                st.info("Nenhum pedido pendente na fila no momento.")
            else:
                for idx, row in pedidos_pendentes.iterrows():
                    with st.expander(f"Pedido #{row['ID']} — {row['Cliente']} (R$ {row['Valor_Total']:.2f})"):
                        st.write(f"**Data/Hora:** {row['Data_Hora']}")
                        st.write(f"**Sabor:** {row['Sabor']} x {row['Quantidade']}")
                        st.write(f"**Forma de Pagamento:** {row['Forma_Pagamento']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ Concluir Pedido", key=f"entregar_{row['ID']}"):
                                idx_est = estoque_df[estoque_df["Sabor"] == row["Sabor"]].index
                                if not idx_est.empty:
                                    estoque_df.loc[idx_est, "Estoque"] -= row["Quantidade"]
                                    salvar_estoque(estoque_df)

                                nova_venda = {
                                    "ID": row["ID"],
                                    "Data_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "Cliente": row["Cliente"],
                                    "Sabor": row["Sabor"],
                                    "Quantidade": row["Quantidade"],
                                    "Valor_Total": row["Valor_Total"],
                                    "Forma_Pagamento": row["Forma_Pagamento"]
                                }
                                vendas_df = pd.concat([vendas_df, pd.DataFrame([nova_venda])], ignore_index=True)
                                salvar_vendas(vendas_df)

                                pedidos_df.loc[pedidos_df["ID"] == row["ID"], "Status"] = "Concluído"
                                salvar_pedidos(pedidos_df)

                                st.success("Pedido concluído e faturamento atualizado!")
                                st.rerun()

                        with col2:
                            if st.button(f"❌ Cancelar", key=f"cancelar_{row['ID']}"):
                                pedidos_df.loc[pedidos_df["ID"] == row["ID"], "Status"] = "Cancelado"
                                salvar_pedidos(pedidos_df)
                                st.warning("Pedido cancelado com sucesso.")
                                st.rerun()

        # 2. CONTROLE DE ESTOQUE
        elif opcao_menu == "📦 Controle de Estoque":
            st.header("📦 Estoque Atual")
            st.dataframe(estoque_df, use_container_width=True)

            st.subheader("➕ Atualizar ou Cadastrar Sabor")
            with st.form("form_estoque"):
                sabor = st.text_input("Sabor do Geladinho:")
                categoria = st.selectbox("Categoria:", ["Gourmet", "Tradicional", "Fruta", "Ao Leite", "Alcoólico"])
                qtd = st.number_input("Quantidade em Estoque:", min_value=0, value=15)
                preco = st.number_input("Preço Unitário (R$):", min_value=0.0, value=5.00, step=0.50)

                btn_salvar = st.form_submit_button("Atualizar Estoque")

                if btn_salvar:
                    if not sabor.strip():
                        st.error("Informe o nome do sabor.")
                    else:
                        if sabor in estoque_df["Sabor"].values:
                            estoque_df.loc[estoque_df["Sabor"] == sabor, ["Categoria", "Estoque", "Preco"]] = [categoria, qtd, preco]
                        else:
                            novo_item = {"Sabor": sabor, "Categoria": categoria, "Estoque": qtd, "Preco": preco}
                            estoque_df = pd.concat([estoque_df, pd.DataFrame([novo_item])], ignore_index=True)

                        salvar_estoque(estoque_df)
                        st.success(f"Estoque de **{sabor}** atualizado!")
                        st.rerun()

        # 3. RELATÓRIO DE VENDAS (COM CANCELAMENTO E DEVOLUÇÃO AO ESTOQUE)
        elif opcao_menu == "📊 Relatório de Vendas":
            st.header("📊 Faturamento e Desempenho")

            if vendas_df.empty:
                st.info("Nenhuma venda registrada até o momento.")
            else:
                faturamento_total = vendas_df["Valor_Total"].sum()
                total_itens = vendas_df["Quantidade"].sum()

                col1, col2 = st.columns(2)
                col1.metric("💰 Faturamento Acumulado", f"R$ {faturamento_total:.2f}")
                col2.metric("🍦 Total de Unidades Vendidas", f"{total_itens} un")

                st.subheader("Cancelar Venda e Retornar ao Estoque")
                venda_selecionada_id = st.selectbox(
                    "Selecione o ID da Venda para Cancelar:", 
                    vendas_df["ID"].unique()
                )

                if st.button("🔄 Cancelar Venda Selecionada e Estornar Estoque"):
                    venda_info = vendas_df[vendas_df["ID"] == venda_selecionada_id].iloc[0]
                    sabor_venda = venda_info["Sabor"]
                    qtd_venda = int(venda_info["Quantidade"])

                    idx_est = estoque_df[estoque_df["Sabor"] == sabor_venda].index
                    if not idx_est.empty:
                        estoque_df.loc[idx_est, "Estoque"] += qtd_venda
                        salvar_estoque(estoque_df)

                    vendas_df = vendas_df[vendas_df["ID"] != venda_selecionada_id]
                    salvar_vendas(vendas_df)

                    st.success(f"Venda {venda_selecionada_id} cancelada! {qtd_venda} unidade(s) de '{sabor_venda}' retornaram ao estoque.")
                    st.rerun()

                st.divider()
                st.subheader("Histórico Detalhado")
                st.dataframe(vendas_df.sort_values(by="Data_Hora", ascending=False), use_container_width=True)

        # 4. CONFIGURAÇÕES & QR CODE (COM IMAGEM LOCAL PIX.PNG)
        elif opcao_menu == "⚙️ Configurações & QR Code":
            st.header("⚙️ Configurações Gerais")

            col_pix_logo, col_pix_tit = st.columns([1, 4])
            with col_pix_logo:
                if os.path.exists(NOME_PIX):
                    st.image(NOME_PIX, width=130)
            with col_pix_tit:
                st.subheader("🔑 Cadastro da Chave Pix (Banco Central)")

            with st.form("form_config_pix"):
                chave = st.text_input("Chave Pix:", value=config_pix["chave_pix"])
                nome = st.text_input("Nome do Titular:", value=config_pix["nome_recebedor"])
                cidade = st.text_input("Cidade:", value=config_pix["cidade_recebedor"])

                btn_salvar_pix = st.form_submit_button("Salvar Dados Pix")

                if btn_salvar_pix:
                    config_pix["chave_pix"] = chave
                    config_pix["nome_recebedor"] = nome
                    config_pix["cidade_recebedor"] = cidade
                    salvar_config(config_pix)
                    st.success("Configurações do Pix atualizadas com sucesso!")

            st.divider()

            url_atual = st.context.headers.get("host", "chupchup-mania.streamlit.app")
            link_cliente = f"https://{url_atual}/?modo=cliente"

            st.subheader("📲 Link e QR Code do Cardápio Digital")
            st.write("Link exclusivo para envio aos clientes:")
            st.code(link_cliente)

            st.write("QR Code gerado para o cardápio dos clientes:")
            url_qr_cliente = obter_url_qr_code(link_cliente)
            st.image(url_qr_cliente, caption="Cardápio Digital Chup Chup Mania", width=220)
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SENHA DO ADMINISTRADOR ---
SENHA_ADMIN = "1234"

# --- URL DA IMAGEM DO PIX BANCO CENTRAL ---
URL_PIX_BACEN = "https://upload.wikimedia.org/wikipedia/commons/a/a2/Logo%E2%80%94pix_powered_by_Banco_Central_%28Brazil%2C_2020%29.svg"

# --- ARQUIVOS DE DADOS ---
ARQUIVO_ESTOQUE = "estoque_chupchup.csv"
ARQUIVO_VENDAS = "historico_vendas.csv"
ARQUIVO_PEDIDOS = "pedidos_pendentes.csv"
ARQUIVO_CONFIG = "config_pix.json"
NOME_BANNER = "banner.jpg"

COLUNAS_ESTOQUE = ["Sabor", "Categoria", "Estoque", "Preco"]
COLUNAS_VENDAS = ["ID", "Data_Hora", "Cliente", "Sabor", "Quantidade", "Valor_Total", "Forma_Pagamento"]
COLUNAS_PEDIDOS = ["ID", "Data_Hora", "Cliente", "Sabor", "Quantidade", "Valor_Total", "Forma_Pagamento", "Status"]

# --- FUNÇÕES DE CARREGAMENTO E SALVAMENTO ---

def inicializar_arquivos():
    if not os.path.exists(ARQUIVO_ESTOQUE):
        estoque_inicial = pd.DataFrame([
            {"Sabor": "Coco c/ abacaxi", "Categoria": "Gourmet", "Estoque": 15, "Preco": 5.00},
            {"Sabor": "Coco", "Categoria": "Tradicional", "Estoque": 15, "Preco": 4.00},
            {"Sabor": "Chocolate c/ avelã", "Categoria": "Gourmet", "Estoque": 20, "Preco": 6.00},
            {"Sabor": "Chocolate", "Categoria": "Ao Leite", "Estoque": 15, "Preco": 5.00},
            {"Sabor": "Maracujá", "Categoria": "Fruta", "Estoque": 15, "Preco": 4.00},
            {"Sabor": "Ninho c/ morango", "Categoria": "Gourmet", "Estoque": 20, "Preco": 6.00},
            {"Sabor": "Ninho c/ nutella", "Categoria": "Gourmet", "Estoque": 20, "Preco": 6.00},
            {"Sabor": "Amendoim", "Categoria": "Gourmet", "Estoque": 15, "Preco": 5.00},
        ])
        estoque_inicial.to_csv(ARQUIVO_ESTOQUE, index=False)

    if not os.path.exists(ARQUIVO_VENDAS):
        pd.DataFrame(columns=COLUNAS_VENDAS).to_csv(ARQUIVO_VENDAS, index=False)

    if not os.path.exists(ARQUIVO_PEDIDOS):
        pd.DataFrame(columns=COLUNAS_PEDIDOS).to_csv(ARQUIVO_PEDIDOS, index=False)

    if not os.path.exists(ARQUIVO_CONFIG):
        config_inicial = {
            "chave_pix": "31993507169",
            "nome_recebedor": "CHUP CHUP MANIA",
            "cidade_recebedor": "BELO HORIZONTE"
        }
        with open(ARQUIVO_CONFIG, "w") as f:
            json.dump(config_inicial, f)

def carregar_dados():
    estoque = pd.read_csv(ARQUIVO_ESTOQUE)
    vendas = pd.read_csv(ARQUIVO_VENDAS)
    pedidos = pd.read_csv(ARQUIVO_PEDIDOS)
    with open(ARQUIVO_CONFIG, "r") as f:
        config = json.load(f)
    return estoque, vendas, pedidos, config

def salvar_estoque(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

def salvar_vendas(df):
    df.to_csv(ARQUIVO_VENDAS, index=False)

def salvar_pedidos(df):
    df.to_csv(ARQUIVO_PEDIDOS, index=False)

def salvar_config(config):
    with open(ARQUIVO_CONFIG, "w") as f:
        json.dump(config, f)

# --- GERADOR DE PIX E QR CODE ---

def calcular_crc16(payload):
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            if (crc & 0x8000) != 0:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"

def gerar_payload_pix(chave, nome, cidade, valor, txid="***"):
    nome = nome[:25].upper()
    cidade = cidade[:15].upper()
    valor_str = f"{valor:.2f}"
    
    gui = "0014br.gov.bcb.pix"
    key = f"01{len(chave):02d}{chave}"
    merchant_account = f"26{len(gui + key):02d}{gui}{key}"
    
    cat = "52040000"
    currency = "5303986"
    amount = f"54{len(valor_str):02d}{valor_str}"
    country = "5802BR"
    merchant_name = f"59{len(nome):02d}{nome}"
    merchant_city = f"60{len(cidade):02d}{cidade}"
    
    txid_str = f"05{len(txid):02d}{txid}"
    additional_data = f"62{len(txid_str):02d}{txid_str}"
    
    payload_sem_crc = (
        f"000201{merchant_account}{cat}{currency}{amount}{country}"
        f"{merchant_name}{merchant_city}{additional_data}6304"
    )
    
    crc = calcular_crc16(payload_sem_crc)
    return payload_sem_crc + crc

def obter_url_qr_code(texto):
    texto_encoded = urllib.parse.quote(texto)
    return f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={texto_encoded}"

# --- CARREGAMENTO INICIAL ---
inicializar_arquivos()
estoque_df, vendas_df, pedidos_df, config_pix = carregar_dados()

try:
    eh_cliente = st.query_params.get("modo") == "cliente"
except Exception:
    eh_cliente = False

# ==========================================
# 📱 INTERFACE DO CLIENTE
# ==========================================
if eh_cliente:
    if os.path.exists(NOME_BANNER):
        st.image(NOME_BANNER, use_container_width=True)

    st.header("🍦 Faça seu Pedido Online")
    st.write("Escolha seus sabores preferidos e garanta o seu geladinho!")

    estoque_disponivel = estoque_df[estoque_df["Estoque"] > 0]

    if estoque_disponivel.empty:
        st.warning("Desculpe, todos os nossos chup chups estão esgotados no momento! 😢")
    else:
        with st.form("form_pedido"):
            cliente_nome = st.text_input("Seu Nome:")
            
            sabor_selecionado = st.selectbox("Escolha o Sabor:", estoque_disponivel["Sabor"].unique())
            
            detalhes_item = estoque_disponivel[estoque_disponivel["Sabor"] == sabor_selecionado].iloc[0]
            preco_unitario = float(detalhes_item["Preco"])
            max_qtd = int(detalhes_item["Estoque"])
            
            st.info(f"Categoria: **{detalhes_item['Categoria']}** | Preço Unitário: **R$ {preco_unitario:.2f}**")

            quantidade = st.number_input("Quantidade:", min_value=1, max_value=max_qtd, value=1)
            forma_pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Dinheiro", "Cartão de Crédito/Débito"])

            valor_total = preco_unitario * quantidade
            st.markdown(f"### **Total: R$ {valor_total:.2f}**")

            btn_confirmar = st.form_submit_button("🛒 Confirmar Pedido")

        if btn_confirmar:
            if not cliente_nome.strip():
                st.error("Por favor, informe seu nome para identificarmos o pedido.")
            else:
                novo_id = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                novo_pedido = {
                    "ID": novo_id,
                    "Data_Hora": data_hora,
                    "Cliente": cliente_nome,
                    "Sabor": sabor_selecionado,
                    "Quantidade": quantidade,
                    "Valor_Total": valor_total,
                    "Forma_Pagamento": forma_pagamento,
                    "Status": "Pendente"
                }

                pedidos_df = pd.concat([pedidos_df, pd.DataFrame([novo_pedido])], ignore_index=True)
                salvar_pedidos(pedidos_df)

                st.success("✅ Pedido enviado com sucesso!")

                if forma_pagamento == "Pix":
                    st.subheader("📲 Pagamento via Pix")
                    st.write("Escaneie o QR Code abaixo com o aplicativo do seu banco para realizar o pagamento:")
                    
                    payload = gerar_payload_pix(
                        chave=config_pix["chave_pix"],
                        nome=config_pix["nome_recebedor"],
                        cidade=config_pix["cidade_recebedor"],
                        valor=valor_total,
                        txid=novo_id[-10:]
                    )
                    
                    url_qr = obter_url_qr_code(payload)
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(url_qr, width=220)
                    with col2:
                        st.write(f"**Chave Pix:** {config_pix['chave_pix']}")
                        st.write(f"**Valor:** R$ {valor_total:.2f}")
                        st.text_area("Copia e Cola Pix:", payload, height=100)

# ==========================================
# 🍦 GESTÃO CHUP CHUP MANIA (MODO ADM)
# ==========================================
else:
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        if os.path.exists(NOME_BANNER):
            st.image(NOME_BANNER, width=110)
    with col_titulo:
        st.title("🍦 Gestão Chup Chup Mania")
        st.write("Sistema Integrado de Vendas, Pedidos e Controle de Estoque")

    st.divider()

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_login, _ = st.columns([2, 1])
        with col_login:
            with st.form("form_login"):
                st.subheader("Acesso Restrito")
                senha_input = st.text_input("Senha de Acesso:", type="password")
                btn_entrar = st.form_submit_button("Acessar Painel")

                if btn_entrar:
                    if senha_input == SENHA_ADMIN:
                        st.session_state["autenticado"] = True
                        st.success("Acesso autorizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Senha de acesso incorreta.")
    else:
        st.sidebar.title("⚙️ Painel de Gestão")
        
        if os.path.exists(NOME_BANNER):
            st.sidebar.image(NOME_BANNER, use_container_width=True)

        if st.sidebar.button("🚪 Sair do Sistema"):
            st.session_state["autenticado"] = False
            st.rerun()

        opcao_menu = st.sidebar.radio(
            "Navegação",
            ["📋 Fila de Pedidos", "📦 Controle de Estoque", "📊 Relatório de Vendas", "⚙️ Configurações & QR Code"]
        )

        # 1. FILA DE PEDIDOS
        if opcao_menu == "📋 Fila de Pedidos":
            st.header("📋 Fila de Pedidos Recebidos")
            
            pedidos_pendentes = pedidos_df[pedidos_df["Status"] == "Pendente"]

            if pedidos_pendentes.empty:
                st.info("Nenhum pedido pendente na fila no momento.")
            else:
                for idx, row in pedidos_pendentes.iterrows():
                    with st.expander(f"Pedido #{row['ID']} — {row['Cliente']} (R$ {row['Valor_Total']:.2f})"):
                        st.write(f"**Data/Hora:** {row['Data_Hora']}")
                        st.write(f"**Sabor:** {row['Sabor']} x {row['Quantidade']}")
                        st.write(f"**Forma de Pagamento:** {row['Forma_Pagamento']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ Concluir Pedido", key=f"entregar_{row['ID']}"):
                                idx_est = estoque_df[estoque_df["Sabor"] == row["Sabor"]].index
                                if not idx_est.empty:
                                    estoque_df.loc[idx_est, "Estoque"] -= row["Quantidade"]
                                    salvar_estoque(estoque_df)

                                nova_venda = {
                                    "ID": row["ID"],
                                    "Data_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "Cliente": row["Cliente"],
                                    "Sabor": row["Sabor"],
                                    "Quantidade": row["Quantidade"],
                                    "Valor_Total": row["Valor_Total"],
                                    "Forma_Pagamento": row["Forma_Pagamento"]
                                }
                                vendas_df = pd.concat([vendas_df, pd.DataFrame([nova_venda])], ignore_index=True)
                                salvar_vendas(vendas_df)

                                pedidos_df.loc[pedidos_df["ID"] == row["ID"], "Status"] = "Concluído"
                                salvar_pedidos(pedidos_df)

                                st.success("Pedido concluído e faturamento atualizado!")
                                st.rerun()

                        with col2:
                            if st.button(f"❌ Cancelar", key=f"cancelar_{row['ID']}"):
                                pedidos_df.loc[pedidos_df["ID"] == row["ID"], "Status"] = "Cancelado"
                                salvar_pedidos(pedidos_df)
                                st.warning("Pedido cancelado com sucesso.")
                                st.rerun()

        # 2. CONTROLE DE ESTOQUE
        elif opcao_menu == "📦 Controle de Estoque":
            st.header("📦 Estoque Atual")
            st.dataframe(estoque_df, use_container_width=True)

            st.subheader("➕ Atualizar ou Cadastrar Sabor")
            with st.form("form_estoque"):
                sabor = st.text_input("Sabor do Geladinho:")
                categoria = st.selectbox("Categoria:", ["Gourmet", "Tradicional", "Fruta", "Ao Leite", "Alcoólico"])
                qtd = st.number_input("Quantidade em Estoque:", min_value=0, value=15)
                preco = st.number_input("Preço Unitário (R$):", min_value=0.0, value=5.00, step=0.50)

                btn_salvar = st.form_submit_button("Atualizar Estoque")

                if btn_salvar:
                    if not sabor.strip():
                        st.error("Informe o nome do sabor.")
                    else:
                        if sabor in estoque_df["Sabor"].values:
                            estoque_df.loc[estoque_df["Sabor"] == sabor, ["Categoria", "Estoque", "Preco"]] = [categoria, qtd, preco]
                        else:
                            novo_item = {"Sabor": sabor, "Categoria": categoria, "Estoque": qtd, "Preco": preco}
                            estoque_df = pd.concat([estoque_df, pd.DataFrame([novo_item])], ignore_index=True)

                        salvar_estoque(estoque_df)
                        st.success(f"Estoque de **{sabor}** atualizado!")
                        st.rerun()

        # 3. RELATÓRIO DE VENDAS (COM BOTÃO DE DEVOLUÇÃO AO ESTOQUE)
        elif opcao_menu == "📊 Relatório de Vendas":
            st.header("📊 Faturamento e Desempenho")

            if vendas_df.empty:
                st.info("Nenhuma venda registrada até o momento.")
            else:
                faturamento_total = vendas_df["Valor_Total"].sum()
                total_itens = vendas_df["Quantidade"].sum()

                col1, col2 = st.columns(2)
                col1.metric("💰 Faturamento Acumulado", f"R$ {faturamento_total:.2f}")
                col2.metric("🍦 Total de Unidades Vendidas", f"{total_itens} un")

                st.subheader("Cancelar Venda e Retornar ao Estoque")
                venda_selecionada_id = st.selectbox(
                    "Selecione o ID da Venda para Cancelar:", 
                    vendas_df["ID"].unique()
                )

                if st.button("🔄 Cancelar Venda Selecionada e Estornar Estoque"):
                    venda_info = vendas_df[vendas_df["ID"] == venda_selecionada_id].iloc[0]
                    sabor_venda = venda_info["Sabor"]
                    qtd_venda = int(venda_info["Quantidade"])

                    # Devolve a quantidade para o estoque
                    idx_est = estoque_df[estoque_df["Sabor"] == sabor_venda].index
                    if not idx_est.empty:
                        estoque_df.loc[idx_est, "Estoque"] += qtd_venda
                        salvar_estoque(estoque_df)

                    # Remove da tabela de vendas
                    vendas_df = vendas_df[vendas_df["ID"] != venda_selecionada_id]
                    salvar_vendas(vendas_df)

                    st.success(f"Venda {venda_selecionada_id} cancelada! {qtd_venda} unidade(s) de '{sabor_venda}' retornaram ao estoque.")
                    st.rerun()

                st.divider()
                st.subheader("Histórico Detalhado")
                st.dataframe(vendas_df.sort_values(by="Data_Hora", ascending=False), use_container_width=True)

        # 4. CONFIGURAÇÕES & QR CODE (COM LOGO BANCO CENTRAL PIX)
        elif opcao_menu == "⚙️ Configurações & QR Code":
            st.header("⚙️ Configurações Gerais")

            col_pix_logo, col_pix_tit = st.columns([1, 4])
            with col_pix_logo:
                st.image(URL_PIX_BACEN, width=120)
            with col_pix_tit:
                st.subheader("Cadastro da Chave Pix (Banco Central)")

            with st.form("form_config_pix"):
                chave = st.text_input("Chave Pix:", value=config_pix["chave_pix"])
                nome = st.text_input("Nome do Titular:", value=config_pix["nome_recebedor"])
                cidade = st.text_input("Cidade:", value=config_pix["cidade_recebedor"])

                btn_salvar_pix = st.form_submit_button("Salvar Dados Pix")

                if btn_salvar_pix:
                    config_pix["chave_pix"] = chave
                    config_pix["nome_recebedor"] = nome
                    config_pix["cidade_recebedor"] = cidade
                    salvar_config(config_pix)
                    st.success("Configurações do Pix atualizadas com sucesso!")

            st.divider()

            url_atual = st.context.headers.get("host", "chupchup-mania.streamlit.app")
            link_cliente = f"https://{url_atual}/?modo=cliente"

            st.subheader("📲 Link e QR Code do Cardápio Digital")
            st.write("Link exclusivo para envio aos clientes:")
            st.code(link_cliente)

            st.write("QR Code gerado para o cardápio dos clientes:")
            url_qr_cliente = obter_url_qr_code(link_cliente)
            st.image(url_qr_cliente, caption="Cardápio Digital Chup Chup Mania", width=220)
