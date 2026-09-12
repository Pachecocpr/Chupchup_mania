
import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
from datetime import datetime
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Chup Chup Mania - Vendas & Pedidos", 
    page_icon="🍦", 
    layout="wide"
)

# --- ARQUIVOS DE DADOS ---
ARQUIVO_ESTOQUE = "estoque_chupchup.csv"
ARQUIVO_VENDAS = "historico_vendas.csv"
ARQUIVO_PEDIDOS = "pedidos_pendentes.csv"
ARQUIVO_CONFIG = "config_pix.json"
NOME_BANNER = "banner.jpg"  # Nome do arquivo da imagem do cartaz no mesmo diretório

COLUNAS_ESTOQUE = ["Sabor", "Categoria", "Estoque", "Preco"]
COLUNAS_VENDAS = ["ID", "Data_Hora", "Cliente", "Sabor", "Quantidade", "Valor_Total", "Forma_Pagamento"]
COLUNAS_PEDIDOS = ["ID", "Data_Hora", "Cliente", "Sabor", "Quantidade", "Valor_Total", "Forma_Pagamento", "Status"]

# --- FUNÇÕES DE CARREGAMENTO E SALVAMENTO ---

def inicializar_arquivos():
    if not os.path.exists(ARQUIVO_ESTOQUE):
        # Sabores extraídos diretamente da imagem do cartaz
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
            "chave_pix": "31993507169",  # Número de telefone que está no cartaz
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

# --- GERADOR DE PIX EMV (COPIA E COLA / BR CODE) ---

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

def gerar_imagem_qr(texto):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    return buf.getvalue()

# --- INICIALIZAÇÃO DE DADOS ---
inicializar_arquivos()
estoque_df, vendas_df, pedidos_df, config_pix = carregar_dados()

# --- BARRA LATERAL (NAVEGAÇÃO) ---
st.sidebar.title("🍦 Chup Chup Mania")

# Exibe o banner reduzido na barra lateral
if os.path.exists(NOME_BANNER):
    st.sidebar.image(NOME_BANNER, use_container_width=True)

opcao_menu = st.sidebar.radio(
    "Navegação",
    ["📱 Fazer Pedido (Cliente)", "📋 Pedidos Pendentes", "📦 Estoque", "📊 Histórico de Vendas", "⚙️ Configuração Pix / QRCodes"]
)

# ==========================================
# 1. FAZER PEDIDO (INTERFACE DO CLIENTE)
# ==========================================
if opcao_menu == "📱 Fazer Pedido (Cliente)":
    # Exibe o banner da loja em destaque no topo da página
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
            preco_unitario = detalhes_item["Preco"]
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
                    
                    qr_img = gerar_imagem_qr(payload)
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(qr_img, width=220)
                    with col2:
                        st.write(f"**Chave Pix:** {config_pix['chave_pix']}")
                        st.write(f"**Valor:** R$ {valor_total:.2f}")
                        st.text_area("Copia e Cola Pix:", payload, height=100)

# ==========================================
# 2. PEDIDOS PENDENTES (PAINEL DO VENDEDOR)
# ==========================================
elif opcao_menu == "📋 Pedidos Pendentes":
    st.header("📋 Fila de Pedidos Recebidos")
    
    pedidos_pendentes = pedidos_df[pedidos_df["Status"] == "Pendente"]

    if pedidos_pendentes.empty:
        st.info("Nenhum pedido pendente no momento.")
    else:
        for idx, row in pedidos_pendentes.iterrows():
            with st.expander(f"Pedido #{row['ID']} - {row['Cliente']} (R$ {row['Valor_Total']:.2f})"):
                st.write(f"**Data/Hora:** {row['Data_Hora']}")
                st.write(f"**Sabor:** {row['Sabor']} x {row['Quantidade']}")
                st.write(f"**Pagamento:** {row['Forma_Pagamento']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Entregar Pedido", key=f"entregar_{row['ID']}"):
                        # Baixa no estoque
                        idx_est = estoque_df[estoque_df["Sabor"] == row["Sabor"]].index
                        if not idx_est.empty:
                            estoque_df.loc[idx_est, "Estoque"] -= row["Quantidade"]
                            salvar_estoque(estoque_df)

                        # Adiciona ao histórico de vendas
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

                        # Atualiza status
                        pedidos_df.loc[pedidos_df["ID"] == row["ID"], "Status"] = "Concluído"
                        salvar_pedidos(pedidos_df)

                        st.success("Pedido concluído e estoque baixado!")
                        st.rerun()

                with col2:
                    if st.button(f"❌ Cancelar Pedido", key=f"cancelar_{row['ID']}"):
                        pedidos_df.loc[pedidos_df["ID"] == row["ID"], "Status"] = "Cancelado"
                        salvar_pedidos(pedidos_df)
                        st.warning("Pedido cancelado.")
                        st.rerun()

