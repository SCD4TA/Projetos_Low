import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import numpy as np
import unicodedata
import io
import google.generativeai as genai
from mkpro_auth import (
    verificar_acesso, is_admin,
    salvar_dados, carregar_dados_salvos,
    listar_usuarios, adicionar_usuario,
    atualizar_expiracao, desativar_usuario, redefinir_senha,
    salvar_metas, carregar_metas, trocar_senha,
)

st.set_page_config(
    page_title="MK Pro · Finance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS — Design QClay/MK Pro
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Fraunces:ital,wght@0,300;1,300;1,500&display=swap');

:root {
    --bg:       #ebebea;
    --card:     #ffffff;
    --ink:      #1a1714;
    --muted:    #8a7a60;
    --border:   #e2ddd8;
    --amber:    #c9a96e;
    --sage:     #7a9e76;
    --terra:    #c9856e;
    --slate:    #8a9bb5;
    --shadow:   rgba(26,23,20,0.07);
    --shadow2:  rgba(26,23,20,0.12);
}

html,body,[class*="css"]{
    font-family:'Outfit',sans-serif!important;
    background:var(--bg)!important;
    color:var(--ink)!important;
}
.stApp{background:var(--bg)!important;}

section[data-testid="stSidebar"]{display:none!important;}
[data-testid="collapsedControl"]{display:none!important;}
.block-container{padding:14px 20px!important;max-width:100%!important;}
header[data-testid="stHeader"]{display:none!important;}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{
    background:#fff!important;border-radius:12px!important;
    border:1px solid var(--border)!important;
    gap:0!important;padding:4px!important;margin-bottom:4px!important;
}
.stTabs [data-baseweb="tab"]{
    font-family:'Outfit',sans-serif!important;
    font-size:11px!important;font-weight:600!important;
    letter-spacing:1px!important;text-transform:uppercase!important;
    color:var(--muted)!important;padding:8px 16px!important;
    border-radius:8px!important;border:none!important;background:transparent!important;
    transition:all .15s!important;
}
.stTabs [aria-selected="true"]{color:#fff!important;background:var(--ink)!important;}
.stTabs [data-baseweb="tab-panel"]{padding-top:16px!important;}

/* ── Inputs ── */
.stSelectbox>div>div,.stTextInput>div>div>input{
    background:#fff!important;border:1px solid var(--border)!important;
    border-radius:10px!important;font-family:'Outfit',sans-serif!important;
    font-size:12px!important;color:var(--ink)!important;
    box-shadow:0 1px 4px var(--shadow)!important;
}
.stFileUploader{
    background:#fff!important;border:1.5px dashed var(--border)!important;
    border-radius:12px!important;box-shadow:0 1px 4px var(--shadow)!important;
}

/* ── Botão ── */
.stButton>button{
    background:var(--ink)!important;color:#fff!important;border:none!important;
    border-radius:100px!important;font-family:'Outfit',sans-serif!important;
    font-size:11px!important;font-weight:600!important;padding:8px 20px!important;
    transition:all .15s!important;letter-spacing:.5px!important;
}
.stButton>button:hover{
    background:#3a3028!important;transform:translateY(-1px)!important;
    box-shadow:0 4px 16px rgba(26,23,20,0.18)!important;
}
.stButton>button *,.stButton>button span{color:#fff!important;}

/* ── Download button ── */
.stDownloadButton>button{
    background:#f5f2ee!important;color:var(--ink)!important;border:1px solid var(--border)!important;
    border-radius:100px!important;font-family:'Outfit',sans-serif!important;
    font-size:11px!important;font-weight:600!important;padding:7px 16px!important;
    transition:all .15s!important;
}
.stDownloadButton>button:hover{background:#ebe7e0!important;transform:translateY(-1px)!important;}
.stDownloadButton>button *,.stDownloadButton>button span{color:var(--ink)!important;}

/* ── Toggles/radios ── */
.stToggle label,.stRadio label{font-family:'Outfit',sans-serif!important;font-size:12px!important;}
.stRadio>div{gap:8px!important;}

/* ── Multiselect ── */
.stMultiSelect>div>div{
    background:#fff!important;border:1px solid var(--border)!important;
    border-radius:10px!important;box-shadow:0 1px 4px var(--shadow)!important;
}

/* ── Number input ── */
.stNumberInput>div>div>input{
    background:#fff!important;border:1px solid var(--border)!important;
    border-radius:10px!important;font-family:'Outfit',sans-serif!important;
    font-size:12px!important;color:var(--ink)!important;
}

/* ── Dataframe ── */
.stDataFrame{border-radius:14px!important;overflow:hidden!important;
    border:1px solid var(--border)!important;
    box-shadow:0 2px 12px var(--shadow)!important;}

/* ── Info/Alert ── */
.stAlert{border-radius:12px!important;border:none!important;
    font-family:'Outfit',sans-serif!important;
    box-shadow:0 2px 8px var(--shadow)!important;}

/* ── Chat messages ── */
.stChatMessage{background:#fff!important;border:1px solid var(--border)!important;
    border-radius:14px!important;font-family:'Outfit',sans-serif!important;}

.stCaption{color:var(--muted)!important;font-size:11px!important;}
hr{border-color:var(--border)!important;}

/* ── Cards QClay (com profundidade 3D) ── */
.qc-card{
    background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);
    border-radius:18px;border:1px solid #e2ddd8;
    box-shadow:
        0 12px 32px rgba(26,23,20,0.10),
        0 4px 12px rgba(26,23,20,0.06),
        inset 0 1px 0 rgba(255,255,255,0.9);
    transition:box-shadow .25s,transform .25s;
}
.qc-card:hover{
    box-shadow:
        0 18px 44px rgba(26,23,20,0.14),
        0 6px 16px rgba(26,23,20,0.08),
        inset 0 1px 0 rgba(255,255,255,0.9);
    transform:translateY(-2px);
}
.qc-pill{
    display:inline-flex;align-items:center;gap:3px;
    padding:3px 9px;border-radius:100px;font-size:10px;font-weight:600;
}
.qc-pill.up{background:#edf7ed;color:#2a7a3a;}
.qc-pill.dn{background:#fdf0ee;color:#c9856e;}
.qc-pill.neu{background:#f5f2ee;color:#8a7a60;}
.qc-pill.amb{background:#fdf8ee;color:#9a6a1e;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES DE DESIGN
# ═══════════════════════════════════════════════════════════════════════════════
C = {
    "amber":  "#c9a96e",
    "sage":   "#7a9e76",
    "terra":  "#c9856e",
    "slate":  "#8a9bb5",
    "ink":    "#1a1714",
    "muted":  "#8a7a60",
    "card":   "#ffffff",
    "bg":     "#ebebea",
    "border": "#e2ddd8",
    "seq":    ["#c9a96e","#7a9e76","#c9856e","#8a9bb5","#b8a0c8","#a0b8b0"],
}

PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(250,248,244,0.35)",
    font=dict(family="Outfit", color="#8a7a60", size=11),
    margin=dict(l=0, r=0, t=20, b=0),
    legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#e2ddd8", borderwidth=1,
                font=dict(size=10, family="Outfit"), orientation="h",
                yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(gridcolor="#f5f1ec", linecolor="#e2ddd8", tickcolor="#e2ddd8",
               tickfont=dict(size=10, family="Outfit"), showgrid=False,
               zeroline=True, zerolinewidth=1, zerolinecolor="#e2ddd8"),
    yaxis=dict(gridcolor="#f5f1ec", linecolor="rgba(0,0,0,0)", tickcolor="#e2ddd8",
               tickfont=dict(size=10, family="Outfit"), showgrid=True,
               zeroline=True, zerolinewidth=1.5, zerolinecolor="#d8d3cc"),
    bargap=0.28,
    bargroupgap=0.12,
)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def fmt_brl(v: float) -> str:
    """Formata valor como moeda brasileira."""
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def fmt_k(v: float) -> str:
    """Formata em formato compacto (k para milhares)."""
    if abs(v) >= 1000: return f"R$ {v/1000:.1f}k"
    return fmt_brl(v)

def card(content_html: str, padding: str = "18px 20px", extra_style: str = "") -> str:
    """Gera HTML de um card QClay com efeito 3D (gradiente sutil + sombra profunda)."""
    return (
        f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);'
        f'border-radius:18px;padding:{padding};'
        f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
        f'inset 0 1px 0 rgba(255,255,255,0.9);'
        f'border:1px solid #e2ddd8;{extra_style}">'
        f'{content_html}</div>'
    )

def badge(txt: str, tipo: str = "up") -> str:
    """Gera HTML de um badge colorido."""
    cores = {
        "up":      ("#e8f5e9","#1b5e20"),
        "down":    ("#fdecea","#b71c1c"),
        "neutral": ("#f3f0eb","#6b5b40"),
        "amber":   ("#fef3e2","#7d4e00"),
        "danger":  ("#fdecea","#b71c1c"),
        "warn":    ("#fff8e1","#7d5a00"),
        "ok":      ("#e8f5e9","#1b5e20"),
    }
    bg, fg = cores.get(tipo, cores["neutral"])
    return (
        f'<span style="background:{bg};color:{fg};border-radius:100px;padding:3px 10px;'
        f'font-size:10px;font-weight:600;display:inline-flex;align-items:center;gap:2px;">'
        f'{txt}</span>'
    )

def label(txt: str) -> str:
    return (
        f'<div style="font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;'
        f'color:#a09080;margin-bottom:8px;font-family:Outfit,sans-serif;">{txt}</div>'
    )

def big_val(txt: str, color: str = "#1a1714", size: str = "26px") -> str:
    return f'<div style="font-size:{size};font-weight:800;color:{color};line-height:1;letter-spacing:-0.5px;">{txt}</div>'

def sec(txt: str) -> None:
    """Renderiza um separador de seção com título."""
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:18px 0 12px;">'
        f'<span style="font-size:9px;font-weight:700;letter-spacing:3px;text-transform:uppercase;'
        f'color:#a09080;font-family:Outfit,sans-serif;white-space:nowrap;">{txt}</span>'
        f'<div style="flex:1;height:1px;background:#e8e3dc;"></div>'
        f'</div>', unsafe_allow_html=True)

def mk_alert(msg: str, tipo: str = "ok") -> None:
    """Renderiza um alerta estilizado."""
    cfg = {
        "ok":     ("#7a9e76","#f0f7ef","#e3f0e2"),
        "warn":   ("#c9a96e","#fdf8ee","#f5ecce"),
        "danger": ("#c9856e","#fdf0ee","#f8ddd7"),
    }
    cor, bg, border_bg = cfg.get(tipo, cfg["ok"])
    st.markdown(
        f'<div style="background:{bg};border:1px solid {border_bg};border-left:4px solid {cor};'
        f'border-radius:0 14px 14px 0;padding:14px 18px;margin:6px 0;font-size:13px;'
        f'line-height:1.7;color:#1a1714;box-shadow:0 1px 4px rgba(26,23,20,0.04);">{msg}</div>',
        unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# IA — GEMINI
# ═══════════════════════════════════════════════════════════════════════════════
def chamar_gemini(api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Chama o Gemini Flash e retorna o texto da resposta.
    Tenta gemini-2.0-flash primeiro, cai para versões anteriores se necessário."""
    genai.configure(api_key=api_key)
    modelos = ["gemini-2.0-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash"]
    ultimo_erro = None
    for nome_modelo in modelos:
        try:
            model = genai.GenerativeModel(
                model_name=nome_modelo,
                system_instruction=system_prompt,
            )
            resp = model.generate_content(user_prompt)
            return resp.text
        except Exception as e:
            ultimo_erro = e
            msg = str(e).lower()
            # Erros não recuperáveis — não tenta próximo modelo
            if "429" in str(e) or "quota" in msg or "rate" in msg:
                raise Exception(
                    "⏳ Limite diário da API gratuita atingido.\n"
                    "O acesso será restaurado automaticamente à meia-noite (horário do Pacífico).\n"
                    "Dica: adicione créditos em aistudio.google.com para uso ilimitado."
                )
            if "api_key" in msg or "invalid" in msg or "unauthorized" in msg:
                raise Exception("🔑 Chave Gemini inválida. Verifique a chave informada.")
            continue
    raise Exception(f"Nenhum modelo disponível. Último erro: {ultimo_erro}")


# ═══════════════════════════════════════════════════════════════════════════════
# CÁLCULO DE MÉTRICAS
# ═══════════════════════════════════════════════════════════════════════════════
def calcular_metricas(df: pd.DataFrame, periodos: list) -> dict:
    """
    Calcula métricas agregadas para uma lista de períodos (pd.Period).
    Comparativo vs. período equivalente anterior e YoY são calculados
    sobre o mesmo número de meses deslocados.
    """
    df = df.copy()  # evita mutar o DataFrame original
    df["data"] = pd.to_datetime(df["data"])
    n = len(periodos)

    # Período atual: todos os meses selecionados
    ma = df[df["data"].dt.to_period("M").isin(periodos)]

    # Período anterior equivalente (mesmo nº de meses, imediatamente antes)
    periodos_sorted = sorted(periodos)
    primeiro        = periodos_sorted[0]
    anterior_periodos = [primeiro - n + i for i in range(n)]
    mp = df[df["data"].dt.to_period("M").isin(anterior_periodos)]

    # YoY: mesmo conjunto de meses, 1 ano atrás
    yoy_periodos = [pd.Period(f"{p.year-1}-{p.month:02d}", freq="M") for p in periodos]
    myoy = df[df["data"].dt.to_period("M").isin(yoy_periodos)]

    rec   = ma[ma["tipo"]=="Receita"]["valor"].abs().sum()
    desp  = ma[ma["tipo"]=="Despesa"]["valor"].abs().sum()
    lucro = rec - desp

    rec_a   = mp[mp["tipo"]=="Receita"]["valor"].abs().sum() or 1
    desp_a  = mp[mp["tipo"]=="Despesa"]["valor"].abs().sum() or 1
    lucro_a = (rec_a - desp_a) or 1

    rec_yoy   = myoy[myoy["tipo"]=="Receita"]["valor"].abs().sum() or 1
    desp_yoy  = myoy[myoy["tipo"]=="Despesa"]["valor"].abs().sum() or 1
    lucro_yoy = (rec_yoy - desp_yoy) or 1

    n_trans         = max(len(ma[ma["tipo"]=="Receita"]), 1)
    ticket          = rec / n_trans
    comprometimento = (desp / rec * 100) if rec > 0 else 0

    # Média dos 3 grupos anteriores (cada grupo = mesmo nº de meses)
    ultimos3 = []
    for i in range(1, 4):
        grp = [primeiro - n*i + j for j in range(n)]
        s   = df[df["data"].dt.to_period("M").isin(grp)]
        ultimos3.append(
            s[s["tipo"]=="Receita"]["valor"].abs().sum() -
            s[s["tipo"]=="Despesa"]["valor"].abs().sum()
        )
    media3 = np.mean(ultimos3) if ultimos3 else lucro

    # Projeção: só faz sentido se o mês atual está na seleção
    hoje = datetime.today()
    mes_hoje = pd.Period(hoje, freq="M")
    if mes_hoje in periodos and n == 1:
        dias_mes = (mes_hoje.to_timestamp(how="end") - mes_hoje.to_timestamp()).days + 1
        projecao = lucro * (dias_mes / max(hoje.day, 1))
    else:
        projecao = lucro

    # Label do YoY para exibição
    primeiro_yoy = yoy_periodos[0] if yoy_periodos else periodos_sorted[0]

    return dict(
        receita=rec, despesa=desp, lucro=lucro,
        pct_rec  =(rec   - rec_a  ) / rec_a         * 100,
        pct_desp =(desp  - desp_a ) / desp_a         * 100,
        pct_lucro=(lucro - lucro_a) / abs(lucro_a)   * 100,
        margem   =(lucro/rec*100) if rec > 0 else 0,
        comprometimento=comprometimento,
        ticket=ticket, n_trans=n_trans,
        pct_rec_yoy  =(rec   - rec_yoy  ) / rec_yoy         * 100,
        pct_desp_yoy =(desp  - desp_yoy ) / desp_yoy         * 100,
        pct_lucro_yoy=(lucro - lucro_yoy) / abs(lucro_yoy)   * 100,
        mes_yoy=primeiro_yoy,
        projecao=projecao, media3=media3,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT — PDF e Excel
# ═══════════════════════════════════════════════════════════════════════════════
def gerar_excel(df: pd.DataFrame, M: dict, periodos: list, label: str = "") -> bytes:
    """
    Gera relatório Excel com múltiplas abas:
    - Resumo: KPIs do mês
    - Transações: todas as movimentações filtradas
    - Por Categoria: breakdown de despesas
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Aba 1 — Resumo executivo
        resumo_data = {
            "Métrica": [
                "Receita Total", "Despesa Total", "Saldo Líquido",
                "Margem Líquida (%)", "Comprometimento (%)",
                "Ticket Médio", "Nº Transações de Receita",
                "Projeção do Mês", "Média 3 Meses",
                "Var. Receita vs Anterior (%)", "Var. Despesa vs Anterior (%)",
                "Var. Receita YoY (%)",
            ],
            "Valor": [
                fmt_brl(M["receita"]), fmt_brl(M["despesa"]), fmt_brl(M["lucro"]),
                f"{M['margem']:.2f}%", f"{M['comprometimento']:.2f}%",
                fmt_brl(M["ticket"]), M["n_trans"],
                fmt_brl(M["projecao"]), fmt_brl(M["media3"]),
                f"{M['pct_rec']:+.2f}%", f"{M['pct_desp']:+.2f}%",
                f"{M['pct_rec_yoy']:+.2f}%",
            ]
        }
        pd.DataFrame(resumo_data).to_excel(writer, sheet_name="Resumo", index=False)

        # Aba 2 — Transações do mês
        df_mes = df[df["data"].dt.to_period("M").isin(periodos)].copy()
        df_mes["valor_abs"] = df_mes["valor"].abs()
        df_exp = df_mes[["data","tipo","categoria","valor_abs"]].copy()
        df_exp.columns = ["Data","Tipo","Categoria","Valor (R$)"]
        df_exp["Data"] = df_exp["Data"].dt.strftime("%d/%m/%Y")
        df_exp.to_excel(writer, sheet_name="Transações", index=False)

        # Aba 3 — Despesas por categoria
        desp_cat = (
            df_mes[df_mes["tipo"]=="Despesa"]
            .groupby("categoria")["valor_abs"].sum()
            .reset_index()
            .sort_values("valor_abs", ascending=False)
        )
        rec_tot = M["receita"] or 1
        desp_cat["% da Receita"] = (desp_cat["valor_abs"] / rec_tot * 100).apply(lambda x: f"{x:.2f}%")
        desp_cat.columns = ["Categoria","Total Despesa","% da Receita"]
        desp_cat.to_excel(writer, sheet_name="Por Categoria", index=False)

        # Aba 4 — Receitas por categoria
        rec_cat = (
            df_mes[df_mes["tipo"]=="Receita"]
            .groupby("categoria")["valor_abs"].sum()
            .reset_index()
            .sort_values("valor_abs", ascending=False)
        )
        rec_cat.columns = ["Categoria","Total Receita"]
        rec_cat.to_excel(writer, sheet_name="Receitas", index=False)

    return output.getvalue()

# ═══════════════════════════════════════════════════════════════════════════════
# DADOS
# ═══════════════════════════════════════════════════════════════════════════════
def normalizar_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza e padroniza colunas do DataFrame carregado."""
    df.columns = [str(c).lower().strip() for c in df.columns]
    for col in df.columns:
        if "unnamed" in col:
            sample = df[col].dropna().head(5)
            if pd.to_datetime(sample, errors="coerce", dayfirst=True).notna().all():
                df = df.rename(columns={col: "data"}); break
    alias = {
        "data":      ["data","date","dt"],
        "tipo":      ["tipo","type","movimento"],
        "categoria": ["categoria","category","servico","descricao"],
        "valor":     ["valor","value","amount","quantia","vlr"],
    }
    rename = {}
    for padrao, opcoes in alias.items():
        if padrao not in df.columns:
            for op in opcoes:
                if op in df.columns: rename[op] = padrao; break
    if rename: df = df.rename(columns=rename)
    for col in ["data","tipo","categoria","valor"]:
        if col not in df.columns:
            raise ValueError(f"Coluna '{col}' não encontrada. Disponíveis: {list(df.columns)}")
    mapa = {"entrada":"Receita","receita":"Receita","income":"Receita",
            "saida":"Despesa","despesa":"Despesa","expense":"Despesa"}
    df["tipo"] = (
        df["tipo"].astype(str).str.strip().str.lower()
        .apply(lambda x: "".join(c for c in unicodedata.normalize("NFKD",x) if not unicodedata.combining(c)))
        .map(mapa).fillna("Receita")
    )
    df["data"]  = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    return df[["data","tipo","categoria","valor"]].dropna(subset=["data"])

@st.cache_data
def gerar_demo() -> pd.DataFrame:
    """Gera dados de demonstração com 90 dias de transações."""
    np.random.seed(42)
    hoje  = datetime.today()
    datas = [hoje - timedelta(days=i) for i in range(89,-1,-1)]
    cat_r = ["MK Completo","Seguidores","Envio Directs","Mentoria"]
    cat_d = ["Fornecedores","Marketing","Plataformas","Equipamentos","Outros"]
    rows  = []
    for d in datas:
        for _ in range(np.random.randint(2,5)):
            rows.append({"data":d.strftime("%Y-%m-%d"),"tipo":"Receita",
                         "categoria":np.random.choice(cat_r,p=[0.4,0.3,0.2,0.1]),
                         "valor":round(np.random.uniform(100,1500),2)})
        for _ in range(np.random.randint(1,3)):
            rows.append({"data":d.strftime("%Y-%m-%d"),"tipo":"Despesa",
                         "categoria":np.random.choice(cat_d,p=[0.3,0.25,0.2,0.15,0.1]),
                         "valor":round(np.random.uniform(50,600),2)})
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def carregar_dados(file_bytes: bytes | None = None, file_name: str | None = None):
    """Carrega CSV ou Excel, normaliza e retorna (df, is_demo).
    Aceita bytes para que o cache funcione corretamente no Streamlit."""
    if file_bytes and file_name:
        try:
            f = io.BytesIO(file_bytes)
            nome = file_name.lower()
            if nome.endswith(".csv"):
                df_raw = pd.read_csv(f)
            elif nome.endswith(".xls"):
                df_raw = pd.read_excel(f, engine="xlrd")
            else:
                import openpyxl
                wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
                ws = wb.active
                header_row = 0
                for i, row in enumerate(ws.iter_rows(max_row=20, values_only=True)):
                    if len([c for c in row if c is not None]) >= 3:
                        header_row = i; break
                wb.close()
                f.seek(0)
                df_raw = pd.read_excel(f, header=header_row, engine="openpyxl")
                df_raw = df_raw.dropna(axis=1, how="all")
            return normalizar_df(df_raw), False
        except Exception as e:
            st.error(f"Erro ao carregar: {e}")
    return gerar_demo(), True

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH (via Supabase — ver mkpro_auth.py)
# ═══════════════════════════════════════════════════════════════════════════════
def tela_login() -> bool:
    for k, v in [("autenticado", False), ("usuario", ""), ("aviso_expiracao", ""),
                 ("df_usuario", None), ("metas_usuario", None)]:
        if k not in st.session_state:
            st.session_state[k] = v
    if st.session_state.autenticado:
        return True

    hoje  = datetime.today()
    dias  = ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"]
    meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown(
            f'<div style="background:#fff;border-radius:20px;padding:40px 36px;'
            f'box-shadow:0 8px 48px rgba(26,23,20,0.1);margin-top:60px;position:relative;overflow:hidden;">'
            f'<div style="position:absolute;top:-40px;right:-40px;width:120px;height:120px;'
            f'border-radius:50%;background:#c9a96e18;pointer-events:none;"></div>'
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:24px;">'
            f'<div style="width:40px;height:40px;border-radius:12px;background:#1a1714;'
            f'display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;color:#c9a96e;">M</div>'
            f'<div><div style="font-weight:800;font-size:16px;color:#1a1714;">MK Pro Finance</div>'
            f'<div style="font-size:10px;color:#8a7a60;letter-spacing:1px;">Acesso exclusivo</div></div></div>'
            f'<div style="background:#f5f2ee;border-radius:12px;padding:12px 16px;margin-bottom:24px;'
            f'display:flex;align-items:center;gap:12px;">'
            f'<div style="text-align:center;"><div style="font-size:28px;font-weight:800;color:#1a1714;line-height:1;">{hoje.day}</div>'
            f'<div style="font-size:9px;color:#8a7a60;">{dias[hoje.weekday()]}</div></div>'
            f'<div style="width:1px;height:30px;background:#e0dbd4;"></div>'
            f'<div style="font-size:12px;color:#8a7a60;">{meses[hoje.month-1]}, {hoje.year}</div>'
            f'</div></div>', unsafe_allow_html=True)

        with st.form("login", clear_on_submit=False):
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            ok    = st.form_submit_button("Entrar no Dashboard →", use_container_width=True, type="primary")
            if ok:
                if not email or not senha:
                    st.error("Preencha todos os campos.")
                else:
                    acesso, msg = verificar_acesso(email, senha)
                    if acesso:
                        email_lower = email.strip().lower()
                        df_salvo, _  = carregar_dados_salvos(email_lower)
                        metas_salvas = carregar_metas(email_lower)
                        st.session_state.autenticado   = True
                        st.session_state.usuario       = email_lower
                        st.session_state.df_usuario    = df_salvo
                        st.session_state.metas_usuario = metas_salvas
                        st.rerun()
                    else:
                        st.error(msg)
        st.caption("Não tem acesso? Adquira em seusite.com.br")
    return False

if not tela_login(): st.stop()

# Aviso de expiração próxima (exibido após login)
if st.session_state.get("aviso_expiracao"):
    st.warning(st.session_state["aviso_expiracao"])
    st.session_state["aviso_expiracao"] = ""  # exibe só uma vez por sessão

# ═══════════════════════════════════════════════════════════════════════════════
# TOPBAR + UPLOAD + PERÍODO
# ═══════════════════════════════════════════════════════════════════════════════
hoje      = datetime.today()
dias_pt   = ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"]
meses_pt  = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

t1, t2, t3, t4, t5 = st.columns([0.65, 0.9, 1.6, 0.9, 0.85])

with t1:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;padding:4px 0;">'
        f'<div style="width:38px;height:38px;border-radius:12px;background:#1a1714;'
        f'display:flex;align-items:center;justify-content:center;font-weight:800;font-size:15px;color:#c9a96e;'
        f'box-shadow:0 2px 8px rgba(26,23,20,0.2);">M</div>'
        f'<div><div style="font-weight:800;font-size:14px;color:#1a1714;line-height:1.1;letter-spacing:-.2px;">MK Pro</div>'
        f'<div style="font-size:9px;color:#a09080;letter-spacing:1.5px;text-transform:uppercase;">Finance</div></div></div>',
        unsafe_allow_html=True)

with t2:
    st.markdown(
        f'<div style="background:#fff;border-radius:14px;padding:8px 14px;'
        f'border:1px solid #e2ddd8;box-shadow:0 1px 4px rgba(26,23,20,0.06);'
        f'display:flex;align-items:center;gap:10px;">'
        f'<div style="text-align:center;"><div style="font-size:24px;font-weight:800;color:#1a1714;line-height:1;">{hoje.day}</div>'
        f'<div style="font-size:8px;color:#a09080;letter-spacing:1px;text-transform:uppercase;">{dias_pt[hoje.weekday()]}</div></div>'
        f'<div style="width:1px;height:28px;background:#e8e3dc;"></div>'
        f'<div><div style="font-size:11px;font-weight:600;color:#1a1714;">{meses_pt[hoje.month-1]}</div>'
        f'<div style="font-size:10px;color:#a09080;">{hoje.year}</div></div>'
        f'</div>', unsafe_allow_html=True)

with t3:
    uploaded = st.file_uploader("", type=["csv","xlsx","xls"], label_visibility="collapsed",
                                help="CSV ou Excel: colunas data, tipo, categoria, valor")

with t4:
    periodo_ph = st.empty()

with t5:
    usuario_ini  = st.session_state.usuario.split("@")[0].upper()[:2]
    usuario_nome = st.session_state.usuario.split("@")[0].capitalize()
    _eh_admin    = is_admin(st.session_state.usuario)
    col_u, col_s = st.columns([3,1])
    with col_u:
        badge_admin = (
            '<span style="background:#1a1714;color:#c9a96e;border-radius:100px;'
            'padding:2px 7px;font-size:8px;font-weight:700;letter-spacing:1px;">ADMIN</span>'
            if _eh_admin else ""
        )
        st.markdown(
            f'<div style="background:#fff;border-radius:100px;padding:5px 14px 5px 5px;'
            f'border:1px solid #e2ddd8;box-shadow:0 1px 4px rgba(26,23,20,0.06);'
            f'display:flex;align-items:center;gap:8px;justify-content:flex-end;">'
            f'<div style="width:28px;height:28px;border-radius:50%;background:#1a1714;'
            f'display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:800;color:#c9a96e;'
            f'flex-shrink:0;">{usuario_ini}</div>'
            f'<span style="font-size:11px;font-weight:600;color:#1a1714;white-space:nowrap;">{usuario_nome}</span>'
            f'{badge_admin}'
            f'</div>', unsafe_allow_html=True)
    with col_s:
        if st.button("Sair", key="sair_btn"):
            st.session_state.autenticado   = False
            st.session_state.df_usuario    = None
            st.session_state.metas_usuario = None
            st.rerun()

st.markdown('<div style="height:1px;background:#e8e3dc;margin:10px 0 14px;"></div>', unsafe_allow_html=True)

# ── Troca de senha ────────────────────────────────────────────────────────────
with st.expander("🔑 Alterar Senha", expanded=False):
    with st.form("form_trocar_senha"):
        ts1, ts2, ts3 = st.columns(3)
        with ts1:
            senha_atual = st.text_input("Senha atual", type="password", key="ts_atual")
        with ts2:
            senha_nova1 = st.text_input("Nova senha", type="password", key="ts_nova1")
        with ts3:
            senha_nova2 = st.text_input("Confirmar nova senha", type="password", key="ts_nova2")
        if st.form_submit_button("Alterar Senha"):
            if not senha_atual or not senha_nova1 or not senha_nova2:
                st.error("Preencha todos os campos.")
            elif senha_nova1 != senha_nova2:
                st.error("As senhas não conferem.")
            else:
                ok, msg = trocar_senha(st.session_state.usuario, senha_atual, senha_nova1)
                st.success(msg) if ok else st.error(msg)

# ═══════════════════════════════════════════════════════════════════════════════
# PAINEL ADMIN — visível apenas para admins
# ═══════════════════════════════════════════════════════════════════════════════
if _eh_admin:
    with st.expander("⚙️ Painel Admin — Gerenciar Usuários", expanded=False):

        # ── Adicionar novo usuário ─────────────────────────────────────────────
        sec("Adicionar Usuário")
        col_a1, col_a2, col_a3 = st.columns([2, 2, 1])
        with col_a1:
            novo_email = st.text_input("E-mail", placeholder="cliente@email.com", key="admin_novo_email")
            novo_plano = st.selectbox("Plano", ["mensal", "vitalicio", "admin"], key="admin_novo_plano")
        with col_a2:
            nova_senha = st.text_input("Senha inicial", type="password", placeholder="SenhaPadrao@123", key="admin_nova_senha")
            nova_expira = st.date_input("Expira em", key="admin_nova_expira") if novo_plano == "mensal" else None
        with col_a3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("Adicionar", key="btn_add_user", use_container_width=True):
                expira_str = nova_expira.isoformat() if nova_expira else None
                ok, msg = adicionar_usuario(novo_email, nova_senha, novo_plano, expira_str)
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()

        # ── Clientes ativos ────────────────────────────────────────────────────
        sec("Usuários Cadastrados")
        usuarios = listar_usuarios()
        if usuarios:
            hoje_dt = datetime.now(timezone.utc)
            rows = []
            for u in usuarios:
                expira = u.get("expira_em")
                if not expira:
                    status, expira_fmt = "✅ Sem expiração", "—"
                else:
                    try:
                        exp_dt = datetime.fromisoformat(expira).replace(tzinfo=timezone.utc)
                        dias_rest  = (exp_dt - hoje_dt).days
                        expira_fmt = exp_dt.strftime("%d/%m/%Y")
                        if not u["ativo"]:          status = "🚫 Desativado"
                        elif dias_rest < 0:         status = f"❌ Vencido há {abs(dias_rest)}d"
                        elif dias_rest <= 7:        status = f"⚠️ Vence em {dias_rest}d"
                        else:                       status = f"✅ Ativo ({dias_rest}d)"
                    except Exception:
                        expira_fmt, status = expira, "⚠️ Data inválida"
                rows.append({"E-mail": u["email"], "Plano": u.get("plano","—"),
                             "Expira": expira_fmt, "Status": status})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            sec("Ações Rápidas")
            col_b1, col_b2, col_b3 = st.columns(3)
            emails_lista = [u["email"] for u in usuarios]
            with col_b1:
                email_ren = st.selectbox("Renovar expiração", emails_lista, key="admin_ren_email")
                nova_data = st.date_input("Nova data", key="admin_ren_data")
                if st.button("Renovar", key="btn_renovar"):
                    ok, msg = atualizar_expiracao(email_ren, nova_data.isoformat())
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()
            with col_b2:
                email_des = st.selectbox("Desativar usuário", emails_lista, key="admin_des_email")
                if st.button("Desativar", key="btn_desativar", type="secondary"):
                    ok, msg = desativar_usuario(email_des)
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()
            with col_b3:
                email_pw = st.selectbox("Redefinir senha", emails_lista, key="admin_pw_email")
                nova_pw  = st.text_input("Nova senha", type="password", key="admin_pw_val")
                if st.button("Redefinir Senha", key="btn_pw"):
                    ok, msg = redefinir_senha(email_pw, nova_pw)
                    st.success(msg) if ok else st.error(msg)
        else:
            st.info("Nenhum usuário cadastrado ainda.")

        sec("Configuração do secrets.toml")
        st.code("""
SUPABASE_URL="https://lnacenhljcwbuchnzyog.supabase.co"
SUPABASE_SERVICE_KEY="eyJ..."
""", language="toml")

# ═══════════════════════════════════════════════════════════════════════════════
# LOAD + PERÍODO
# ═══════════════════════════════════════════════════════════════════════════════
if uploaded is not None:
    file_bytes = uploaded.read()
    file_name  = uploaded.name
    df_novo, _ = carregar_dados(file_bytes, file_name)
    st.session_state.df_usuario = df_novo
    salvar_dados(st.session_state.usuario, df_novo, file_name)

if st.session_state.get("df_usuario") is not None:
    df      = st.session_state.df_usuario.copy()
    is_demo = False
else:
    df, is_demo = gerar_demo(), True
df["data"]   = pd.to_datetime(df["data"], errors="coerce")
meses_reais  = sorted(df["data"].dt.to_period("M").dropna().unique(), reverse=True)
meses_labels = [str(m) for m in meses_reais]

meses_sel = periodo_ph.multiselect(
    "Período", meses_labels,
    default=[meses_labels[0]] if meses_labels else [],
    key="mes_sel", label_visibility="collapsed",
    placeholder="Selecione um ou mais meses…"
)
if not meses_sel:
    meses_sel = [meses_labels[0]] if meses_labels else []

# Períodos selecionados como pd.Period (ordenados)
periodos_sel = sorted([pd.Period(m, freq="M") for m in meses_sel])

# mes_ref = período mais recente da seleção (para filtros pontuais)
mes_ref  = periodos_sel[-1]
# Label compacto para exibição
mes_label = meses_sel[0] if len(meses_sel) == 1 else f"{meses_sel[-1]} → {meses_sel[0]}"

M = calcular_metricas(df, periodos_sel)

if is_demo:
    st.info("Dados de demonstração — faça upload do seu arquivo para análise real.", icon="ℹ️")

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Visão Geral", "Fluxo de Caixa", "Categorias",
    "Alertas IA", "Metas", "Transações", "Visão Anual"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — VISÃO GERAL
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:

    def dp(pct: float):
        if pct > 0:   return "up",      f"▲ {pct:.1f}%"
        elif pct < 0: return "down",    f"▼ {abs(pct):.1f}%"
        else:          return "neutral", "— estável"

    dc1,ds1 = dp(M["pct_rec"])
    dc2,ds2 = dp(M["pct_desp"])
    dc3,ds3 = dp(M["pct_lucro"])

    # ── HERO ROW ──────────────────────────────────────────────────────────────
    h1, h2 = st.columns([2, 1])

    with h1:
        stats_hero = [
            (fmt_k(M["receita"]),  "Receita",  C["sage"]),
            (fmt_k(M["despesa"]),  "Despesas", C["terra"]),
            (fmt_k(M["lucro"]),    "Saldo",    C["amber"]),
            (f"{M['margem']:.1f}%","Margem",   C["slate"]),
        ]
        stats_html = ""
        for sv, sl, sc in stats_hero:
            stats_html += (
                f'<div style="background:radial-gradient(ellipse at 35% 32%,#ffffff 0%,#f3efe9 70%,#ebe6df 100%);'
                f'border-radius:14px;padding:12px 16px;text-align:center;min-width:80px;'
                f'box-shadow:0 4px 12px rgba(26,23,20,0.08),inset 0 1px 0 rgba(255,255,255,0.9),'
                f'inset 0 -2px 4px rgba(26,23,20,0.04);">'
                f'<div style="font-size:17px;font-weight:800;color:{sc};line-height:1;">{sv}</div>'
                f'<div style="font-size:8px;color:#a09080;text-transform:uppercase;letter-spacing:1.5px;margin-top:3px;font-weight:600;">{sl}</div>'
                f'</div>'
            )
        st.markdown(
            f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:18px;padding:20px 24px;'
            f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
            f'inset 0 1px 0 rgba(255,255,255,0.9);'
            f'border:1px solid #e8e3dc;display:flex;align-items:center;justify-content:space-between;gap:16px;">'
            f'<div style="flex:1;">'
            f'<div style="font-size:9px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#a09080;margin-bottom:8px;">MK Pro Finance · {mes_label}</div>'
            f'<div style="font-family:Fraunces,serif;font-size:30px;font-weight:300;font-style:italic;color:#1a1714;line-height:1.1;">Olá, bem-vindo 👋</div>'
            f'<div style="font-size:12px;color:#a09080;margin-top:6px;font-weight:400;">Seus dados financeiros estão prontos para análise.</div>'
            f'</div>'
            f'<div style="display:flex;gap:8px;flex-shrink:0;">{stats_html}</div>'
            f'</div>', unsafe_allow_html=True)

    with h2:
        # Card: Saldo do Período — esfera 3D proporcional à margem
        df_hero = df[df["data"].dt.to_period("M").isin(periodos_sel)].copy()
        rec_hero = df_hero[df_hero["tipo"]=="Receita"]["valor"].abs().sum()
        desp_hero = df_hero[df_hero["tipo"]=="Despesa"]["valor"].abs().sum()
        saldo_hero = rec_hero - desp_hero
        margem_hero = (saldo_hero / rec_hero * 100) if rec_hero > 0 else 0

        # Tamanho da esfera proporcional ao valor absoluto da margem (72px–124px)
        abs_margem = min(abs(margem_hero), 100)
        sphere_size = int(72 + (abs_margem / 100) * 52)  # 72 a 124

        # Cor base conforme sinal do saldo
        if saldo_hero >= 0:
            cor_base    = "#7a9e76"   # sage
            cor_clara   = "#a8c4a4"
            cor_escura  = "#4f7a4b"
            glow_rgba   = "rgba(122,158,118,0.35)"
        else:
            cor_base    = "#c9856e"   # terra
            cor_clara   = "#e2a89a"
            cor_escura  = "#9a5841"
            glow_rgba   = "rgba(201,133,110,0.35)"

        # Gradiente radial simulando luz vinda do canto superior esquerdo (35% 32%)
        sphere_bg = (
            f"radial-gradient(circle at 35% 32%,"
            f"#ffffff 0%,{cor_clara} 18%,{cor_base} 55%,{cor_escura} 100%)"
        )

        # Título do card reflete o período
        anos_no_periodo = sorted(set(p.year for p in periodos_sel))
        if len(anos_no_periodo) == 1:
            titulo_card = f"Saldo · {anos_no_periodo[0]}"
        else:
            titulo_card = f"Saldo · {anos_no_periodo[0]}–{anos_no_periodo[-1]}"

        st.markdown(
            f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:16px;padding:16px 20px;'
            f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
            f'inset 0 1px 0 rgba(255,255,255,0.9);'
            f'border:1px solid #e0dbd4;height:100%;">'
            f'<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
            f'color:#8a7a60;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">'
            f'{titulo_card} <span style="color:#c9a96e;">{len(periodos_sel)}m</span></div>'

            # ── Container da esfera 3D ─────────────────────────────────────
            f'<div style="position:relative;height:170px;display:flex;align-items:center;justify-content:center;">'

            # Glow externo (halo radial atrás da esfera)
            f'<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);'
            f'width:{int(sphere_size*1.7)}px;height:{int(sphere_size*1.7)}px;border-radius:50%;'
            f'background:radial-gradient(circle,{glow_rgba} 0%,rgba(255,255,255,0) 70%);'
            f'pointer-events:none;"></div>'

            # Sombra projetada elíptica (chão)
            f'<div style="position:absolute;bottom:14px;left:50%;transform:translateX(-50%);'
            f'width:{int(sphere_size*0.85)}px;height:10px;border-radius:50%;'
            f'background:radial-gradient(ellipse,rgba(26,23,20,0.28) 0%,rgba(26,23,20,0) 70%);'
            f'filter:blur(2px);"></div>'

            # ── Esfera principal ────────────────────────────────────────────
            f'<div style="position:relative;width:{sphere_size}px;height:{sphere_size}px;border-radius:50%;'
            f'background:{sphere_bg};'
            f'box-shadow:inset -8px -10px 20px rgba(26,23,20,0.35),'
            f'inset 6px 6px 18px rgba(255,255,255,0.55),'
            f'0 8px 24px {glow_rgba};'
            f'display:flex;flex-direction:column;align-items:center;justify-content:center;'
            f'color:#fff;text-shadow:0 1px 3px rgba(26,23,20,0.4);">'

            # Reflexo superior (mancha branca desfocada simulando luz)
            f'<div style="position:absolute;top:10%;left:22%;width:38%;height:24%;border-radius:50%;'
            f'background:radial-gradient(ellipse,rgba(255,255,255,0.55) 0%,rgba(255,255,255,0) 70%);'
            f'filter:blur(3px);pointer-events:none;"></div>'

            # Valor do saldo
            f'<div style="font-size:{int(sphere_size/6)}px;font-weight:800;line-height:1;letter-spacing:-0.3px;'
            f'position:relative;z-index:2;">{fmt_k(saldo_hero)}</div>'

            # Margem % dentro da esfera
            f'<div style="font-size:{int(sphere_size/10)}px;font-weight:600;opacity:0.9;margin-top:4px;'
            f'position:relative;z-index:2;">{margem_hero:+.1f}%</div>'

            f'</div>'   # fim esfera
            f'</div>'   # fim container

            # Badge YoY embaixo
            f'<div style="margin-top:8px;">{badge("YoY: "+str(round(M["pct_lucro_yoy"],1))+"%", "up" if M["pct_lucro_yoy"]>=0 else "down")}</div>'
            f'</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # ── LINHA 2: 4 KPIs ───────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    KPI_CFG = {
        "Receita":        (C["sage"],  "#e8f4e8", "↑"),
        "Despesas":       (C["terra"], "#fdecea", "↓"),
        "Ticket Médio":   (C["slate"], "#e8eef8", "◎"),
        "Projeção do Mês":(C["amber"], "#fdf8ee", "→"),
    }

    def kpi(col, lbl, val, delta_str, delta_tipo, sub=None, mini_bars=None, cor_val="#1a1714"):
        cfg = KPI_CFG.get(lbl, (C["amber"], "#fdf8ee", "◎"))
        cor_icon, bg_icon, icone = cfg

        # Barras com gradiente cilíndrico 3D
        bars_html = ""
        if mini_bars:
            bars_html = f'<div style="display:flex;gap:2px;align-items:flex-end;height:32px;margin-top:10px;padding:0 2px;">'
            max_b = max(mini_bars) or 1
            for i, b in enumerate(mini_bars):
                h = max(int(b/max_b*100), 10)
                alpha = "1" if i==len(mini_bars)-1 else ("0.7" if i==len(mini_bars)-2 else "0.4")
                bars_html += (
                    f'<div style="flex:1;border-radius:3px 3px 0 0;min-height:3px;'
                    f'background:linear-gradient(180deg,rgba(255,255,255,0.55) 0%,{cor_icon} 35%,{cor_icon} 70%,rgba(0,0,0,0.18) 100%);'
                    f'opacity:{alpha};height:{h}%;'
                    f'box-shadow:0 1px 2px rgba(26,23,20,0.15),inset 0 1px 0 rgba(255,255,255,0.5);"></div>'
                )
            bars_html += '</div>'

        # Spacer equivalente às mini_bars quando não há barras — mantém altura uniforme dos 4 KPIs
        spacer_html = '<div style="height:32px;margin-top:10px;"></div>' if not mini_bars else ""

        sub_html = f'<div style="font-size:10px;color:#a09080;margin-top:4px;font-weight:500;">{sub}</div>' if sub else ""

        with col:
            st.markdown(
                f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);'
                f'border-radius:18px;padding:18px 18px 14px;'
                f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
                f'inset 0 1px 0 rgba(255,255,255,0.9);'
                f'border:1px solid #e8e3dc;position:relative;overflow:hidden;">'
                f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:{cor_icon};border-radius:18px 18px 0 0;opacity:.6;"></div>'
                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'

                # Ícone esférico 3D
                f'<div style="width:36px;height:36px;border-radius:50%;'
                f'background:radial-gradient(circle at 35% 32%,#ffffff 0%,{bg_icon} 40%,{cor_icon} 100%);'
                f'box-shadow:inset -2px -3px 6px rgba(26,23,20,0.18),'
                f'inset 2px 2px 4px rgba(255,255,255,0.7),'
                f'0 3px 8px rgba(26,23,20,0.18);'
                f'display:flex;align-items:center;justify-content:center;font-size:15px;color:#fff;font-weight:800;'
                f'text-shadow:0 1px 2px rgba(26,23,20,0.3);">{icone}</div>'

                f'<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#a09080;">{lbl}</div>'
                f'</div>'
                f'<div style="font-size:24px;font-weight:800;color:{cor_val};line-height:1;letter-spacing:-.5px;">{val}</div>'
                f'<div style="margin-top:6px;">{badge(delta_str, delta_tipo)}</div>'
                f'{sub_html}{bars_html}{spacer_html}'
                f'</div>', unsafe_allow_html=True)

    def sparkdata(tipo):
        # Mostra os 6 grupos anteriores + o período atual (cada grupo = mesmo nº de meses)
        n_p = len(periodos_sel)
        primeiro_p = sorted(periodos_sel)[0]
        vals = []
        for i in range(5, -1, -1):
            grp = [primeiro_p - n_p*i + j for j in range(n_p)]
            s = df[df["data"].dt.to_period("M").isin(grp)]
            vals.append(s[s["tipo"]==tipo]["valor"].abs().sum())
        return vals

    spark_rec  = sparkdata("Receita")
    spark_desp = sparkdata("Despesa")

    kpi(k1, "Receita", fmt_brl(M["receita"]), ds1+" vs anterior", dc1,
        sub=f"YoY {M['pct_rec_yoy']:+.1f}%", mini_bars=spark_rec)
    kpi(k2, "Despesas", fmt_brl(M["despesa"]), ds2+" vs anterior", dc2,
        sub=f"YoY {M['pct_desp_yoy']:+.1f}%", mini_bars=spark_desp, cor_val="#c9856e")
    kpi(k3, "Ticket Médio", fmt_brl(M["ticket"]), f"{M['n_trans']} transações", "neutral",
        sub="por entrada de receita")
    kpi(k4, "Projeção do Mês", fmt_brl(M["projecao"]),
        "▲ em andamento" if M["projecao"]!=M["lucro"] else "mês encerrado",
        "up" if M["projecao"]>=0 else "down",
        sub=f"Média 3m: {fmt_brl(M['media3'])}")

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # ── LINHA 3: Gráfico + Eficiência + YoY ──────────────────────────────────
    g1, g2, g3 = st.columns([2, 1, 1])

    with g1:
        sec("Receita · Despesa · Saldo — 6 períodos")
        n_p        = len(periodos_sel)
        primeiro_p = sorted(periodos_sel)[0]
        ex, rv, dv = [], [], []
        for i in range(5, -1, -1):
            grp   = [primeiro_p - n_p*i + j for j in range(n_p)]
            sub   = df[df["data"].dt.to_period("M").isin(grp)]
            r_grp = sub[sub["tipo"]=="Receita"]["valor"].abs().sum()
            d_grp = sub[sub["tipo"]=="Despesa"]["valor"].abs().sum()
            lbl   = str(grp[0]) if n_p == 1 else f"{grp[0]}-{grp[-1]}"
            ex.append(lbl); rv.append(r_grp); dv.append(d_grp)
        lucro_v = [r-d for r,d in zip(rv,dv)]

        fig = go.Figure()
        fig.add_bar(name="Receita", x=ex, y=rv, width=0.22,
                    marker=dict(color=C["sage"], opacity=0.9,
                                line=dict(width=1.5, color="#fff"), cornerradius=4))
        fig.add_bar(name="Despesa", x=ex, y=dv, width=0.22,
                    marker=dict(color=C["terra"], opacity=0.9,
                                line=dict(width=1.5, color="#fff"), cornerradius=4))
        fig.add_scatter(name="Saldo", x=ex, y=lucro_v, mode="lines+markers",
                        line=dict(color=C["amber"], width=3),
                        marker=dict(size=11, color=C["amber"],
                                    line=dict(color="#fff", width=2.5)))
        fig.update_layout(**PLOT, barmode="group", height=220)
        fig.update_yaxes(tickformat=",.0f", tickprefix="R$ ")
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        sec("Eficiência")
        comp     = M["comprometimento"]
        comp_cor = C["terra"] if comp > 80 else C["amber"] if comp > 60 else C["sage"]
        comp_bg  = "#fdecea" if comp > 80 else "#fdf8ee" if comp > 60 else "#edf7eb"

        margem_cor = C["sage"] if M["margem"] >= 20 else C["amber"] if M["margem"] >= 10 else C["terra"]

        # Dois donuts lado a lado dentro de um card HTML, igual ao estilo "Distribuição de Despesas"
        rows_ef = (
            # Margem
            f'<div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid #f5f1ec;">'
            f'<div style="width:34px;height:34px;border-radius:50%;'
            f'background:radial-gradient(circle at 35% 32%,#ffffff 0%,#edf7eb 40%,{margem_cor} 100%);'
            f'box-shadow:inset -2px -3px 5px rgba(26,23,20,0.18),'
            f'inset 2px 2px 4px rgba(255,255,255,0.7),'
            f'0 3px 7px rgba(26,23,20,0.15);'
            f'display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800;color:#fff;'
            f'text-shadow:0 1px 2px rgba(26,23,20,0.3);flex-shrink:0;">%</div>'
            f'<div style="flex:1;">'
            f'<div style="font-size:11px;font-weight:600;color:#1a1714;">Margem Líquida</div>'
            f'<div style="height:6px;background:#f0ece8;border-radius:3px;margin-top:5px;'
            f'box-shadow:inset 0 1px 2px rgba(26,23,20,0.08);">'
            f'<div style="height:100%;width:{min(M["margem"],100):.1f}%;'
            f'background:linear-gradient(180deg,rgba(255,255,255,0.5) 0%,{margem_cor} 35%,{margem_cor} 70%,rgba(0,0,0,0.2) 100%);'
            f'border-radius:3px;box-shadow:0 1px 2px rgba(26,23,20,0.15);"></div>'
            f'</div></div>'
            f'<div style="font-size:14px;font-weight:800;color:{margem_cor};flex-shrink:0;">{M["margem"]:.1f}%</div>'
            f'</div>'
            # Comprometimento
            f'<div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid #f5f1ec;">'
            f'<div style="width:34px;height:34px;border-radius:50%;'
            f'background:radial-gradient(circle at 35% 32%,#ffffff 0%,{comp_bg} 40%,{comp_cor} 100%);'
            f'box-shadow:inset -2px -3px 5px rgba(26,23,20,0.18),'
            f'inset 2px 2px 4px rgba(255,255,255,0.7),'
            f'0 3px 7px rgba(26,23,20,0.15);'
            f'display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800;color:#fff;'
            f'text-shadow:0 1px 2px rgba(26,23,20,0.3);flex-shrink:0;">↓</div>'
            f'<div style="flex:1;">'
            f'<div style="font-size:11px;font-weight:600;color:#1a1714;">Comprometimento</div>'
            f'<div style="height:6px;background:#f0ece8;border-radius:3px;margin-top:5px;position:relative;'
            f'box-shadow:inset 0 1px 2px rgba(26,23,20,0.08);">'
            f'<div style="height:100%;width:{min(comp,100):.1f}%;'
            f'background:linear-gradient(180deg,rgba(255,255,255,0.5) 0%,{comp_cor} 35%,{comp_cor} 70%,rgba(0,0,0,0.2) 100%);'
            f'border-radius:3px;box-shadow:0 1px 2px rgba(26,23,20,0.15);"></div>'
            f'<div style="position:absolute;top:-3px;left:60%;width:1.5px;height:12px;background:rgba(201,133,110,0.4);"></div>'
            f'</div></div>'
            f'<div style="font-size:14px;font-weight:800;color:{comp_cor};flex-shrink:0;">{comp:.1f}%</div>'
            f'</div>'
            # Saldo
            + (lambda l=M["lucro"], c=C["sage"] if M["lucro"]>=0 else C["terra"]: (
            f'<div style="display:flex;align-items:center;gap:10px;padding:9px 0;">'
            f'<div style="width:34px;height:34px;border-radius:50%;'
            f'background:radial-gradient(circle at 35% 32%,#ffffff 0%,#f5f2ee 40%,{c} 100%);'
            f'box-shadow:inset -2px -3px 5px rgba(26,23,20,0.18),'
            f'inset 2px 2px 4px rgba(255,255,255,0.7),'
            f'0 3px 7px rgba(26,23,20,0.15);'
            f'display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800;color:#fff;'
            f'text-shadow:0 1px 2px rgba(26,23,20,0.3);flex-shrink:0;">{'+'  if l>=0 else '-'}</div>'
            f'<div style="flex:1;">'
            f'<div style="font-size:11px;font-weight:600;color:#1a1714;">Saldo do Período</div>'
            f'<div style="font-size:10px;color:#a09080;margin-top:2px;">receita − despesa</div>'
            f'</div>'
            f'<div style="font-size:14px;font-weight:800;color:{c};flex-shrink:0;">{fmt_k(l)}</div>'
            f'</div>'
            ))()
        )

        st.markdown(
            f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:16px;padding:16px 18px;'
            f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
            f'inset 0 1px 0 rgba(255,255,255,0.9);'
            f'border:1px solid #e0dbd4;">'
            f'{rows_ef}'
            f'<div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap;">'
            f'{badge("Margem saudável" if M["margem"]>=20 else "Margem baixa", "ok" if M["margem"]>=20 else "warn")}'
            f'{badge("Comprometimento OK" if comp<60 else "Comprometimento alto", "ok" if comp<60 else "danger")}'
            f'</div></div>',
            unsafe_allow_html=True)

    with g3:
        sec("Comparativo YoY")
        yoy_items = [
            ("Receita",  M["receita"],  M["pct_rec_yoy"]),
            ("Despesa",  M["despesa"],  M["pct_desp_yoy"]),
            ("Saldo",    M["lucro"],    M["pct_lucro_yoy"]),
            ("Margem",   M["margem"],   M["pct_rec_yoy"]-M["pct_desp_yoy"]),
        ]
        rows_html = ""
        for nome, val, pct in yoy_items:
            pct_tipo = "up" if pct >= 0 else "down"
            val_str  = f"{val:.1f}%" if nome == "Margem" else fmt_k(val)
            rows_html += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:8px 0;border-bottom:1px solid #f0ece8;">'
                f'<span style="font-size:11px;color:#8a7a60;font-weight:500;">{nome}</span>'
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'{badge(f"{pct:+.1f}%", pct_tipo)}'
                f'<span style="font-size:12px;font-weight:700;color:#1a1714;">{val_str}</span>'
                f'</div></div>'
            )
        st.markdown(
            f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:16px;padding:14px 16px;'
            f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
            f'inset 0 1px 0 rgba(255,255,255,0.9);'
            f'border:1px solid #e0dbd4;">'
            f'<div style="font-size:9px;font-weight:600;letter-spacing:2px;text-transform:uppercase;'
            f'color:#8a7a60;margin-bottom:6px;">{periodos_sel[0].year if len(set(p.year for p in periodos_sel))==1 else str(sorted(periodos_sel)[0].year)+"-"+str(sorted(periodos_sel)[-1].year)} vs {M["mes_yoy"].year}</div>'
            f'{rows_html}</div>', unsafe_allow_html=True)

    # ── LINHA 4: Atividades recentes ──────────────────────────────────────────
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    a1, a2 = st.columns([2, 1])

    with a1:
        sec("Atividades Recentes")
        df_recentes = df[df["data"].dt.to_period("M").isin(periodos_sel)].copy()
        df_recentes["valor_abs"] = df_recentes["valor"].abs()
        df_recentes = df_recentes.sort_values("data", ascending=False).head(8)

        cat_cfg = {
            "MK Completo":   ("#c9a96e","#fdf8ee"),
            "Seguidores":    ("#7a9e76","#edf7eb"),
            "Envio Directs": ("#8a9bb5","#eef2f8"),
            "Mentoria":      ("#b8a0c8","#f5f0fb"),
            "Fornecedores":  ("#c9856e","#fdecea"),
            "Marketing":     ("#c9856e","#fdecea"),
            "Plataformas":   ("#8a9bb5","#eef2f8"),
            "Equipamentos":  ("#8a9bb5","#eef2f8"),
            "Outros":        ("#a09080","#f3f0eb"),
        }
        rows_a = ""
        for _, row in df_recentes.iterrows():
            cor_icon_fg, cor_icon_bg = cat_cfg.get(row["categoria"], ("#a09080","#f3f0eb"))
            sinal   = "+" if row["tipo"] == "Receita" else "−"
            cor_val = "#7a9e76" if row["tipo"] == "Receita" else "#c9856e"
            inicial = row["categoria"][0].upper()
            rows_a += (
                f'<div style="display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid #f5f1ec;">'
                f'<div style="width:34px;height:34px;border-radius:50%;'
                f'background:radial-gradient(circle at 35% 32%,#ffffff 0%,{cor_icon_bg} 40%,{cor_icon_fg} 100%);'
                f'box-shadow:inset -2px -3px 5px rgba(26,23,20,0.18),'
                f'inset 2px 2px 4px rgba(255,255,255,0.7),'
                f'0 3px 7px rgba(26,23,20,0.15);'
                f'display:flex;align-items:center;justify-content:center;font-size:13px;'
                f'font-weight:800;color:#fff;text-shadow:0 1px 2px rgba(26,23,20,0.3);flex-shrink:0;">{inicial}</div>'
                f'<div style="flex:1;min-width:0;">'
                f'<div style="font-size:12px;font-weight:600;color:#1a1714;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row["categoria"]}</div>'
                f'<div style="font-size:10px;color:#a09080;font-weight:500;">{row["tipo"]} · {row["data"].strftime("%d/%m")}</div>'
                f'</div>'
                f'<div style="font-size:13px;font-weight:700;color:{cor_val};flex-shrink:0;">{sinal} {fmt_brl(row["valor_abs"])}</div>'
                f'</div>'
            )
        st.markdown(
            f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:16px;padding:16px 18px;'
            f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
            f'inset 0 1px 0 rgba(255,255,255,0.9);'
            f'border:1px solid #e0dbd4;">'
            f'{rows_a}</div>', unsafe_allow_html=True)

    with a2:
        # ── Distribuição de Receitas (caixa superior) ─────────────────────────
        sec("Distribuição de Receitas")
        df_mes_cat = df[df["data"].dt.to_period("M").isin(periodos_sel)].copy()
        df_mes_cat["valor_abs"] = df_mes_cat["valor"].abs()
        rec_cat_dist  = df_mes_cat[df_mes_cat["tipo"]=="Receita"].groupby("categoria")["valor_abs"].sum()
        rec_tot_dist  = rec_cat_dist.sum()

        dist_rec_html = ""
        for cat, val in rec_cat_dist.sort_values(ascending=False).items():
            pct_rec = (val / rec_tot_dist * 100) if rec_tot_dist > 0 else 0
            cor_bar = C["sage"]
            dist_rec_html += (
                f'<div style="margin-bottom:10px;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                f'<span style="font-size:11px;font-weight:600;color:#1a1714;">{cat}</span>'
                f'<span style="font-size:10px;color:#8a7a60;">{pct_rec:.1f}% · {fmt_k(val)}</span>'
                f'</div>'
                f'<div style="height:6px;background:#f0ece8;border-radius:3px;'
                f'box-shadow:inset 0 1px 2px rgba(26,23,20,0.08);">'
                f'<div style="height:100%;width:{pct_rec:.1f}%;'
                f'background:linear-gradient(180deg,rgba(255,255,255,0.5) 0%,{cor_bar} 35%,{cor_bar} 70%,rgba(0,0,0,0.2) 100%);'
                f'border-radius:3px;box-shadow:0 1px 2px rgba(26,23,20,0.15);"></div>'
                f'</div></div>'
            )
        if not dist_rec_html:
            dist_rec_html = '<div style="font-size:11px;color:#a09080;">Sem receitas no período.</div>'

        st.markdown(
            f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:16px;padding:16px 18px;'
            f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
            f'inset 0 1px 0 rgba(255,255,255,0.9);'
            f'border:1px solid #e0dbd4;">'
            f'{dist_rec_html}</div>', unsafe_allow_html=True)

        # Gap entre as duas caixas para não sobrescrever em caso de muitas categorias
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # ── Distribuição de Despesas (caixa inferior) ─────────────────────────
        sec("Distribuição de Despesas")
        desp_cat = df_mes_cat[df_mes_cat["tipo"]=="Despesa"].groupby("categoria")["valor_abs"].sum()
        rec_tot  = df_mes_cat[df_mes_cat["tipo"]=="Receita"]["valor_abs"].sum()

        dist_html = ""
        for cat, val in desp_cat.sort_values(ascending=False).items():
            pct_rec  = (val / rec_tot * 100) if rec_tot > 0 else 0
            pct_desp = (val / desp_cat.sum() * 100) if desp_cat.sum() > 0 else 0
            cor_bar  = C["terra"] if pct_rec > 30 else C["amber"] if pct_rec > 15 else C["sage"]
            dist_html += (
                f'<div style="margin-bottom:10px;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                f'<span style="font-size:11px;font-weight:600;color:#1a1714;">{cat}</span>'
                f'<span style="font-size:10px;color:#8a7a60;">{pct_rec:.1f}% · {fmt_k(val)}</span>'
                f'</div>'
                f'<div style="height:6px;background:#f0ece8;border-radius:3px;'
                f'box-shadow:inset 0 1px 2px rgba(26,23,20,0.08);">'
                f'<div style="height:100%;width:{pct_desp:.1f}%;'
                f'background:linear-gradient(180deg,rgba(255,255,255,0.5) 0%,{cor_bar} 35%,{cor_bar} 70%,rgba(0,0,0,0.2) 100%);'
                f'border-radius:3px;box-shadow:0 1px 2px rgba(26,23,20,0.15);"></div>'
                f'</div></div>'
            )
        if not dist_html:
            dist_html = '<div style="font-size:11px;color:#a09080;">Sem despesas no período.</div>'

        st.markdown(
            f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:16px;padding:16px 18px;'
            f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
            f'inset 0 1px 0 rgba(255,255,255,0.9);'
            f'border:1px solid #e0dbd4;">'
            f'{dist_html}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FLUXO DE CAIXA
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    df_mes   = df[df["data"].dt.to_period("M").isin(periodos_sel)].copy()
    df_mes["valor_abs"] = df_mes["valor"].abs()
    df_daily = df_mes.groupby(["data","tipo"])["valor_abs"].sum().reset_index()
    dr       = pd.date_range(df_mes["data"].min(), df_mes["data"].max())
    rec_d    = df_daily[df_daily["tipo"]=="Receita"].set_index("data")["valor_abs"].reindex(dr, fill_value=0)
    desp_d   = df_daily[df_daily["tipo"]=="Despesa"].set_index("data")["valor_abs"].reindex(dr, fill_value=0)
    saldo    = (rec_d - desp_d).cumsum()

    c1, c2, c3 = st.columns(3)
    fc_icones = {"Total Entradas":"↑","Total Saídas":"↓","Saldo Final":"="}
    fc_bgs    = {C["sage"]:"#edf7eb", C["terra"]:"#fdecea", C["amber"]:"#fdf8ee"}
    for col, lbl, val, cor in [
        (c1,"Total Entradas",rec_d.sum(),  C["sage"]),
        (c2,"Total Saídas",  desp_d.sum(), C["terra"]),
        (c3,"Saldo Final",   saldo.iloc[-1] if len(saldo)>0 else 0, C["amber"]),
    ]:
        with col:
            bg_icon = fc_bgs.get(cor,"#f5f1eb")
            icone   = fc_icones.get(lbl,"◎")
            st.markdown(
                f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:18px;padding:18px 18px 14px;'
                f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
                f'inset 0 1px 0 rgba(255,255,255,0.9);'
                f'border:1px solid #e8e3dc;position:relative;overflow:hidden;">'
                f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:{cor};border-radius:18px 18px 0 0;opacity:.5;"></div>'
                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'
                f'<div style="width:34px;height:34px;border-radius:50%;'
                f'background:radial-gradient(circle at 35% 32%,#ffffff 0%,{bg_icon} 40%,{cor} 100%);'
                f'box-shadow:inset -2px -3px 5px rgba(26,23,20,0.18),'
                f'inset 2px 2px 4px rgba(255,255,255,0.7),'
                f'0 3px 7px rgba(26,23,20,0.15);'
                f'display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:800;color:#fff;'
                f'text-shadow:0 1px 2px rgba(26,23,20,0.3);">{icone}</div>'
                f'<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#a09080;">{lbl}</div>'
                f'</div>'
                f'<div style="font-size:24px;font-weight:800;color:{cor};line-height:1;letter-spacing:-.5px;">{fmt_brl(val)}</div>'
                f'</div>', unsafe_allow_html=True)

    sec("Entradas e Saídas Diárias")
    fig2 = go.Figure()
    fig2.add_scatter(x=dr, y=rec_d.values, name="Receita", fill="tozeroy",
                     fillcolor="rgba(143,166,138,0.15)", line=dict(color=C["sage"],width=2.5),
                     marker=dict(size=6,color=C["sage"],line=dict(color="#fff",width=2)))
    fig2.add_scatter(x=dr, y=desp_d.values, name="Despesa", fill="tozeroy",
                     fillcolor="rgba(201,133,110,0.12)", line=dict(color=C["terra"],width=2.5),
                     marker=dict(size=6,color=C["terra"],line=dict(color="#fff",width=2)))
    fig2.update_layout(**PLOT, height=260)
    st.plotly_chart(fig2, use_container_width=True)

    sec("Saldo Acumulado")
    saldo_final = saldo.iloc[-1] if len(saldo) > 0 else 0
    cor_s  = C["sage"] if saldo_final >= 0 else C["terra"]
    fill_s = "rgba(143,166,138,0.1)" if saldo_final >= 0 else "rgba(201,133,110,0.1)"

    fig3 = go.Figure()
    fig3.add_scatter(x=dr, y=saldo.values, fill="tozeroy", fillcolor=fill_s,
                     line=dict(color=cor_s,width=3))
    fig3.add_hline(y=0, line_dash="dot", line_color="#e0dbd4", line_width=1)
    if len(dr) > 0:
        fig3.add_scatter(x=[dr[-1]], y=[saldo_final], mode="markers+text", showlegend=False,
                         text=[fmt_brl(saldo_final)], textposition="top center",
                         textfont=dict(size=10,color=cor_s),
                         marker=dict(size=14,color=cor_s,line=dict(color="#fff",width=3)))
    hoje_local = datetime.today()
    if pd.Period(hoje_local, freq="M") in periodos_sel and len(periodos_sel)==1 and len(dr) > 1:
        fim_mes = pd.Period(hoje_local, freq="M").to_timestamp(how="end")
        proj_d  = pd.date_range(dr[-1]+timedelta(days=1), fim_mes, freq="D")
        media_d = (rec_d - desp_d).mean()
        proj_v  = [saldo_final + media_d*(i+1) for i in range(len(proj_d))]
        if len(proj_d) > 0:
            fig3.add_scatter(x=proj_d, y=proj_v, name="Projeção", mode="lines",
                             line=dict(color=C["amber"],width=2,dash="dot"))
    fig3.update_layout(**PLOT, height=220)
    fig3.update_yaxes(tickformat=",.0f", tickprefix="R$ ")
    st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CATEGORIAS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    df_mes = df[df["data"].dt.to_period("M").isin(periodos_sel)].copy()
    df_mes["valor_abs"] = df_mes["valor"].abs()
    rec_tot_mes  = df_mes[df_mes["tipo"]=="Receita"]["valor_abs"].sum()
    desp_tot_mes = df_mes[df_mes["tipo"]=="Despesa"]["valor_abs"].sum()

    # ── LINHA 1: Receita por Categoria (full-width, barra horizontal) ─────────
    sec("Receita por Categoria")
    rec_cat = (
        df_mes[df_mes["tipo"]=="Receita"]
        .groupby("categoria")["valor_abs"].sum()
        .sort_values(ascending=True)
    )
    rec_pcts = (rec_cat / rec_tot_mes * 100) if rec_tot_mes > 0 else rec_cat * 0
    altura_rec = max(60 + 36*len(rec_cat), 180)   # altura dinâmica conforme nº de categorias

    fig_rec = go.Figure(go.Bar(
        x=rec_cat.values, y=rec_cat.index, orientation="h",
        marker=dict(color=C["sage"], opacity=0.9,
                    line=dict(width=1.5, color="#fff"), cornerradius=4),
        text=[f"{p:.1f}%" for p in rec_pcts.values],
        textposition="outside",
        textfont=dict(size=11, color="#1a1714", family="Outfit"),
    ))
    fig_rec.update_layout(**{k:v for k,v in PLOT.items() if k!="xaxis"}, height=altura_rec)
    max_rec = rec_cat.values.max() if len(rec_cat) > 0 else 1
    fig_rec.update_xaxes(tickformat=",.0f", tickprefix="R$ ",
                         range=[0, max_rec * 1.18])
    st.plotly_chart(fig_rec, use_container_width=True)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # ── LINHA 2: Despesa por Categoria + Saldo por Categoria (donut) ─────────
    col_l, col_r = st.columns(2)

    with col_l:
        sec("Despesa por Categoria")
        desp_cat = df_mes[df_mes["tipo"]=="Despesa"].groupby("categoria")["valor_abs"].sum().sort_values()
        desp_pcts = (desp_cat / desp_tot_mes * 100) if desp_tot_mes > 0 else desp_cat * 0
        altura_desp = max(60 + 36*len(desp_cat), 200)

        fig_d = go.Figure(go.Bar(
            x=desp_cat.values, y=desp_cat.index, orientation="h",
            marker=dict(color=C["terra"], opacity=0.9,
                        line=dict(width=1.5, color="#fff"), cornerradius=4),
            text=[f"{p:.1f}%" for p in desp_pcts.values],
            textposition="outside",
            textfont=dict(size=10, color="#1a1714", family="Outfit"),
        ))
        fig_d.update_layout(**{k:v for k,v in PLOT.items() if k!="xaxis"}, height=altura_desp)
        max_desp = desp_cat.values.max() if len(desp_cat) > 0 else 1
        fig_d.update_xaxes(tickformat=",.0f", range=[0, max_desp * 1.18])
        st.plotly_chart(fig_d, use_container_width=True)

    with col_r:
        sec("Saldo por Categoria")
        # Saldo por categoria: só considera categorias com saldo positivo (receita > despesa)
        # Como rec_cat e desp_cat normalmente são categorias diferentes (entradas vs saídas),
        # exibimos as categorias de receita (que representam saldo positivo para o negócio).
        # Caso o usuário tenha categorias mistas, somamos receita - despesa por categoria.
        saldo_por_cat = {}
        for cat in df_mes["categoria"].unique():
            r = df_mes[(df_mes["categoria"]==cat)&(df_mes["tipo"]=="Receita")]["valor_abs"].sum()
            d = df_mes[(df_mes["categoria"]==cat)&(df_mes["tipo"]=="Despesa")]["valor_abs"].sum()
            saldo = r - d
            if saldo > 0:
                saldo_por_cat[cat] = saldo

        if saldo_por_cat:
            cats_saldo = list(saldo_por_cat.keys())
            vals_saldo = list(saldo_por_cat.values())
            altura_donut = max(altura_desp, 260)

            fig_s = go.Figure(go.Pie(
                labels=cats_saldo, values=vals_saldo, hole=0.58,
                marker=dict(colors=C["seq"], line=dict(color="#fff", width=2.5)),
                textfont=dict(family="Outfit", size=11, color="#fff"),
                textinfo="percent",
                pull=[0.02]*len(cats_saldo),
                hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
            ))
            fig_s.update_layout(
                **{k:v for k,v in PLOT.items() if k not in ["xaxis","yaxis","legend"]},
                height=altura_donut,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5,
                            xanchor="left", x=1.02,
                            font=dict(size=10, family="Outfit"),
                            bgcolor="rgba(255,255,255,0)",
                            bordercolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig_s, use_container_width=True)
        else:
            st.markdown(
                '<div style="font-size:11px;color:#a09080;padding:20px;text-align:center;">'
                'Nenhuma categoria com saldo positivo no período.</div>',
                unsafe_allow_html=True)

    # ── LINHA 3: Custo por categoria como % da receita ────────────────────────
    sec("Custo por Categoria como % da Receita")
    desp_pct = df_mes[df_mes["tipo"]=="Despesa"].groupby("categoria")["valor_abs"].sum()
    desp_pct = (desp_pct/rec_tot_mes*100).sort_values() if rec_tot_mes > 0 else desp_pct
    cores_pct = [C["terra"] if v>30 else C["amber"] if v>15 else C["sage"] for v in desp_pct.values]
    fig_pct = go.Figure(go.Bar(
        x=desp_pct.values, y=desp_pct.index, orientation="h",
        marker=dict(color=cores_pct, opacity=0.9,
                    line=dict(width=1.5, color="#fff"), cornerradius=4),
        text=[f"{v:.1f}%" for v in desp_pct.values], textposition="outside",
        textfont=dict(size=10,color="#8a7a60"),
    ))
    fig_pct.add_vline(x=30, line_dash="dot", line_color="rgba(201,133,110,0.33)", line_width=1,
                      annotation_text="30% alerta", annotation_font_color="#c9856e",
                      annotation_font_size=9)
    fig_pct.update_layout(**{k:v for k,v in PLOT.items() if k!="xaxis"}, height=260)
    fig_pct.update_xaxes(ticksuffix="%", range=[0, max(desp_pct.values)*1.3] if len(desp_pct)>0 else [0,100])
    st.plotly_chart(fig_pct, use_container_width=True)

    # ── LINHA 4: Evolução das Principais Categorias (top 3 de RECEITA) ────────
    sec("Evolução das Principais Categorias")
    top_cats_rec = (
        df_mes[df_mes["tipo"]=="Receita"]
        .groupby("categoria")["valor_abs"].sum()
        .sort_values(ascending=False)
        .head(3).index.tolist()
    )
    df_evol  = df[df["tipo"]=="Receita"].copy()
    df_evol["valor_abs"] = df_evol["valor"].abs()
    df_evol["mes"]       = df_evol["data"].dt.to_period("M").astype(str)
    df_evol = df_evol[df_evol["categoria"].isin(top_cats_rec)]
    df_evol = df_evol.groupby(["mes","categoria"])["valor_abs"].sum().reset_index()

    fig_ev = go.Figure()
    ev_c_rec = [C["sage"], C["amber"], C["slate"]]
    for i, cat in enumerate(top_cats_rec):
        sub = df_evol[df_evol["categoria"]==cat].sort_values("mes")
        fig_ev.add_scatter(x=sub["mes"], y=sub["valor_abs"], name=cat, mode="lines+markers",
                           line=dict(color=ev_c_rec[i], width=2.5),
                           marker=dict(size=10, color=ev_c_rec[i],
                                       line=dict(color="#fff", width=2.5)))
    fig_ev.update_layout(**PLOT, height=240)
    fig_ev.update_yaxes(tickformat=",.0f", tickprefix="R$ ")
    st.plotly_chart(fig_ev, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ALERTAS IA (reformulada com análise automática + chat)
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:

    # ── Dados do mês ──────────────────────────────────────────────────────────
    df_mes         = df[df["data"].dt.to_period("M").isin(periodos_sel)].copy()
    df_mes["valor_abs"] = df_mes["valor"].abs()
    desp_cat_mes   = df_mes[df_mes["tipo"]=="Despesa"].groupby("categoria")["valor_abs"].sum()
    rec_total_mes  = df_mes[df_mes["tipo"]=="Receita"]["valor_abs"].sum()
    top3_desp      = [(c, v/rec_total_mes*100) for c,v in desp_cat_mes.nlargest(3).items()] if rec_total_mes > 0 else []

    resumo_financeiro = (
        f"Período: {mes_label} | Receita: {fmt_brl(M['receita'])} ({M['pct_rec']:+.1f}% vs anterior, YoY: {M['pct_rec_yoy']:+.1f}%)\n"
        f"Despesa: {fmt_brl(M['despesa'])} ({M['pct_desp']:+.1f}%) | Saldo: {fmt_brl(M['lucro'])} | Margem: {M['margem']:.1f}%\n"
        f"Comprometimento: {M['comprometimento']:.1f}% | Ticket Médio: {fmt_brl(M['ticket'])} ({M['n_trans']} transações)\n"
        f"Projeção: {fmt_brl(M['projecao'])} | Média 3m: {fmt_brl(M['media3'])}\n"
        f"Top despesas: {', '.join([f'{c}: {p:.1f}%' for c,p in top3_desp])}"
    )

    # ── Alertas automáticos (regras) ──────────────────────────────────────────
    sec("Alertas Automáticos")
    alertas = []
    if M["margem"] < 20:
        alertas.append(("danger", f"⚠ Margem líquida em {M['margem']:.1f}% — abaixo do saudável (>20%). Revise as despesas."))
    elif M["margem"] > 40:
        alertas.append(("ok", f"✦ Margem líquida em {M['margem']:.1f}% — excelente performance!"))
    if M["comprometimento"] > 80:
        alertas.append(("danger", f"🔴 {M['comprometimento']:.1f}% da receita comprometida — situação crítica."))
    elif M["comprometimento"] > 60:
        alertas.append(("warn", f"◈ {M['comprometimento']:.1f}% da receita em despesas — acima do ideal (60%)."))
    if M["pct_desp"] > 15:
        alertas.append(("warn", f"📈 Despesas cresceram {M['pct_desp']:.1f}% vs mês anterior."))
    if rec_total_mes > 0:
        for cat, val in desp_cat_mes.items():
            pct = val/rec_total_mes*100
            if pct > 30:
                alertas.append(("warn", f"◉ '{cat}' consome {pct:.1f}% da receita — alto peso."))
    if M["lucro"] < 0:
        alertas.append(("danger", f"✕ Resultado negativo: {fmt_brl(M['lucro'])}. Ação imediata recomendada."))
    if M["pct_rec_yoy"] < -10:
        alertas.append(("warn", f"📉 Receita {M['pct_rec_yoy']:.1f}% abaixo do mesmo mês do ano passado."))
    elif M["pct_rec_yoy"] > 20:
        alertas.append(("ok", f"📈 Receita {M['pct_rec_yoy']:.1f}% acima do mesmo mês do ano passado!"))
    if M["projecao"] != M["lucro"]:
        t = "ok" if M["projecao"] >= 0 else "danger"
        alertas.append((t, f"🔮 Projeção de encerramento: {fmt_brl(M['projecao'])}."))

    for tipo, msg in alertas:
        mk_alert(msg, tipo)
    if not alertas:
        mk_alert("✦ Nenhum alerta crítico identificado para o período selecionado.", "ok")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── Configuração da API ───────────────────────────────────────────────────
    api_key = ""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        api_conectada = True
    except:
        api_conectada = False

    # ── Análise IA automática do mês ──────────────────────────────────────────
    sec("Análise IA do Mês")

    col_api_info, col_api_key = st.columns([2,1])
    with col_api_info:
        if api_conectada:
            st.markdown(
                f'<div style="background:#f0f7ef;border:1px solid #e3f0e2;border-radius:12px;'
                f'padding:10px 14px;font-size:12px;color:#1a5e2a;display:flex;align-items:center;gap:8px;">'
                f'<span style="font-size:14px;">✓</span> Gemini API conectada via secrets</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="background:#fdf8ee;border:1px solid #f5ecce;border-radius:12px;'
                f'padding:10px 14px;font-size:12px;color:#7d4e00;display:flex;align-items:center;gap:8px;">'
                f'<span style="font-size:14px;">◈</span> Insira sua chave Gemini para ativar a IA '
                f'— obtenha grátis em <b>aistudio.google.com</b></div>',
                unsafe_allow_html=True)
    with col_api_key:
        if not api_conectada:
            api_key = st.text_input("Chave Gemini API", type="password",
                                    placeholder="AIza...", label_visibility="collapsed",
                                    key="api_key_input")

    # Inicializa histórico do chat
    if "chat_ia" not in st.session_state:
        st.session_state.chat_ia = []
    if "analise_auto_feita" not in st.session_state:
        st.session_state.analise_auto_feita = {}

    chave_analise = f"{mes_label}_{bool(api_key)}"

    # Análise automática ao abrir o mês (só roda 1x por mês/sessão)
    if api_key and chave_analise not in st.session_state.analise_auto_feita:
        with st.spinner("🤖 Gerando análise automática do mês..."):
            try:
                analise_texto = chamar_gemini(
                    api_key,
                    system_prompt=(
                        "Você é um analista financeiro especializado em pequenos negócios e criadores de conteúdo digital. "
                        "Seja direto, objetivo e use dados concretos. Máximo 4 parágrafos curtos. "
                        "Formato: primeiro parágrafo = diagnóstico geral, segundo = pontos de atenção, "
                        "terceiro = oportunidades, quarto = recomendação principal. Português brasileiro."
                    ),
                    user_prompt=f"Faça a análise completa deste período:\n\n{resumo_financeiro}"
                )
                st.session_state.analise_auto_feita[chave_analise] = analise_texto
            except Exception as e:
                st.session_state.analise_auto_feita[chave_analise] = f"[Erro ao gerar análise: {e}]"

    if chave_analise in st.session_state.analise_auto_feita:
        texto_analise = st.session_state.analise_auto_feita[chave_analise]
        # Se for erro, exibe alerta — não renderiza como análise
        if texto_analise.startswith("[Erro") or texto_analise.startswith("⏳"):
            tipo_alerta = "warn" if "⏳" in texto_analise else "danger"
            mk_alert(texto_analise.strip("[]"), tipo_alerta)
            if st.button("🔄 Tentar novamente", key="btn_retry_analise"):
                del st.session_state.analise_auto_feita[chave_analise]
                st.rerun()
        else:
            paragrafos = [p.strip() for p in texto_analise.split("\n") if p.strip()]
            icones_par = ["📊","⚠️","✨","🎯"]
            titulos_par = ["Diagnóstico","Atenção","Oportunidades","Recomendação"]
            cards_html = ""
            for i, par in enumerate(paragrafos[:4]):
                ic = icones_par[i] if i < len(icones_par) else "•"
                ti = titulos_par[i] if i < len(titulos_par) else ""
                cards_html += (
                    f'<div style="background:#f8f5f1;border-radius:12px;padding:12px 14px;margin-bottom:8px;">'
                    f'<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
                    f'color:#a09080;margin-bottom:6px;">{ic} {ti}</div>'
                    f'<div style="font-size:13px;line-height:1.65;color:#1a1714;">{par}</div>'
                    f'</div>'
                )
            if cards_html:
                st.markdown(
                    f'<div style="background:#fff;border-radius:18px;padding:20px;'
                    f'box-shadow:0 2px 16px rgba(26,23,20,0.07);border:1px solid #e8e3dc;">'
                    f'{cards_html}</div>', unsafe_allow_html=True)
    elif not api_key:
        mk_alert("Configure sua chave Gemini acima para gerar a análise automática do período.", "warn")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── Chat com dados financeiros ────────────────────────────────────────────
    sec("Chat com seus Dados")

    # Exibe histórico do chat
    for msg in st.session_state.chat_ia:
        role_icon  = "🧑" if msg["role"] == "user" else "🤖"
        role_label = "Você" if msg["role"] == "user" else "Gemini IA"
        bg_msg = "#f8f5f1" if msg["role"] == "user" else "#fff"
        border_msg = "#e8e3dc" if msg["role"] == "user" else "#e0dbd4"
        st.markdown(
            f'<div style="background:{bg_msg};border:1px solid {border_msg};border-radius:14px;'
            f'padding:12px 16px;margin-bottom:8px;">'
            f'<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
            f'color:#a09080;margin-bottom:6px;">{role_icon} {role_label}</div>'
            f'<div style="font-size:13px;line-height:1.65;color:#1a1714;">{msg["content"]}</div>'
            f'</div>', unsafe_allow_html=True)

    # Input e envio
    if api_key:
        col_inp, col_btn = st.columns([4,1])
        with col_inp:
            pergunta = st.text_input(
                "Pergunta", label_visibility="collapsed",
                placeholder="Ex: Por que minha margem caiu? Como reduzir despesas?",
                key="chat_input"
            )
        with col_btn:
            enviar = st.button("Enviar →", key="btn_enviar_chat")

        if enviar and pergunta.strip():
            st.session_state.chat_ia.append({"role":"user","content":pergunta.strip()})
            with st.spinner("Analisando..."):
                try:
                    # Monta histórico como texto para o Gemini
                    historico_txt = "\n".join([
                        f"{'Usuário' if m['role']=='user' else 'Assistente'}: {m['content']}"
                        for m in st.session_state.chat_ia[:-1]
                    ])
                    prompt_chat = (
                        f"Contexto financeiro:\n{resumo_financeiro}\n\n"
                        + (f"Histórico:\n{historico_txt}\n\n" if historico_txt else "")
                        + f"Usuário: {pergunta.strip()}"
                    )
                    resposta = chamar_gemini(
                        api_key,
                        system_prompt=(
                            "Analista financeiro para pequenos negócios e criadores de conteúdo digital. "
                            "Respostas diretas, objetivas, máximo 3 parágrafos. Use os dados fornecidos. "
                            "Português brasileiro. Nunca invente dados."
                        ),
                        user_prompt=prompt_chat
                    )
                    st.session_state.chat_ia.append({"role":"assistant","content":resposta})
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        col_lp, col_btn_lp = st.columns([4,1])
        with col_btn_lp:
            if st.button("Limpar chat", key="btn_limpar"):
                st.session_state.chat_ia = []
                st.rerun()
    else:
        mk_alert("Configure sua chave Gemini acima para ativar o chat.", "warn")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — METAS MENSAIS (nova)
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:

    # Inicializa metas — carrega do Supabase se disponível, senão usa defaults
    if "metas" not in st.session_state:
        metas_salvas = st.session_state.get("metas_usuario")
        if metas_salvas:
            st.session_state.metas = metas_salvas
        else:
            st.session_state.metas = {
                "receita":        M["receita"] * 1.1,
                "margem":         30.0,
                "comprometimento":60.0,
            }
            df_cats_d = df[df["tipo"]=="Despesa"]["categoria"].unique().tolist()
            for cat in df_cats_d:
                avg_cat = (
                    df[df["tipo"]=="Despesa"]
                    .groupby(["data"])
                    .apply(lambda x: x[x["categoria"]==cat]["valor"].abs().sum())
                    .mean()
                )
                st.session_state.metas[f"cat_{cat}"] = round(float(avg_cat) * 1.0, 2)

    sec("Configurar Metas do Mês")

    with st.expander("⚙️ Editar Metas", expanded=False):
        st.markdown(
            '<div style="font-size:11px;color:#8a7a60;margin-bottom:12px;">'
            'Defina os limites e objetivos para o período selecionado.</div>',
            unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        with cm1:
            nova_meta_rec = st.number_input(
                "Meta de Receita (R$)", min_value=0.0,
                value=float(st.session_state.metas["receita"]),
                step=100.0, format="%.2f", key="inp_meta_rec"
            )
        with cm2:
            nova_meta_mgm = st.number_input(
                "Meta de Margem (%)", min_value=0.0, max_value=100.0,
                value=float(st.session_state.metas["margem"]),
                step=0.5, format="%.1f", key="inp_meta_mgm"
            )
        with cm3:
            nova_meta_comp = st.number_input(
                "Limite Comprometimento (%)", min_value=0.0, max_value=100.0,
                value=float(st.session_state.metas["comprometimento"]),
                step=1.0, format="%.1f", key="inp_meta_comp"
            )

        # Metas por categoria
        st.markdown('<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#a09080;margin:14px 0 8px;">Limite por Categoria de Despesa</div>', unsafe_allow_html=True)
        df_cats_d_lista = sorted(df[df["tipo"]=="Despesa"]["categoria"].unique().tolist())
        cols_cat = st.columns(min(len(df_cats_d_lista), 3))
        novas_metas_cat = {}
        for i, cat in enumerate(df_cats_d_lista):
            with cols_cat[i % 3]:
                val_atual = st.session_state.metas.get(f"cat_{cat}", 500.0)
                novas_metas_cat[cat] = st.number_input(
                    cat, min_value=0.0, value=float(val_atual),
                    step=50.0, format="%.2f", key=f"meta_cat_{cat}"
                )

        if st.button("💾 Salvar Metas", key="btn_salvar_metas"):
            st.session_state.metas["receita"]        = nova_meta_rec
            st.session_state.metas["margem"]         = nova_meta_mgm
            st.session_state.metas["comprometimento"]= nova_meta_comp
            for cat, val in novas_metas_cat.items():
                st.session_state.metas[f"cat_{cat}"] = val
            ok = salvar_metas(st.session_state.usuario, st.session_state.metas)
            st.success("✅ Metas salvas na nuvem!") if ok else st.warning("Metas salvas localmente, mas não sincronizadas.")

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    sec("Progresso das Metas")

    # ── Cards de metas principais ─────────────────────────────────────────────
    mm1, mm2, mm3 = st.columns(3)

    def meta_card(col, titulo, atual, meta, unidade="R$", inverso=False):
        """
        Renderiza um card de progresso de meta.
        inverso=True: menor é melhor (ex: comprometimento)
        """
        if meta <= 0:
            pct = 0.0
        else:
            pct = min((atual / meta) * 100, 200.0)

        if inverso:
            # Verde se abaixo da meta, vermelho se ultrapassou
            atingida = atual <= meta
            cor_bar  = C["sage"] if atingida else C["terra"]
            cor_val  = C["sage"] if atingida else C["terra"]
            status   = "✓ Dentro do limite" if atingida else "✕ Limite excedido"
            st_tipo  = "ok" if atingida else "danger"
        else:
            atingida = atual >= meta
            cor_bar  = C["sage"] if atingida else (C["amber"] if pct >= 80 else C["slate"])
            cor_val  = C["sage"] if atingida else C["ink"]
            status   = "✓ Meta atingida!" if atingida else f"{pct:.0f}% da meta"
            st_tipo  = "ok" if atingida else ("warn" if pct >= 80 else "neutral")

        val_fmt  = f"{atual:.1f}{unidade}" if unidade != "R$" else fmt_brl(atual)
        meta_fmt = f"{meta:.1f}{unidade}" if unidade != "R$" else fmt_brl(meta)
        bar_pct  = min(pct, 100)

        with col:
            st.markdown(
                f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:18px;padding:18px;'
                f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
                f'inset 0 1px 0 rgba(255,255,255,0.9);'
                f'border:1px solid #e8e3dc;'
                f'position:relative;overflow:hidden;">'
                f'<div style="position:absolute;top:0;left:0;right:0;height:3px;'
                f'background:{cor_bar};border-radius:18px 18px 0 0;opacity:.7;"></div>'
                f'<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
                f'color:#a09080;margin-bottom:12px;">{titulo}</div>'
                f'<div style="font-size:26px;font-weight:800;color:{cor_val};line-height:1;letter-spacing:-.5px;">{val_fmt}</div>'
                f'<div style="font-size:10px;color:#a09080;margin-top:4px;">meta: {meta_fmt}</div>'
                f'<div style="height:8px;background:#f0ece8;border-radius:4px;margin:12px 0 8px;position:relative;'
                f'box-shadow:inset 0 1px 2px rgba(26,23,20,0.08);">'
                f'<div style="height:100%;width:{bar_pct:.1f}%;'
                f'background:linear-gradient(180deg,rgba(255,255,255,0.55) 0%,{cor_bar} 35%,{cor_bar} 70%,rgba(0,0,0,0.2) 100%);'
                f'border-radius:4px;transition:width .4s;'
                f'box-shadow:0 1px 3px rgba(26,23,20,0.18);"></div>'
                f'</div>'
                f'{badge(status, st_tipo)}'
                f'</div>', unsafe_allow_html=True)

    meta_card(mm1, "Receita",         M["receita"],         st.session_state.metas["receita"],         "R$",  False)
    meta_card(mm2, "Margem Líquida",  M["margem"],          st.session_state.metas["margem"],          "%",   False)
    meta_card(mm3, "Comprometimento", M["comprometimento"], st.session_state.metas["comprometimento"], "%",   True)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    sec("Limites por Categoria de Despesa")

    # Calcula gastos reais do mês por categoria
    df_mes_metas = df[df["data"].dt.to_period("M").isin(periodos_sel)].copy()
    df_mes_metas["valor_abs"] = df_mes_metas["valor"].abs()
    gastos_cat = df_mes_metas[df_mes_metas["tipo"]=="Despesa"].groupby("categoria")["valor_abs"].sum()

    df_cats_ordenadas = sorted(df[df["tipo"]=="Despesa"]["categoria"].unique().tolist())
    cols_meta_cat = st.columns(min(len(df_cats_ordenadas), 3))
    for i, cat in enumerate(df_cats_ordenadas):
        gasto  = gastos_cat.get(cat, 0.0)
        limite = st.session_state.metas.get(f"cat_{cat}", 500.0)
        pct_c  = min((gasto / limite * 100) if limite > 0 else 0, 200.0)
        ok_c   = gasto <= limite
        cor_c  = C["sage"] if ok_c else C["terra"]
        with cols_meta_cat[i % 3]:
            st.markdown(
                f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:14px;padding:14px 16px;'
                f'box-shadow:0 8px 22px rgba(26,23,20,0.08),0 3px 8px rgba(26,23,20,0.05),'
                f'inset 0 1px 0 rgba(255,255,255,0.9);'
                f'border:1px solid #e8e3dc;margin-bottom:10px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">'
                f'<span style="font-size:12px;font-weight:700;color:#1a1714;">{cat}</span>'
                f'{badge("OK","ok") if ok_c else badge("⚠ Excedido","danger")}'
                f'</div>'
                f'<div style="font-size:18px;font-weight:800;color:{cor_c};line-height:1;">{fmt_brl(gasto)}</div>'
                f'<div style="font-size:10px;color:#a09080;margin-top:2px;">limite: {fmt_brl(limite)}</div>'
                f'<div style="height:6px;background:#f0ece8;border-radius:3px;margin-top:10px;'
                f'box-shadow:inset 0 1px 2px rgba(26,23,20,0.08);">'
                f'<div style="height:100%;width:{min(pct_c,100):.1f}%;'
                f'background:linear-gradient(180deg,rgba(255,255,255,0.5) 0%,{cor_c} 35%,{cor_c} 70%,rgba(0,0,0,0.2) 100%);'
                f'border-radius:3px;box-shadow:0 1px 2px rgba(26,23,20,0.15);"></div>'
                f'</div>'
                f'<div style="font-size:9px;color:#a09080;margin-top:4px;text-align:right;">{pct_c:.0f}% do limite</div>'
                f'</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — TRANSAÇÕES
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    sec("Todas as Transações")

    df_mes_full = df[df["data"].dt.to_period("M").isin(periodos_sel)].copy()
    df_mes_full["valor_abs"] = df_mes_full["valor"].abs()

    # Linha de filtros + export
    col_f1, col_f2, col_f3, col_exp = st.columns([1, 1, 1, 1])
    with col_f1: tipo_f = st.selectbox("Tipo",       ["Todos","Receita","Despesa"])
    with col_f2: cat_f  = st.selectbox("Categoria",  ["Todas"]+sorted(df_mes_full["categoria"].unique().tolist()))
    with col_f3: ordem  = st.selectbox("Ordenar",    ["Data ↓","Valor ↓","Valor ↑"])
    with col_exp:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        excel_bytes = gerar_excel(df, M, periodos_sel, mes_label)
        st.download_button(
            label="📥 Excel",
            data=excel_bytes,
            file_name=f"mkpro_{mes_label}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_excel_trans"
        )

    df_v = df_mes_full.copy()
    if tipo_f != "Todos":  df_v = df_v[df_v["tipo"]==tipo_f]
    if cat_f  != "Todas":  df_v = df_v[df_v["categoria"]==cat_f]

    ordem_config = {
        "Data ↓":  ("data",      False),
        "Valor ↓": ("valor_abs", False),
        "Valor ↑": ("valor_abs", True),
    }
    col_sort, asc = ordem_config[ordem]
    df_v = df_v.sort_values(col_sort, ascending=asc)
    df_v["Valor"] = df_v["valor_abs"].apply(fmt_brl)
    df_v["Data"]  = df_v["data"].dt.strftime("%d/%m/%Y")

    st.dataframe(
        df_v[["Data","tipo","categoria","Valor"]].rename(columns={"tipo":"Tipo","categoria":"Categoria"}),
        use_container_width=True, height=420, hide_index=True)
    st.caption(f"{len(df_v)} transações · Total: {fmt_brl(df_v['valor_abs'].sum())}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — VISÃO ANUAL
# ═══════════════════════════════════════════════════════════════════════════════
with tab7:
    df_a = df.copy()
    df_a["valor_abs"] = df_a["valor"].abs()
    df_a["ano"]  = df_a["data"].dt.year.astype(str)
    df_a["mes"]  = df_a["data"].dt.to_period("M").astype(str)
    df_a["mnum"] = df_a["data"].dt.month

    anos_disp = sorted(df_a["ano"].unique(), reverse=True)

    sec("Filtro")
    fa1, fa2, fa3 = st.columns([2,2,1])
    with fa1: anos_sel = st.multiselect("Anos", options=anos_disp, default=anos_disp[:3], key="anos_a")
    with fa2: gran = st.radio("Granularidade", ["Anual","Mensal"], horizontal=True, key="gran_a")
    with fa3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if anos_sel:
            anos_str = "_".join(sorted(anos_sel))
            excel_anual = gerar_excel(df_a[df_a["ano"].isin(anos_sel)].rename(columns={"ano":"_ano"}), M, periodos_sel, mes_label)
            st.download_button(
                label="📥 Excel",
                data=excel_anual,
                file_name=f"mkpro_anual_{anos_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_excel_anual"
            )

    if not anos_sel: st.warning("Selecione ao menos um ano."); st.stop()
    df_f = df_a[df_a["ano"].isin(anos_sel)]

    rec_t   = df_f[df_f["tipo"]=="Receita"]["valor_abs"].sum()
    desp_t  = df_f[df_f["tipo"]=="Despesa"]["valor_abs"].sum()
    lucro_t = rec_t - desp_t
    tk_a    = rec_t / max(len(df_f[df_f["tipo"]=="Receita"]),1)

    k1,k2,k3,k4 = st.columns(4)
    an_cfgs = [
        (k1,"Receita Total", fmt_brl(rec_t),  C["sage"],  "#edf7eb","↑"),
        (k2,"Despesa Total", fmt_brl(desp_t), C["terra"], "#fdecea","↓"),
        (k3,"Saldo Líquido", fmt_brl(lucro_t),C["amber"] if lucro_t>=0 else C["terra"],
            "#fdf8ee" if lucro_t>=0 else "#fdecea","="),
        (k4,"Ticket Médio",  fmt_brl(tk_a),   C["slate"], "#eef2f8","◎"),
    ]
    for col, lbl, val, cor, bg_ic, icone in an_cfgs:
        with col:
            st.markdown(
                f'<div style="background:linear-gradient(160deg,#ffffff 0%,#fbfaf8 100%);border-radius:18px;padding:18px 18px 14px;'
                f'box-shadow:0 12px 32px rgba(26,23,20,0.10),0 4px 12px rgba(26,23,20,0.06),'
                f'inset 0 1px 0 rgba(255,255,255,0.9);'
                f'border:1px solid #e8e3dc;position:relative;overflow:hidden;">'
                f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:{cor};border-radius:18px 18px 0 0;opacity:.5;"></div>'
                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'
                f'<div style="width:34px;height:34px;border-radius:50%;'
                f'background:radial-gradient(circle at 35% 32%,#ffffff 0%,{bg_ic} 40%,{cor} 100%);'
                f'box-shadow:inset -2px -3px 5px rgba(26,23,20,0.18),'
                f'inset 2px 2px 4px rgba(255,255,255,0.7),'
                f'0 3px 7px rgba(26,23,20,0.15);'
                f'display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:800;color:#fff;'
                f'text-shadow:0 1px 2px rgba(26,23,20,0.3);">{icone}</div>'
                f'<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#a09080;">{lbl}</div>'
                f'</div>'
                f'<div style="font-size:22px;font-weight:800;color:{cor};line-height:1;letter-spacing:-.5px;">{val}</div>'
                f'<div style="font-size:10px;color:#a09080;margin-top:4px;font-weight:500;">período selecionado</div>'
                f'</div>', unsafe_allow_html=True)

    ev_c = [C["amber"],C["sage"],C["terra"],C["slate"],C["slate"]]

    sec("Receita · Despesa · Saldo")
    if gran == "Anual":
        grp = df_f.groupby(["ano","tipo"])["valor_abs"].sum().reset_index()
        ex  = sorted(anos_sel)
        rv  = [grp[(grp["ano"]==a)&(grp["tipo"]=="Receita")]["valor_abs"].sum() for a in ex]
        dv  = [grp[(grp["ano"]==a)&(grp["tipo"]=="Despesa")]["valor_abs"].sum() for a in ex]
    else:
        grp = df_f.groupby(["mes","tipo"])["valor_abs"].sum().reset_index()
        ex  = sorted(grp["mes"].unique())
        rv  = [grp[(grp["mes"]==m)&(grp["tipo"]=="Receita")]["valor_abs"].sum() for m in ex]
        dv  = [grp[(grp["mes"]==m)&(grp["tipo"]=="Despesa")]["valor_abs"].sum() for m in ex]
    sv = [r-d for r,d in zip(rv,dv)]

    fig_an = go.Figure()
    fig_an.add_bar(name="Receita", x=ex, y=rv,
                   width=0.28 if gran=="Anual" else None,
                   marker=dict(color=C["sage"],opacity=0.9,
                               line=dict(width=1.5, color="#fff"),cornerradius=4))
    fig_an.add_bar(name="Despesa", x=ex, y=dv,
                   width=0.28 if gran=="Anual" else None,
                   marker=dict(color=C["terra"],opacity=0.9,
                               line=dict(width=1.5, color="#fff"),cornerradius=4))
    fig_an.add_scatter(name="Saldo", x=ex, y=sv, mode="lines+markers",
                       line=dict(color=C["amber"],width=3),
                       marker=dict(size=12,color=C["amber"],line=dict(color="#fff",width=2.5)))
    fig_an.update_layout(**PLOT, barmode="group", height=300)
    fig_an.update_yaxes(tickformat=",.0f", tickprefix="R$ ")
    st.plotly_chart(fig_an, use_container_width=True)

    an1, an2 = st.columns(2)
    with an1:
        sec("Saldo Acumulado")
        fig_ac = go.Figure()
        for i, ano in enumerate(sorted(anos_sel)):
            df_ano = df_f[df_f["ano"]==ano].copy()
            cor = ev_c[i % len(ev_c)]
            if gran == "Anual":
                r = df_ano[df_ano["tipo"]=="Receita"]["valor_abs"].sum()
                d = df_ano[df_ano["tipo"]=="Despesa"]["valor_abs"].sum()
                fig_ac.add_scatter(x=[ano], y=[r-d], name=ano, mode="markers+text",
                                   marker=dict(size=20,color=cor,line=dict(color="#fff",width=3.5)),
                                   text=[fmt_k(r-d)], textposition="top center",
                                   textfont=dict(size=10,color=cor))
            else:
                gm = df_ano.groupby(["mnum","mes","tipo"])["valor_abs"].sum().reset_index()
                acum,xs,ys = 0,[],[]
                for mn in sorted(gm["mnum"].unique()):
                    sub  = gm[gm["mnum"]==mn]
                    acum += (sub[sub["tipo"]=="Receita"]["valor_abs"].sum() -
                             sub[sub["tipo"]=="Despesa"]["valor_abs"].sum())
                    xs.append(sub["mes"].iloc[0] if not sub.empty else f"{ano}-{mn:02d}")
                    ys.append(acum)
                fig_ac.add_scatter(x=xs, y=ys, name=ano, mode="lines+markers",
                                   line=dict(color=cor,width=2.5),
                                   marker=dict(size=9,color=cor,line=dict(color="#fff",width=2.5)),
                                   fill="tozeroy",
                                   fillcolor=f"rgba({int(cor[1:3],16)},{int(cor[3:5],16)},{int(cor[5:7],16)},0.07)")
        fig_ac.add_hline(y=0, line_dash="dot", line_color="#e0dbd4", line_width=1)
        fig_ac.update_layout(**PLOT, height=260)
        fig_ac.update_yaxes(tickformat=",.0f", tickprefix="R$ ")
        st.plotly_chart(fig_ac, use_container_width=True)

    with an2:
        sec("Margem Líquida %")
        fig_mg = go.Figure()
        for i, ano in enumerate(sorted(anos_sel)):
            df_ano = df_f[df_f["ano"]==ano]
            cor    = ev_c[i % len(ev_c)]
            if gran == "Anual":
                r  = df_ano[df_ano["tipo"]=="Receita"]["valor_abs"].sum()
                d  = df_ano[df_ano["tipo"]=="Despesa"]["valor_abs"].sum()
                mg = ((r-d)/r*100) if r>0 else 0
                fig_mg.add_bar(x=[ano], y=[mg], name=ano,
                               marker=dict(color=cor,opacity=0.9,
                                           line=dict(width=1.5, color="#fff"),cornerradius=4))
            else:
                gm = df_ano.groupby(["mnum","mes","tipo"])["valor_abs"].sum().reset_index()
                xs,ys = [],[]
                for mn in sorted(gm["mnum"].unique()):
                    sub = gm[gm["mnum"]==mn]
                    r   = sub[sub["tipo"]=="Receita"]["valor_abs"].sum()
                    d   = sub[sub["tipo"]=="Despesa"]["valor_abs"].sum()
                    ys.append(((r-d)/r*100) if r>0 else 0)
                    xs.append(sub["mes"].iloc[0] if not sub.empty else f"{ano}-{mn:02d}")
                fig_mg.add_scatter(x=xs, y=ys, name=ano, mode="lines+markers",
                                   line=dict(color=cor,width=2.5),
                                   marker=dict(size=9,color=cor,line=dict(color="#fff",width=2.5)))
        fig_mg.add_hline(y=20, line_dash="dot", line_color="rgba(143,166,138,0.33)", line_width=1,
                         annotation_text="Meta 20%", annotation_font_color="#8fa68a",
                         annotation_font_size=9)
        fig_mg.update_layout(**PLOT, barmode="group", height=260)
        fig_mg.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig_mg, use_container_width=True)

    sec("Resumo por Ano")
    rows_r = []
    for ano in sorted(anos_sel):
        d  = df_f[df_f["ano"]==ano]
        r  = d[d["tipo"]=="Receita"]["valor_abs"].sum()
        dp = d[d["tipo"]=="Despesa"]["valor_abs"].sum()
        l  = r - dp
        rows_r.append({
            "Ano":     ano,
            "Receita": fmt_brl(r),
            "Despesa": fmt_brl(dp),
            "Saldo":   fmt_brl(l),
            "Margem":  f"{(l/r*100):.1f}%" if r>0 else "—",
            "Ticket":  fmt_brl(r/max(len(d[d["tipo"]=="Receita"]),1))
        })
    st.dataframe(pd.DataFrame(rows_r), use_container_width=True, hide_index=True,
                 height=min(50+35*len(rows_r), 300))

    # ── Export final consolidado ───────────────────────────────────────────────
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    sec("Exportar Relatório Completo")
    col_ex1, col_ex2, _ = st.columns([1,1,2])
    with col_ex1:
        excel_full = gerar_excel(df, M, periodos_sel, mes_label)
        st.download_button(
            label="📊 Baixar Excel — Mês Atual",
            data=excel_full,
            file_name=f"mkpro_relatorio_{mes_label}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_excel_full"
        )
    with col_ex2:
        # CSV completo de todos os dados
        csv_bytes = df.copy().assign(
            data=df["data"].dt.strftime("%d/%m/%Y"),
            valor=df["valor"].abs()
        ).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📄 Baixar CSV — Todos os Dados",
            data=csv_bytes,
            file_name=f"mkpro_completo.csv",
            mime="text/csv",
            key="dl_csv_full"
        )
