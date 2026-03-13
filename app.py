import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Peugeot · Base de Clientes",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600&family=Barlow+Condensed:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }
.stApp { background-color: #0d0d14; }
[data-testid="stSidebar"] { background-color: #111119 !important; border-right: 1px solid #1e1e2e; }
[data-testid="stSidebar"] * { color: #a0a0b8 !important; }
.dash-header {
    background: #0a0a12; border: 1px solid #1e1e35; border-radius: 8px;
    padding: 20px 28px; margin-bottom: 4px;
    display: flex; align-items: center; justify-content: space-between;
}
.dash-title {
    font-family: 'Barlow Condensed', sans-serif; font-size: 26px;
    font-weight: 700; letter-spacing: 3px; color: #e8e8f5;
    text-transform: uppercase; margin: 0;
}
.dash-sub { font-size: 11px; color: #0088cc; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
.dash-badge {
    background: rgba(0,136,204,0.12); border: 1px solid #0088cc;
    color: #0088cc; font-size: 10px; padding: 4px 12px;
    border-radius: 3px; letter-spacing: 1px; text-transform: uppercase;
}
.kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 4px; }
.kpi-card { background: #111119; border: 1px solid #1e1e30; border-radius: 8px; padding: 16px 20px; }
.kpi-label { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: #555570; margin-bottom: 6px; }
.kpi-value { font-family: 'Barlow Condensed', sans-serif; font-size: 34px; font-weight: 600; color: #e8e8f5; line-height: 1; letter-spacing: -1px; }
.kpi-sub { font-size: 10px; color: #444460; margin-top: 4px; }
.kpi-bar { height: 2px; background: #1e1e30; border-radius: 1px; margin-top: 12px; }
.kpi-bar-fill { height: 100%; background: #0088cc; border-radius: 1px; }
.section-title {
    font-family: 'Barlow Condensed', sans-serif; font-size: 13px;
    font-weight: 600; letter-spacing: 2px; text-transform: uppercase;
    color: #e8e8f5; margin-bottom: 0;
}
</style>
""", unsafe_allow_html=True)

# ── Constantes ─────────────────────────────────────────────────────────────────
SHEET_ID = "1P3qFgAygEzKjc2P8jn0inJLji6h5IQEBwB68lx1SwL8"
GID      = "1933435937"
CSV_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# Base layout sin margin — se pasa siempre por separado para evitar conflictos
BASE = dict(
    paper_bgcolor="#111119",
    plot_bgcolor="#111119",
    font=dict(family="Barlow, sans-serif", color="#a0a0b8", size=11),
    xaxis=dict(gridcolor="#1e1e30", linecolor="#1e1e30", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#1e1e30", linecolor="#1e1e30", tickfont=dict(size=10)),
    colorway=["#0088cc","#5794f2","#00aadd","#73bf69","#fade2a","#ff780a"],
)

def layout(height=200, ml=12, mr=50, mt=8, mb=8, **extra):
    return dict(**BASE, height=height, margin=dict(l=ml, r=mr, t=mt, b=mb), **extra)

# ── Carga de datos ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [c.strip() for c in df.columns]
    if "am_modelo" in df.columns and "am_modelocl" not in df.columns:
        df = df.rename(columns={"am_modelo": "am_modelocl"})
    if "vp_f_compra" in df.columns:
        df["vp_f_compra"] = pd.to_datetime(df["vp_f_compra"], errors="coerce", dayfirst=True)
        df["mes_compra"]  = df["vp_f_compra"].dt.to_period("M").astype(str)
        df["año_compra"]  = df["vp_f_compra"].dt.year
    if "empresa" in df.columns:
        df["tipo_cliente"] = df["empresa"].apply(
            lambda x: "Corporativo" if pd.notna(x) and str(x).strip() not in ("", "nan") else "Particular"
        )
    else:
        df["tipo_cliente"] = "Particular"
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"No se pudo cargar la Google Sheet. Verificá que sea pública. Error: {e}")
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🦁 Peugeot CRM")
    st.caption(f"{len(df_raw):,} registros · refresco cada 5 min")
    if st.button("🔄 Forzar actualización"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.markdown("#### Filtros")

    modelos_opts = ["Todos"] + sorted(df_raw["am_modelocl"].dropna().unique().tolist())
    modelo_sel = st.selectbox("Modelo", modelos_opts)

    if "cl_dir_provincia" in df_raw.columns:
        prov_opts = ["Todas"] + sorted(df_raw["cl_dir_provincia"].dropna().unique().tolist())
        provincia_sel = st.selectbox("Provincia", prov_opts)
    else:
        provincia_sel = "Todas"

    tipo_sel = st.selectbox("Tipo de cliente", ["Todos", "Particular", "Corporativo"])

    fecha_rango = ()
    if "vp_f_compra" in df_raw.columns:
        fechas = df_raw["vp_f_compra"].dropna()
        if len(fechas):
            f_min = fechas.min().date()
            f_max = fechas.max().date()
            fecha_rango = st.date_input("Rango de compra", value=(f_min, f_max),
                                        min_value=f_min, max_value=f_max)

    st.markdown("---")
    st.markdown("#### Vistas")
    pagina = st.radio("", ["General", "Por modelo", "Por provincia", "Empresas"],
                      label_visibility="collapsed")

# ── Filtros ────────────────────────────────────────────────────────────────────
df = df_raw.copy()
if modelo_sel != "Todos":
    df = df[df["am_modelocl"] == modelo_sel]
if provincia_sel != "Todas" and "cl_dir_provincia" in df.columns:
    df = df[df["cl_dir_provincia"] == provincia_sel]
if tipo_sel != "Todos":
    df = df[df["tipo_cliente"] == tipo_sel]
if len(fecha_rango) == 2 and "vp_f_compra" in df.columns:
    df = df[(df["vp_f_compra"].dt.date >= fecha_rango[0]) &
            (df["vp_f_compra"].dt.date <= fecha_rango[1])]

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">Peugeot Argentina</div>
    <div class="dash-sub">Base de Clientes · Dashboard CRM</div>
  </div>
  <div class="dash-badge">Vista: {pagina}</div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

NO_MB = {"displayModeBar": False}

# ══════════════════════════════════════════════════════════════════════════════
# GENERAL
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "General":

    total_clientes = df["cl_k_cliente"].nunique() if "cl_k_cliente" in df.columns else len(df)
    total_compras  = len(df)
    promedio       = round(total_compras / total_clientes, 2) if total_clientes > 0 else 0

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Clientes únicos</div>
        <div class="kpi-value">{total_clientes:,}</div>
        <div class="kpi-sub">COUNT DISTINCT · cl_k_cliente</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:100%"></div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total de compras</div>
        <div class="kpi-value">{total_compras:,}</div>
        <div class="kpi-sub">COUNT · vp_f_compra</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:75%"></div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Promedio por cliente</div>
        <div class="kpi-value">{promedio}</div>
        <div class="kpi-sub">compras / clientes únicos</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:50%"></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_tabla, col_charts = st.columns([3, 2], gap="medium")

    with col_tabla:
        st.markdown('<p class="section-title">Registro de clientes</p>', unsafe_allow_html=True)
        cols_show = [c for c in ["cl_apellido","cl_nombre","cl_numero_doc","am_modelocl",
                                  "cl_dir_localidad","cl_dir_provincia","empresa","vp_f_compra"]
                     if c in df.columns]
        rename_map = {
            "cl_apellido":"Apellido","cl_nombre":"Nombre","cl_numero_doc":"N° Doc",
            "am_modelocl":"Modelo","cl_dir_localidad":"Localidad",
            "cl_dir_provincia":"Provincia","empresa":"Empresa","vp_f_compra":"F. Compra"
        }
        tabla = df[cols_show].rename(columns=rename_map).head(500)
        if "F. Compra" in tabla.columns:
            tabla["F. Compra"] = tabla["F. Compra"].dt.strftime("%d/%m/%Y")
        st.dataframe(tabla, use_container_width=True, hide_index=True, height=320)

    with col_charts:
        st.markdown('<p class="section-title">Compras por modelo</p>', unsafe_allow_html=True)
        mod_df = df.groupby("am_modelocl").size().reset_index(name="n").sort_values("n", ascending=True)
        fig = go.Figure(go.Bar(
            x=mod_df["n"], y=mod_df["am_modelocl"], orientation="h",
            marker_color="#0088cc", marker_line_width=0,
            text=mod_df["n"], textposition="outside",
            textfont=dict(size=10, color="#a0a0b8"),
        ))
        fig.update_layout(**layout(180, mr=60))
        st.plotly_chart(fig, use_container_width=True, config=NO_MB)

        if "cl_dir_provincia" in df.columns:
            st.markdown('<p class="section-title">Clientes por provincia</p>', unsafe_allow_html=True)
            prov_df = (df.groupby("cl_dir_provincia")["cl_k_cliente"]
                       .nunique().reset_index(name="n")
                       .sort_values("n", ascending=True).tail(8))
            fig2 = go.Figure(go.Bar(
                x=prov_df["n"], y=prov_df["cl_dir_provincia"], orientation="h",
                marker_color="#5794f2", marker_line_width=0,
                text=prov_df["n"], textposition="outside",
                textfont=dict(size=10, color="#a0a0b8"),
            ))
            fig2.update_layout(**layout(220, mr=60))
            st.plotly_chart(fig2, use_container_width=True, config=NO_MB)

    if "mes_compra" in df.columns:
        st.markdown('<p class="section-title">Compras por mes</p>', unsafe_allow_html=True)
        time_df = df.groupby("mes_compra").size().reset_index(name="n").sort_values("mes_compra")
        fig3 = go.Figure(go.Bar(
            x=time_df["mes_compra"], y=time_df["n"],
            marker_color="#0088cc", marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Compras: %{y}<extra></extra>",
        ))
        fig3.update_layout(**layout(160, mr=12))
        st.plotly_chart(fig3, use_container_width=True, config=NO_MB)

# ══════════════════════════════════════════════════════════════════════════════
# POR MODELO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Por modelo":

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        mod_pie = df.groupby("am_modelocl").size().reset_index(name="n")
        fig = go.Figure(go.Pie(
            labels=mod_pie["am_modelocl"], values=mod_pie["n"], hole=0.5,
            marker=dict(colors=["#0088cc","#5794f2","#00aadd","#73bf69","#fade2a","#ff780a","#e02f44"]),
            textfont=dict(size=11),
        ))
        fig.update_layout(**layout(280, mr=12, mt=36),
                          showlegend=True,
                          title=dict(text="Distribución de compras", font=dict(size=12), x=0),
                          legend=dict(font=dict(size=11)))
        st.plotly_chart(fig, use_container_width=True, config=NO_MB)

    with col2:
        mod_uni = (df.groupby("am_modelocl")["cl_k_cliente"]
                   .nunique().reset_index(name="n").sort_values("n", ascending=False))
        fig2 = go.Figure(go.Bar(
            x=mod_uni["am_modelocl"], y=mod_uni["n"],
            marker_color="#0088cc", marker_line_width=0,
            text=mod_uni["n"], textposition="outside",
            textfont=dict(size=10, color="#a0a0b8"),
        ))
        fig2.update_layout(**layout(280, mr=12, mt=36),
                           title=dict(text="Clientes únicos por modelo", font=dict(size=12), x=0))
        st.plotly_chart(fig2, use_container_width=True, config=NO_MB)

    if "mes_compra" in df.columns:
        st.markdown('<p class="section-title">Tendencia mensual por modelo</p>', unsafe_allow_html=True)
        trend = df.groupby(["mes_compra","am_modelocl"]).size().reset_index(name="n")
        fig3 = px.line(trend, x="mes_compra", y="n", color="am_modelocl",
                       color_discrete_sequence=["#0088cc","#5794f2","#00aadd","#73bf69","#fade2a","#ff780a"])
        fig3.update_traces(line_width=2)
        fig3.update_layout(**layout(240, mr=12, mb=50),
                           legend=dict(font=dict(size=11), orientation="h", y=-0.25))
        st.plotly_chart(fig3, use_container_width=True, config=NO_MB)

    st.markdown('<p class="section-title">Resumen por modelo</p>', unsafe_allow_html=True)
    resumen = (df.groupby("am_modelocl")
               .agg(Compras=("vp_f_compra","count"),
                    Clientes_unicos=("cl_k_cliente","nunique"),
                    Provincias=("cl_dir_provincia","nunique"))
               .reset_index()
               .rename(columns={"am_modelocl":"Modelo","Clientes_unicos":"Clientes únicos"})
               .sort_values("Compras", ascending=False))
    st.dataframe(resumen, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# POR PROVINCIA
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Por provincia":

    if "cl_dir_provincia" not in df.columns:
        st.warning("No se encontró la columna cl_dir_provincia en tus datos.")
    else:
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            prov_df = (df.groupby("cl_dir_provincia")
                       .agg(clientes=("cl_k_cliente","nunique"))
                       .reset_index().sort_values("clientes", ascending=True))
            fig = go.Figure(go.Bar(
                x=prov_df["clientes"], y=prov_df["cl_dir_provincia"], orientation="h",
                marker_color="#0088cc", marker_line_width=0,
                text=prov_df["clientes"], textposition="outside",
                textfont=dict(size=10, color="#a0a0b8"),
            ))
            fig.update_layout(**layout(340, ml=12, mr=60, mt=36, mb=12),
                              title=dict(text="Clientes únicos por provincia", font=dict(size=12), x=0))
            st.plotly_chart(fig, use_container_width=True, config=NO_MB)

        with col2:
            if "cl_dir_localidad" in df.columns:
                loc_df = (df.groupby("cl_dir_localidad")["cl_k_cliente"]
                          .nunique().reset_index(name="n")
                          .sort_values("n", ascending=False).head(12)
                          .sort_values("n", ascending=True))
                fig2 = go.Figure(go.Bar(
                    x=loc_df["n"], y=loc_df["cl_dir_localidad"], orientation="h",
                    marker_color="#5794f2", marker_line_width=0,
                    text=loc_df["n"], textposition="outside",
                    textfont=dict(size=10, color="#a0a0b8"),
                ))
                fig2.update_layout(**layout(340, ml=12, mr=60, mt=36, mb=12),
                                   title=dict(text="Top localidades", font=dict(size=12), x=0))
                st.plotly_chart(fig2, use_container_width=True, config=NO_MB)

        st.markdown('<p class="section-title">Modelo más comprado por provincia</p>', unsafe_allow_html=True)
        top_mod = (df.groupby(["cl_dir_provincia","am_modelocl"]).size()
                   .reset_index(name="n").sort_values("n", ascending=False)
                   .groupby("cl_dir_provincia").first().reset_index()
                   .rename(columns={"cl_dir_provincia":"Provincia",
                                     "am_modelocl":"Modelo más comprado","n":"Compras"}))
        st.dataframe(top_mod, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# EMPRESAS
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Empresas":

    df_corp = df[df["tipo_cliente"] == "Corporativo"].copy()
    total_corp   = df_corp["cl_k_cliente"].nunique() if "cl_k_cliente" in df_corp.columns else len(df_corp)
    total_emp    = df_corp["empresa"].nunique() if "empresa" in df_corp.columns else 0
    compras_corp = len(df_corp)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Clientes corporativos</div>
        <div class="kpi-value" style="color:#fade2a">{total_corp:,}</div>
        <div class="kpi-sub">COUNT DISTINCT · cl_k_cliente</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:100%;background:#fade2a"></div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Empresas únicas</div>
        <div class="kpi-value" style="color:#fade2a">{total_emp:,}</div>
        <div class="kpi-sub">COUNT DISTINCT · empresa</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:60%;background:#fade2a"></div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Compras corporativas</div>
        <div class="kpi-value" style="color:#fade2a">{compras_corp:,}</div>
        <div class="kpi-sub">COUNT · vp_f_compra</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:75%;background:#fade2a"></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown('<p class="section-title">Registro de empresas</p>', unsafe_allow_html=True)
        if "empresa" in df_corp.columns and len(df_corp) > 0:
            emp_tab = (df_corp.groupby("empresa")
                       .agg(contactos=("cl_k_cliente","nunique"),
                            compras=("vp_f_compra","count"),
                            provincia=("cl_dir_provincia", lambda x: x.mode()[0] if len(x) > 0 else ""),
                            modelo=("am_modelocl", lambda x: x.mode()[0] if len(x) > 0 else ""),
                            ultima_compra=("vp_f_compra","max"))
                       .reset_index()
                       .rename(columns={"empresa":"Empresa","contactos":"Contactos",
                                         "compras":"Compras","provincia":"Provincia",
                                         "modelo":"Modelo top","ultima_compra":"Última compra"})
                       .sort_values("Compras", ascending=False))
            emp_tab["Última compra"] = emp_tab["Última compra"].dt.strftime("%d/%m/%Y")
            st.dataframe(emp_tab, use_container_width=True, hide_index=True, height=320)
        else:
            st.info("No hay clientes corporativos con los filtros actuales.")

    with col2:
        if len(df_corp) > 0:
            st.markdown('<p class="section-title">Modelos preferidos</p>', unsafe_allow_html=True)
            mc = df_corp.groupby("am_modelocl").size().reset_index(name="n").sort_values("n", ascending=True)
            fig = go.Figure(go.Bar(
                x=mc["n"], y=mc["am_modelocl"], orientation="h",
                marker_color="#fade2a", marker_line_width=0,
                text=mc["n"], textposition="outside",
                textfont=dict(size=10, color="#a0a0b8"),
            ))
            fig.update_layout(**layout(200, mr=60))
            st.plotly_chart(fig, use_container_width=True, config=NO_MB)

            if "cl_dir_provincia" in df_corp.columns:
                st.markdown('<p class="section-title">Por provincia</p>', unsafe_allow_html=True)
                pc = (df_corp.groupby("cl_dir_provincia")["cl_k_cliente"]
                      .nunique().reset_index(name="n").sort_values("n", ascending=True).tail(6))
                fig2 = go.Figure(go.Bar(
                    x=pc["n"], y=pc["cl_dir_provincia"], orientation="h",
                    marker_color="#c8a800", marker_line_width=0,
                    text=pc["n"], textposition="outside",
                    textfont=dict(size=10, color="#a0a0b8"),
                ))
                fig2.update_layout(**layout(200, mr=60))
                st.plotly_chart(fig2, use_container_width=True, config=NO_MB)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-size:10px;color:#333350;letter-spacing:1px;'>"
    "PEUGEOT ARGENTINA · DASHBOARD CRM · BASE DE CLIENTES</p>",
    unsafe_allow_html=True
)