# ==========================================
# 3. GESTÃO DE ESTOQUE
# ==========================================
elif opcao_menu == "📦 Estoque":
    st.header("📦 Gerenciamento de Estoque")

    st.dataframe(estoque_df, use_container_width=True)

    st.subheader("➕ Adicionar ou Editar Sabor")
    with st.form("form_estoque"):
        sabor = st.text_input("Sabor do Chup Chup:")
        categoria = st.selectbox("Categoria:", ["Gourmet", "Tradicional", "Fruta", "Ao Leite", "Alcoólico"])
        qtd = st.number_input("Quantidade em Estoque:", min_value=0, value=15)
        preco = st.number_input("Preço de Venda (R$):", min_value=0.0, value=5.00, step=0.50)

        btn_salvar = st.form_submit_button("Salvar")

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
                st.success(f"Sabor **{sabor}** atualizado no estoque!")
                st.rerun()

# ==========================================
# 4. HISTÓRICO DE VENDAS
# ==========================================
elif opcao_menu == "📊 Histórico de Vendas":
    st.header("📊 Vendas e Faturamento")

    if vendas_df.empty:
        st.info("Nenhuma venda registrada ainda.")
    else:
        faturamento_total = vendas_df["Valor_Total"].sum()
        total_itens = vendas_df["Quantidade"].sum()

        col1, col2 = st.columns(2)
        col1.metric("💰 Faturamento Total", f"R$ {faturamento_total:.2f}")
        col2.metric("🍦 Chup Chups Vendidos", f"{total_itens} un")

        st.subheader("Detalhamento")
        st.dataframe(vendas_df.sort_values(by="Data_Hora", ascending=False), use_container_width=True)

# ==========================================
# 5. CONFIGURAÇÃO PIX E QR CODES
# ==========================================
elif opcao_menu == "⚙️ Configuração Pix / QRCodes":
    st.header("⚙️ Configurações de Pagamento e Cardápio")

    st.subheader("🔑 Configuração da Chave Pix")
    with st.form("form_config_pix"):
        chave = st.text_input("Chave Pix (Telefone, CPF, E-mail ou Aleatória):", value=config_pix["chave_pix"])
        nome = st.text_input("Nome do Titular/Estabelecimento:", value=config_pix["nome_recebedor"])
        cidade = st.text_input("Cidade do Titular:", value=config_pix["cidade_recebedor"])

        btn_salvar_pix = st.form_submit_button("Salvar Configurações Pix")

        if btn_salvar_pix:
            config_pix["chave_pix"] = chave
            config_pix["nome_recebedor"] = nome
            config_pix["cidade_recebedor"] = cidade
            salvar_config(config_pix)
            st.success("Dados do Pix salvos com sucesso!")

    st.divider()

    st.subheader("📲 Gerador de QR Code do Cardápio")
    st.write("Gere um QR Code com a URL do seu aplicativo para imprimir e colar no seu carrinho/mesa.")

    url_app = st.text_input("URL do App Publicado (ex: https://chupchupmania.streamlit.app):", "http://localhost:8501")
    
    if url_app:
        qr_cardapio = gerar_imagem_qr(url_app)
        col_qr1, col_qr2 = st.columns([1, 2])
        with col_qr1:
            st.image(qr_cardapio, caption="QR Code para acesso do cliente", width=200)
        with col_qr2:
            st.download_button(
                label="📥 Baixar QR Code do Cardápio",
                data=qr_cardapio,
                file_name="qr_code_cardapio_chupchup.png",
                mime="image/png"
            )
