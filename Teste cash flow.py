import streamlit as st
import pandas as pd
import numpy as np
import os  # Adicionado apenas para verificar a existência do arquivo

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

    # Processar Saídas
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

    # Processar Recebidos
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
        # Tenta carregar a logo, se falhar (arquivo não encontrado), não trava o código
        if os.path.exists("logo-white.jpg"):
            st.image("logo-white.jpg", use_container_width=True)
        else:
            st.warning("⚠️ Logo 'logo-white.jpg' não encontrada na pasta.")
        
        st.markdown("<h2 style='color: #00D1FF;'>💎 MALDÍVAS GROUP</h2>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.write("---")
        
        default_mes = [lista_meses[-1]] if lista_meses else []
        meses_sel = st.multiselect("📅 Períodos:", options=lista_meses, default=default_mes)
        grupos_sel = st.multiselect("📂 Grupos:", options=list(MAPA_GRUPOS.keys()), default=list(MAPA_GRUPOS.keys()))
        
        cats_dinamicas = [cat for g in grupos_sel for cat in MAPA_GRUPOS[g]]
        cats_sel = st.multiselect("🏷️ Categorias:", options=sorted(list(set(cats_dinamicas))), default=sorted(list(set(cats_dinamicas))))

        # --- SEÇÃO DE EXPORTAÇÃO TXT (RELATÓRIO CFO) ---
        st.write("---")
        if meses_sel:
            # Cálculos para o Relatório
            df_m = df_raw[df_raw['Mes_Ano'].isin(meses_sel)]
            df_r_m = df_rec_raw[df_rec_raw['Mes_Ano'].isin(meses_sel)]
            t_in = df_r_m[col_v].sum()
            t_out = abs(df_m[df_m[col_v] < 0][col_v].sum())
            saldo = t_in - t_out
            margem = (saldo / t_in * 100) if t_in > 0 else 0
            top_cat = df_m[df_m[col_v] < 0].groupby('Categoria')[col_v].sum().abs().sort_values(ascending=False).head(5)

            report_txt = f"""
============================================================
           __  __          _      _ _             
          |  \/  |  _ _   | |  __| (_) __ __  __ _ 
          | |\/| | / _` | | | / _` | | \ V / / _` |
          |_|  |_| \__,_| |_| \__,_|_|  \_/  \__,_|
                    GROUP FINANCIAL REPORT
============================================================
RELATÓRIO EXECUTIVO DE FLUXO DE CAIXA
Período: {', '.join(meses_sel)}
Data de Geração: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
============================================================

1. RESUMO FINANCEIRO (CFO VIEW)
------------------------------------------------------------
(+) TOTAL CASH IN (Entradas):     {format_brl(t_in)}
(-) TOTAL CASH OUT (Saídas):      {format_brl(t_out)}
------------------------------------------------------------
(=) SALDO LÍQUIDO DO PERÍODO:     {format_brl(saldo)}
(%) MARGEM DE CAIXA OPERACIONAL:  {margem:.2f}%

STATUS ATUAL: {"✅ OPERAÇÃO SAUDÁVEL" if saldo > 0 else "🚨 ALERTA: CASH BURN"}

2. PERFORMANCE POR GRUPO ESTRATÉGICO
------------------------------------------------------------
"""
            for g in grupos_sel:
                v_g = abs(df_m[(df_m['Grupo_Filtro'] == g) & (df_m[col_v] < 0)][col_v].sum())
                p_g = (v_g / t_out * 100) if t_out > 0 else 0
                report_txt += f"- {g:<20}: {format_brl(v_g)} ({p_g:.1f}%)\n"

            report_txt += f"""
3. PARETO: TOP 5 GARGALOS (Onde está o dinheiro?)
------------------------------------------------------------
"""
            for cat, val in top_cat.items():
                report_txt += f"- {cat:<25}: {format_brl(val)}\n"

            report_txt += f"""
4. INSIGHTS PARA OS SÓCIOS
------------------------------------------------------------
* O grupo {top_cat.index[0] if not top_cat.empty else "N/A"} representa o maior peso financeiro.
* Margem de {margem:.2f}%: {"Operação gerando caixa para reinvestimento." if saldo > 0 else "Necessidade de revisão urgente de custos fixos."}
* Recomendação: Analisar contratos recorrentes das categorias Top 1 e 2.

Gerado automaticamente via Maldívas Intel Intelligence.
============================================================
"""
            st.download_button(
                label="📥 Baixar Relatório para Sócios (TXT)",
                data=report_txt,
                file_name=f"Relatorio_CFO_{'_'.join(meses_sel)}.txt",
                mime="text/plain",
                use_container_width=True
            )

    # Filtros Saídas
    df = df_raw.copy()
    if meses_sel: df = df[df['Mes_Ano'].isin(meses_sel)]
    if grupos_sel: df = df[df['Grupo_Filtro'].isin(grupos_sel)]
    if cats_sel: df = df[df['Categoria'].isin(cats_sel)]

    # Filtros Recebidos
    df_rec = df_rec_raw.copy()
    if meses_sel: df_rec = df_rec[df_rec['Mes_Ano'].isin(meses_sel)]

    # --- HEADER PRINCIPAL ---
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
    
    st.write("") 

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

    with tab1:
        st.markdown("### 🏛️ Visão Executiva e Estrutura de Dados")
        st.markdown("---")
        pres_col1, pres_col2 = st.columns(2)
        with pres_col1:
            st.markdown(f"""
            #### 🎯 Objetivo da Ferramenta
            Este ecossistema foi projetado para converter dados brutos de faturamento e despesas em **Inteligência Financeira**.
            
            **Como os dados fluem:**
            1. **Ingestão:** Conexão direta com as planilhas de Saídas e Recebidos.
            2. **Processamento:** Limpeza de caracteres e conversão monetária automática.
            3. **Categorização:** Mapeamento inteligente de categorias em 4 grandes grupos.
            """)
        with pres_col2:
            st.markdown("#### 🛠️ Pilares de Análise")
            st.info("**Fluxo de Caixa:** Foco total no saldo bancário real.")
            st.warning("**Eficiência de Custos:** Identificação de gargalos (Pareto 80/20).")
            st.success("**Saúde Líquida:** Visibilidade imediata de lucro ou prejuízo.")

    with tab2:
        st.subheader("Queima de Caixa Diária (Acumulada)")
        if not saidas_df.empty:
            burn = saidas_df.groupby('Data de pagamento')[col_v].sum().abs().reset_index().sort_values('Data de pagamento')
            burn['Acumulado'] = burn[col_v].cumsum()
            st.line_chart(burn.set_index('Data de pagamento')['Acumulado'], color="#FF4B4B")
            st.write("#### Detalhamento de Saída Diária")
            diario = saidas_df.groupby('Data de pagamento')[col_v].sum().abs().reset_index()
            diario.columns = ['Data', 'Valor do Dia']
            st.dataframe(diario.style.format({'Valor do Dia': "R$ {:,.2f}"}), use_container_width=True, hide_index=True)
        else:
            st.info("Sem saídas registradas.")

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Maiores Gastos por Grupo")
            g_pareto = saidas_df.groupby('Grupo_Filtro')[col_v].sum().abs().sort_values(ascending=False).reset_index()
            st.dataframe(g_pareto.style.format({col_v: "R$ {:,.2f}"}), use_container_width=True, hide_index=True)
            st.bar_chart(g_pareto.set_index('Grupo_Filtro')[col_v], color="#00D1FF")
        with c2:
            st.subheader("Top 10 Categorias")
            c_pareto = saidas_df.groupby('Categoria')[col_v].sum().abs().sort_values(ascending=False).head(10).reset_index()
            st.dataframe(c_pareto.style.format({col_v: "R$ {:,.2f}"}), use_container_width=True, hide_index=True)
            st.bar_chart(c_pareto.set_index('Categoria')[col_v], color="#00D1FF")

    with tab4:
        st.subheader("Explorador de Lançamentos")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab5:
        st.subheader("Explorador de Recebidos")
        st.dataframe(df_rec, use_container_width=True, hide_index=True)

    with tab6:
        st.subheader(f"Análise Financeira: {', '.join(meses_sel) if meses_sel else 'Nenhum'}")
        curr_s = abs(df[df[col_v] < 0][col_v].sum())
        curr_e = df_rec[col_v].sum()
        resultado = curr_e - curr_s
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Entrou no Período", format_brl(curr_e))
        col_res2.metric("Saiu no Período", format_brl(curr_s))
        color_res = "#FF4B4B" if resultado < 0 else "#00D1FF"
        st.markdown(f"**Saldo Líquido**")
        st.markdown(f"<h2 style='color: {color_res}; margin-top: -15px;'>{format_brl(resultado)}</h2>", unsafe_allow_html=True)

    with tab7:
        st.subheader("INDICADORES DE LUCRATIVIDADE")
        total_e = df_rec[col_v].sum()
        total_s = abs(df[df[col_v] < 0][col_v].sum())
        lucro_abs = total_e - total_s
        color_lucro = "#FF4B4B" if lucro_abs < 0 else "#00D1FF"
        st.markdown(f"**LUCRO LÍQUIDO (CAIXA)**")
        st.markdown(f"<h2 style='color: {color_lucro}; margin-top: -15px;'>{format_brl(lucro_abs)}</h2>", unsafe_allow_html=True)
        if total_e > 0:
            grupo_valores = df[df[col_v] < 0].groupby('Grupo_Filtro')[col_v].sum().abs().reset_index()
            st.bar_chart(grupo_valores.set_index('Grupo_Filtro'), color="#00D1FF")

    with tab8:
        st.header("📖 Guia Didático e Manual de Instruções")
        st.markdown("""
        Este painel foi desenvolvido para simplificar a gestão financeira da **Maldívas**. Abaixo, explicamos como interpretar cada seção:

        ### 1. Grupos Estratégicos (Como os dados são organizados)
        * **Administrativo:** Custos fixos e infraestrutura (Aluguel, TI, Software). É o "custo de existir".
        * **Pessoal:** Tudo relacionado ao time (Salários, Encargos, Benefícios). Monitoramos a eficiência do capital humano.
        * **Operacional:** Gastos diretos para a entrega do serviço. Crescimento aqui deve ser proporcional ao faturamento.
        * **Tributário:** Obrigações fiscais. Essencial para o compliance.

        ### 2. A Métrica de Cash Burn (Tab 🔥)
        O gráfico mostra o dinheiro saindo do caixa ao longo dos dias. 
        * **Ponto de Atenção:** Se a linha sobe muito rápido no início do mês, suas despesas fixas estão concentradas no começo do ciclo.

        ### 3. Análise de Pareto (Tab 🎯)
        Focamos na regra 80/20. O dashboard identifica automaticamente quais categorias consomem a maior parte do seu orçamento. 
        * **Dica:** Reduzir 5% da categoria principal gera mais impacto do que eliminar uma categoria pequena por completo.

        ### 4. Lucratividade (Tab 💎)
        Aqui calculamos a **Margem de Caixa**. 
        * **Saldo Positivo:** Capacidade de reinvestimento ou distribuição de lucros.
        * **Saldo Negativo:** Operação sendo financiada por reserva ou capital de terceiros.

        ### 5. Relatório para Sócios (Botão na Sidebar)
        O botão "Baixar Relatório" gera um resumo executivo formatado para o Bloco de Notas ou WhatsApp. Ele contém o Branding da Maldívas e os insights que um CFO prioriza (Margem, Pareto e Status de Operação).
        """)

except Exception as e:
    st.error(f"Erro ao carregar layout: {e}")
