import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. Configuração de Página e Layout Dark Luxo
st.set_page_config(page_title="CASH FLOW | AP", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    /* Global Style */
    .main { background-color: #0B0E14; }
    div[data-testid="stMetricValue"] { color: #00D1FF; font-weight: 700; font-size: 1.8rem !important; }
    div[data-testid="stMetricLabel"] { color: #94A3B8; font-weight: 400; }
    
    /* Containers das Métricas */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Estilização das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #1E293B;
        border-radius: 8px 8px 0 0;
        color: #94A3B8;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #00D1FF !important; 
        color: #0B0E14 !important; 
    }

    /* Sidebar Custom */
    .css-1d391kg { background-color: #111827; }
    </style>
    """, unsafe_allow_html=True)

def format_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

MAPA_GRUPOS = {
    "Administrativo": ["ALUGUEL", "COMPRA DE ATIVO FIXO", "CONDOMÍNIO", "COWORKING", "CUSTO OPERACIONAL", "DESPESAS FINANCEIRAS", "ENERGIA ELÉTRICA", "ESTORNO", "EVENTOS FUNCIONÁRIOS", "DESPESAS VIAGEM", "MANUTENÇÃO ESCRITÓRIO", "MATERIAIS DE TI", "MATERIAL DE COPA", "MATERIAL DE ESCRITÓRIO", "MATERIAL DE LIMPEZA", "Multas Pagas","LOCOMOÇÃO", "OUTRAS DESPESAS", "PAGAMENTO DE EMPRÉSTIMO", "REPRESENTAÇÃO", "SEGUROS", "SERVIÇOS CONTÁBEIS","REPRESENTAÇÃO", "SERVIÇOS CONTRATADOS", "SERVIÇOS DE E-MAIL", "SERVIÇOS DE ENTREGA", "SERVIÇOS DE PUBLICIDADE", "SERVIÇOS JURÍDICOS", "SERVIÇOS TI", "SISTEMAS", "TAXAS E CONTRIBUIÇÕES", "TELEFONIA/INTERNET", "TREINAMENTOS", "VAGAS GARAGEM - SÓCIOS","SERVIÇOS DE PUBLICIDADE"],
    "Despesa de pessoal": ["13º SALÁRIO", "ADIANTAMENTO AO FUNCIONÁRIO", "ANTECIPAÇÃO DE RESULTADOS", "ASSISTÊNCIA MÉDICA", "ASSISTÊNCIA ODONTO", "BÔNUS CLT", "BÔNUS PERFORMANCE - G", "CONSULTORIA ESPECIALIZADA - G", "CONSULTORIA ESPECIALIZADA - TI", "DESPESA EVENTUAL DE PESSOAL", "ESTAGIÁRIO FOLHA", "EXAMES OCUPACIONAIS", "FÉRIAS", "FGTS", "GRATIFICAÇÕES CLT", "GRATIFICAÇÕES PJ - G", "INSS", "IRRF", "PRO LABORE", "RESCISÃO", "SALÁRIOS CLT", "SEGURO DE VIDA", "SERVIÇOS CONTRATADOS", "VA/VR", "VT"],
    "Operacional": ["BÔNUS - TERCEIROS", "COMISSÕES SEGUROS", "CUSTO OPERACIONAL", "Descontos Recebidos", "EVENTOS CLIENTES", "Multas Pagas", "REBATE COMISSÕES", "REPRESENTAÇÃO"],
    "Tributário": ["COFINS", "COFINS Retido sobre Pagamentos", "CSLL", "CSLL Retido sobre Pagamentos", "DESPESAS FINANCEIRAS", "ESTORNO", "INSS Retido sobre Pagamentos", "Juros Pagos", "IPTU", "IRPJ", "IRPJ Retido sobre Pagamentos", "ISS", "ISS Retido sobre Pagamentos", "Juros Pagos", "Multas Pagas", "Pagamento de ISS Retido", "PARCELAMENTO RECEITA FEDERAL", "PERT CSLL", "PERT IRPJ", "PERT IRRF", "PERT SN", "Multas Pagas", "PIS", "PIS Retido sobre Pagamentos"]
}

@st.cache_data(ttl=600)
def load_and_process():
    url_saidas = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7KV7hi8lJHEleaPoPyAKWo7ChUTlLuorbLX9v4aZGXPKI6aeudpF06eUc60hmIPX8Pkz5BrZOhc1G/pub?gid=1959056339&single=true&output=csv"
    url_recebidos = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7KV7hi8lJHEleaPoPyAKWo7ChUTlLuorbLX9v4aZGXPKI6aeudpF06eUc60hmIPX8Pkz5BrZOhc1G/pub?gid=58078527&single=true&output=csv"
    
    def clean_val(v):
        if isinstance(v, str):
            v = v.replace('R$', '').replace('.', '').replace(' ', '').replace(',', '.')
            try: return float(v)
            except: return 0.0
        return v

    col_v = 'Valor categoria/centro de custo'

    df_s = pd.read_csv(url_saidas)
    df_s[col_v] = df_s[col_v].apply(clean_val)
    df_s['Data de pagamento'] = pd.to_datetime(df_s['Data de pagamento'], dayfirst=True, errors='coerce')
    df_s = df_s.dropna(subset=['Data de pagamento']).sort_values('Data de pagamento')
    df_s['Mes_Ano'] = df_s['Data de pagamento'].dt.strftime('%m/%Y')
    
    def atribuir_grupo(cat):
        for grupo, categorias in MAPA_GRUPOS.items():
            if cat in categorias: return grupo
        return "Outros"
    df_s['Grupo_Filtro'] = df_s['Categoria'].apply(atribuir_grupo)

    df_r = pd.read_csv(url_recebidos)
    df_r[col_v] = df_r[col_v].apply(clean_val)
    df_r['Data de pagamento'] = pd.to_datetime(df_r['Data de pagamento'], dayfirst=True, errors='coerce')
    df_r = df_r.dropna(subset=['Data de pagamento'])
    df_r['Mes_Ano'] = df_r['Data de pagamento'].dt.strftime('%m/%Y')

    return df_s, df_r

try:
    df_raw, df_rec_raw = load_and_process()
    col_v = 'Valor categoria/centro de custo'
    
    meses_s = df_raw['Mes_Ano'].unique()
    meses_r = df_rec_raw['Mes_Ano'].unique()
    lista_meses = sorted(list(set(meses_s) | set(meses_r)), key=lambda x: pd.to_datetime(x, format='%m/%Y'))

    with st.sidebar:
        # --- CARREGAMENTO DA LOGO ---
        if os.path.exists("logo-white.jpg"):
            st.image("logo-white.jpg", use_container_width=True)
        else:
            st.markdown("<h2 style='color: #00D1FF;'>💎 DASHBOARD</h2>", unsafe_allow_html=True)
            st.warning("Verifique se o arquivo 'logo-white.jpg' está na mesma pasta do script.")

        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.write("---")
        
        default_mes = [lista_meses[-1]] if lista_meses else []
        meses_sel = st.multiselect("📅 Períodos:", options=lista_meses, default=default_mes)
        grupos_sel = st.multiselect("📂 Grupos:", options=list(MAPA_GRUPOS.keys()), default=list(MAPA_GRUPOS.keys()))
        
        cats_dinamicas = [cat for g in grupos_sel for cat in MAPA_GRUPOS[g]]
        cats_sel = st.multiselect("🏷️ Categorias:", options=sorted(list(set(cats_dinamicas))), default=sorted(list(set(cats_dinamicas))))

        # --- EXPORTAÇÃO TXT ---
        st.write("---")
        if meses_sel:
            st.markdown("### 📄 Relatório p/ Sócios")
            df_m = df_raw[df_raw['Mes_Ano'].isin(meses_sel)]
            df_r_m = df_rec_raw[df_rec_raw['Mes_Ano'].isin(meses_sel)]
            t_in = df_r_m[col_v].sum()
            t_out = abs(df_m[df_m[col_v] < 0][col_v].sum())
            saldo = t_in - t_out
            margem = (saldo / t_in * 100) if t_in > 0 else 0
            top_cat = df_m[df_m[col_v] < 0].groupby('Categoria')[col_v].sum().abs().sort_values(ascending=False).head(5)

            report = f"""
============================================================
                    GROUP FINANCIAL REPORT
============================================================
PERÍODO ANALISADO: {', '.join(meses_sel)}
STATUS: {"✅ POSITIVO" if saldo > 0 else "🚨 ALERTA"}
============================================================

1. SUMÁRIO (CASH FLOW)
------------------------------------------------------------
(+) TOTAL CASH IN:    {format_brl(t_in)}
(-) TOTAL CASH OUT:   {format_brl(t_out)}
------------------------------------------------------------
(=) SALDO LÍQUIDO:    {format_brl(saldo)}
(%) MARGEM CAIXA:     {margem:.2f}%

2. TOP 5 GARGALOS
------------------------------------------------------------
"""
            for c, val in top_cat.items():
                report += f"- {c:<25}: {format_brl(val)}\n"

            st.download_button(
                label="📥 Baixar Relatório (TXT)",
                data=report,
                file_name=f"Relatorio_{'_'.join(meses_sel)}.txt",
                mime="text/plain",
                use_container_width=True
            )

    # Conteúdo Principal
    st.title("💸 Cash Flow | Expenses and Receipts")
    
    total_recebidos_header = df_rec[col_v].sum()
    c_in_1, c_in_2 = st.columns([1, 3])
    with c_in_1:
        st.markdown(f"""
            <div style='background: rgba(0, 209, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #00D1FF;'>
                <p style='color: #00D1FF; margin: 0; font-weight: bold;'>💰 TOTAL CASH IN (ENTRADAS)</p>
                <h2 style='color: #00D1FF; margin: 0;'>{format_brl(total_recebidos_header)}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    saidas_df = df[df[col_v] < 0]
    total_geral = saidas_df[col_v].sum()
    
    cols_m = st.columns(len(grupos_sel) + 1)
    with cols_m[0]:
        st.metric("CASH OUT TOTAL", format_brl(abs(total_geral)))
    for i, grupo in enumerate(grupos_sel):
        val_g = df[(df['Grupo_Filtro'] == grupo) & (df[col_v] < 0)][col_v].sum()
        with cols_m[i+1]:
            st.metric(grupo.upper(), format_brl(abs(val_g)))

    st.write("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 APRESENTAÇÃO", "🔥 CASH BURN", "🎯 PARETO", "📋 DADOS", 
        "💰 RECEBIDOS", "📈 ANÁLISE MENSAL", "💎 LUCRATIVIDADE", "📖 GUIA DO DASHBOARD"
    ])

    with tab1: st.markdown("### 🏛️ Visão Executiva")
    with tab2:
        if not saidas_df.empty:
            burn = saidas_df.groupby('Data de pagamento')[col_v].sum().abs().cumsum().reset_index()
            st.line_chart(burn.set_index('Data de pagamento'))
    with tab3:
        g_pareto = saidas_df.groupby('Grupo_Filtro')[col_v].sum().abs().sort_values(ascending=False).reset_index()
        st.bar_chart(g_pareto.set_index('Grupo_Filtro')[col_v])
    with tab4: st.dataframe(df, use_container_width=True)
    with tab5: st.dataframe(df_rec, use_container_width=True)
    with tab6:
        curr_s = abs(df[df[col_v] < 0][col_v].sum())
        curr_e = df_rec[col_v].sum()
        st.metric("Saldo Líquido", format_brl(curr_e - curr_s))
    with tab7: st.subheader("Indicadores de Lucratividade")
    with tab8: st.header("📖 Guia Didático")

except Exception as e:
    st.error(f"Erro ao carregar layout: {e}")
