import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Peugeot - Base de Clientes",
    page_icon="https://www.peugeot.com.ar/content/dam/peugeot/master/home/peugeot-logo-alt.png",
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
.kpi-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 4px; }
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
GID      = "1111388380"
CSV_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

SIN_DATO = "Sin dato"

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

    # Reemplazar nulls con "Sin dato" en columnas categóricas clave
    for col in ["am_modelocl", "cl_dir_provincia", "cl_dir_localidad", "Gender"]:
        if col in df.columns:
            df[col] = df[col].fillna(SIN_DATO).replace("", SIN_DATO).astype(str).str.strip()
            df[col] = df[col].replace("nan", SIN_DATO)

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
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px 0">
      <img src="https://www.peugeot.com.ar/content/dam/peugeot/master/home/peugeot-logo-alt.png" width="80"><br>
      <span style="font-family:'Barlow Condensed',sans-serif;font-size:15px;font-weight:700;letter-spacing:3px;color:#e8e8f5;text-transform:uppercase">Peugeot</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-size:12px;color:#666680;margin-top:2px'>{len(df_raw):,} registros</p>", unsafe_allow_html=True)
    if st.button("🔄 Forzar actualización (del sheet)"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.markdown("#### Filtros")

    modelos_opts = ["Todos"] + sorted(df_raw["am_modelocl"].unique().tolist())
    modelo_sel = st.selectbox("Modelo", modelos_opts)

    if "cl_dir_provincia" in df_raw.columns:
        prov_opts = ["Todas"] + sorted(df_raw["cl_dir_provincia"].unique().tolist())
        provincia_sel = st.selectbox("Provincia", prov_opts)
    else:
        provincia_sel = "Todas"

    tipo_sel = st.selectbox("Tipo de cliente", ["Todos", "Particular", "Corporativo"])

    if "Gender" in df_raw.columns:
        gender_opts = ["Todos"] + sorted(df_raw["Gender"].unique().tolist())
        gender_sel = st.selectbox("Género", gender_opts)
    else:
        gender_sel = "Todos"

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
    pagina = st.radio("", ["General", "Por modelo", "Por provincia", "Empresas", "Género"],
                      label_visibility="collapsed")

# ── Filtros ────────────────────────────────────────────────────────────────────
df = df_raw.copy()
if modelo_sel != "Todos":
    df = df[df["am_modelocl"] == modelo_sel]
if provincia_sel != "Todas" and "cl_dir_provincia" in df.columns:
    df = df[df["cl_dir_provincia"] == provincia_sel]
if tipo_sel != "Todos":
    df = df[df["tipo_cliente"] == tipo_sel]
if gender_sel != "Todos" and "Gender" in df.columns:
    df = df[df["Gender"] == gender_sel]
if len(fecha_rango) == 2 and "vp_f_compra" in df.columns:
    df = df[(df["vp_f_compra"].dt.date >= fecha_rango[0]) &
            (df["vp_f_compra"].dt.date <= fecha_rango[1])]

# ── Contraseña ────────────────────────────────────────────────────────────────────
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("### 🔒 Acceso restringido")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if pwd == "FCB_2026!":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        st.stop()

check_password()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">Stellantis: Peugeot</div>
    <div class="dash-sub">Base de Clientes</div>
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
    total_compras  = len(df_raw) if modelo_sel == "Todos" and provincia_sel == "Todas" and tipo_sel == "Todos" else len(df)
    promedio = round(len(df) / total_clientes, 2) if total_clientes > 0 else 0

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Clientes únicos</div>
        <div class="kpi-value">{total_clientes:,}</div>
        <div class="kpi-sub">Suma de DNI's únicos registrados</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:100%"></div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total de compras</div>
        <div class="kpi-value">{total_compras:,}</div>
        <div class="kpi-sub">Todos los registros</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:75%"></div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Promedio por cliente</div>
        <div class="kpi-value">{promedio}</div>
        <div class="kpi-sub">Total compras / Clientes únicos</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:50%"></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_anio, col_prov = st.columns(2, gap="medium")

    with col_anio:
        st.markdown('<p class="section-title">Compras por año</p>', unsafe_allow_html=True)
        anio_df = df.groupby("año_compra").size().reset_index(name="n").sort_values("n", ascending=True)
        fig = go.Figure(go.Bar(
            x=anio_df["n"], y=anio_df["año_compra"].astype(str), orientation="h",
            marker_color="#0088cc", marker_line_width=0,
            text=anio_df["n"], textposition="outside",
            textfont=dict(size=10, color="#a0a0b8"),
        ))
        fig.update_layout(**layout(240, mr=60))
        st.plotly_chart(fig, use_container_width=True, config=NO_MB)

    with col_prov:
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
            fig2.update_layout(**layout(240, mr=60))
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

    st.markdown('<p class="section-title">Registro de clientes</p>', unsafe_allow_html=True)
    cols_show = [c for c in ["cl_apellido","cl_nombre","cl_numero_doc","am_modelocl",
                              "cl_dir_localidad","cl_dir_provincia","empresa","vp_f_compra","Gender"]
                 if c in df.columns]
    rename_map = {
        "cl_apellido":"Apellido","cl_nombre":"Nombre","cl_numero_doc":"N° Doc",
        "am_modelocl":"Modelo","cl_dir_localidad":"Localidad",
        "cl_dir_provincia":"Provincia","empresa":"Empresa","vp_f_compra":"F. Compra","Gender":"Género"
    }
    tabla = df[cols_show].rename(columns=rename_map).head(500)
    if "F. Compra" in tabla.columns:
        tabla["F. Compra"] = tabla["F. Compra"].dt.strftime("%d/%m/%Y")
    st.dataframe(tabla, use_container_width=True, hide_index=True, height=320)

# ══════════════════════════════════════════════════════════════════════════════
# POR MODELO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Por modelo":

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        # fillna ya aplicado en load_data, pero por si acaso
        mod_pie = df.groupby("am_modelocl").size().reset_index(name="n")
        colors  = ["#0088cc","#5794f2","#00aadd","#73bf69","#fade2a","#ff780a","#e02f44","#555570"]
        # "Sin dato" siempre en gris
        label_colors = ["#555570" if l == SIN_DATO else colors[i % len(colors)]
                        for i, l in enumerate(mod_pie["am_modelocl"])]
        fig = go.Figure(go.Pie(
            labels=mod_pie["am_modelocl"].astype(str), values=mod_pie["n"], hole=0.5,
            marker=dict(colors=label_colors),
            textfont=dict(size=11),
        ))
        fig.update_layout(**layout(280, mr=12, mt=36))
        fig.update_layout(showlegend=True,
                          title=dict(text="Distribución de compras", font=dict(size=12), x=0),
                          legend=dict(font=dict(size=11)))
        st.plotly_chart(fig, use_container_width=True, config=NO_MB)

    with col2:
        mod_uni = (df.groupby("am_modelocl")["cl_k_cliente"]
                   .nunique().reset_index(name="n").sort_values("n", ascending=False))
        bar_colors = ["#555570" if m == SIN_DATO else "#0088cc" for m in mod_uni["am_modelocl"]]
        fig2 = go.Figure(go.Bar(
            x=mod_uni["am_modelocl"].astype(str), y=mod_uni["n"],
            marker_color=bar_colors, marker_line_width=0,
            text=mod_uni["n"], textposition="outside",
            textfont=dict(size=10, color="#a0a0b8"),
        ))
        fig2.update_layout(**layout(280, mr=12, mt=36))
        fig2.update_layout(
            title=dict(text="Clientes únicos por modelo", font=dict(size=12), x=0),
            xaxis=dict(type="category", gridcolor="#1e1e30", linecolor="#1e1e30"),
        )
        st.plotly_chart(fig2, use_container_width=True, config=NO_MB)

    if "mes_compra" in df.columns:
        st.markdown('<p class="section-title">Tendencia mensual por modelo</p>', unsafe_allow_html=True)
        trend = df.groupby(["mes_compra","am_modelocl"]).size().reset_index(name="n")
        fig3 = px.line(trend, x="mes_compra", y="n", color="am_modelocl",
                       color_discrete_sequence=["#0088cc","#5794f2","#00aadd","#73bf69","#fade2a","#ff780a","#555570"])
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
            bar_colors = ["#555570" if p == SIN_DATO else "#0088cc" for p in prov_df["cl_dir_provincia"]]
            fig = go.Figure(go.Bar(
                x=prov_df["clientes"], y=prov_df["cl_dir_provincia"], orientation="h",
                marker_color=bar_colors, marker_line_width=0,
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
                bar_colors2 = ["#555570" if l == SIN_DATO else "#5794f2" for l in loc_df["cl_dir_localidad"]]
                fig2 = go.Figure(go.Bar(
                    x=loc_df["n"], y=loc_df["cl_dir_localidad"], orientation="h",
                    marker_color=bar_colors2, marker_line_width=0,
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

    df_corp = df[pd.to_numeric(df["empresa"], errors="coerce") == 1].copy()
    total_corp   = df_corp["cl_k_cliente"].nunique() if "cl_k_cliente" in df_corp.columns else len(df_corp)
    compras_corp = len(df_corp)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Clientes de empresa</div>
        <div class="kpi-value" style="color:#fade2a">{total_corp:,}</div>
        <div class="kpi-sub">Suma de DNI's únicos registrados (Con empresa=1)</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:100%;background:#fade2a"></div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total compras empresas</div>
        <div class="kpi-value" style="color:#fade2a">{compras_corp:,}</div>
        <div class="kpi-sub">Todos los registros (Con empresa=1)</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:75%;background:#fade2a"></div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">% sobre total</div>
        <div class="kpi-value" style="color:#fade2a">{round(compras_corp/len(df)*100,1) if len(df)>0 else 0}%</div>
        <div class="kpi-sub">Compras empresa / Total compras</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{round(compras_corp/len(df)*100,1) if len(df)>0 else 0}%;background:#fade2a"></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown('<p class="section-title">Modelos preferidos</p>', unsafe_allow_html=True)
        mc = df_corp.groupby("am_modelocl").size().reset_index(name="n").sort_values("n", ascending=False)
        bar_colors = ["#555570" if m == SIN_DATO else "#fade2a" for m in mc["am_modelocl"]]
        fig = go.Figure(go.Bar(
            x=mc["am_modelocl"].astype(str), y=mc["n"],
            marker_color=bar_colors, marker_line_width=0,
            text=mc["n"], textposition="outside",
            textfont=dict(size=10, color="#a0a0b8"),
        ))
        fig.update_layout(**layout(280, mr=12))
        fig.update_layout(xaxis=dict(type="category", gridcolor="#1e1e30", linecolor="#1e1e30"))
        st.plotly_chart(fig, use_container_width=True, config=NO_MB)

    with col2:
        if "cl_dir_provincia" in df_corp.columns:
            st.markdown('<p class="section-title">Por provincia</p>', unsafe_allow_html=True)
            pc = (df_corp.groupby("cl_dir_provincia")["cl_k_cliente"]
                  .nunique().reset_index(name="n").sort_values("n", ascending=True).tail(8))
            bar_colors2 = ["#555570" if p == SIN_DATO else "#c8a800" for p in pc["cl_dir_provincia"]]
            fig2 = go.Figure(go.Bar(
                x=pc["n"], y=pc["cl_dir_provincia"], orientation="h",
                marker_color=bar_colors2, marker_line_width=0,
                text=pc["n"], textposition="outside",
                textfont=dict(size=10, color="#a0a0b8"),
            ))
            fig2.update_layout(**layout(280, mr=80))
            st.plotly_chart(fig2, use_container_width=True, config=NO_MB)

    st.markdown('<p class="section-title">Registro de clientes de empresa</p>', unsafe_allow_html=True)
    cols_show = [c for c in ["cl_apellido","cl_nombre","cl_numero_doc","am_modelocl",
                              "cl_dir_localidad","cl_dir_provincia","vp_f_compra","Gender"]
                 if c in df_corp.columns]
    rename_map = {
        "cl_apellido":"Apellido","cl_nombre":"Nombre","cl_numero_doc":"N° Doc",
        "am_modelocl":"Modelo","cl_dir_localidad":"Localidad",
        "cl_dir_provincia":"Provincia","vp_f_compra":"F. Compra","Gender":"Género"
    }
    tabla = df_corp[cols_show].rename(columns=rename_map).head(500)
    if "F. Compra" in tabla.columns:
        tabla["F. Compra"] = tabla["F. Compra"].dt.strftime("%d/%m/%Y")
    st.dataframe(tabla, use_container_width=True, hide_index=True, height=320)

# ══════════════════════════════════════════════════════════════════════════════
# GÉNERO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Género":

    if "Gender" not in df.columns:
        st.warning("No se encontró la columna Gender en tus datos.")
    else:
        # ── KPIs ──
        gender_counts = df["Gender"].value_counts()
        total_gen     = len(df)
        sin_dato_n    = gender_counts.get(SIN_DATO, 0)
        pct_sin_dato  = round(sin_dato_n / total_gen * 100, 1) if total_gen > 0 else 0

        # Colores por género
        COLOR_MAP = {"M": "#0088cc", "F": "#e05c9e", SIN_DATO: "#555570"}
        # Intentamos detectar valores reales (pueden ser "M"/"F", "Masculino"/"Femenino", etc.)
        generos_reales = [g for g in gender_counts.index if g != SIN_DATO]

        kpi_html = ""
        for g in generos_reales:
            n   = gender_counts.get(g, 0)
            pct = round(n / total_gen * 100, 1) if total_gen > 0 else 0
            col = COLOR_MAP.get(g, "#5794f2")
            kpi_html += f"""
            <div class="kpi-card">
              <div class="kpi-label">{g}</div>
              <div class="kpi-value" style="color:{col}">{n:,}</div>
              <div class="kpi-sub">{pct}% del total</div>
              <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{pct}%;background:{col}"></div></div>
            </div>"""

        kpi_html += f"""
        <div class="kpi-card">
          <div class="kpi-label">Sin dato</div>
          <div class="kpi-value" style="color:#555570">{sin_dato_n:,}</div>
          <div class="kpi-sub">{pct_sin_dato}% sin información</div>
          <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{pct_sin_dato}%;background:#555570"></div></div>
        </div>"""

        st.markdown(f'<div class="kpi-grid">{kpi_html}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Fila: Donut | Modelos por género ──
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown('<p class="section-title">Distribución por género</p>', unsafe_allow_html=True)
            gen_df = df["Gender"].value_counts().reset_index()
            gen_df.columns = ["Gender", "n"]
            pie_colors = [COLOR_MAP.get(g, "#5794f2") for g in gen_df["Gender"]]
            fig = go.Figure(go.Pie(
                labels=gen_df["Gender"], values=gen_df["n"], hole=0.5,
                marker=dict(colors=pie_colors),
                textfont=dict(size=11),
            ))
            fig.update_layout(**layout(280, mr=12, mt=8))
            fig.update_layout(showlegend=True, legend=dict(font=dict(size=11)))
            st.plotly_chart(fig, use_container_width=True, config=NO_MB)

        with col2:
            st.markdown('<p class="section-title">Compras por género y modelo</p>', unsafe_allow_html=True)
            gm_df = df.groupby(["am_modelocl","Gender"]).size().reset_index(name="n")
            bar_colors_gm = [COLOR_MAP.get(g, "#5794f2") for g in gm_df["Gender"]]
            fig2 = px.bar(gm_df, x="am_modelocl", y="n", color="Gender",
                          color_discrete_map=COLOR_MAP,
                          barmode="group")
            fig2.update_layout(**layout(280, mr=12, mt=8, mb=50),
                               xaxis=dict(type="category", gridcolor="#1e1e30", linecolor="#1e1e30"),
                               legend=dict(font=dict(size=11), orientation="h", y=-0.3))
            st.plotly_chart(fig2, use_container_width=True, config=NO_MB)

        # ── Género por provincia ──
        if "cl_dir_provincia" in df.columns:
            st.markdown('<p class="section-title">Distribución de género por provincia (top 10)</p>', unsafe_allow_html=True)
            gp_df = (df.groupby(["cl_dir_provincia","Gender"]).size().reset_index(name="n"))
            top_provs = (df.groupby("cl_dir_provincia").size()
                         .nlargest(10).index.tolist())
            gp_df = gp_df[gp_df["cl_dir_provincia"].isin(top_provs)]
            fig3 = px.bar(gp_df, x="cl_dir_provincia", y="n", color="Gender",
                          color_discrete_map=COLOR_MAP,
                          barmode="stack")
            fig3.update_layout(**layout(260, mr=12, mt=8, mb=60),
                               xaxis=dict(type="category", gridcolor="#1e1e30", linecolor="#1e1e30"),
                               legend=dict(font=dict(size=11), orientation="h", y=-0.35))
            st.plotly_chart(fig3, use_container_width=True, config=NO_MB)

        # ── Tendencia por género ──
        if "mes_compra" in df.columns:
            st.markdown('<p class="section-title">Tendencia mensual por género</p>', unsafe_allow_html=True)
            gt_df = df.groupby(["mes_compra","Gender"]).size().reset_index(name="n")
            fig4 = px.line(gt_df, x="mes_compra", y="n", color="Gender",
                           color_discrete_map=COLOR_MAP)
            fig4.update_traces(line_width=2)
            fig4.update_layout(**layout(200, mr=12, mb=50),
                               legend=dict(font=dict(size=11), orientation="h", y=-0.3))
            st.plotly_chart(fig4, use_container_width=True, config=NO_MB)

        # ── Tabla ──
        st.markdown('<p class="section-title">Registro por género</p>', unsafe_allow_html=True)
        cols_show = [c for c in ["cl_apellido","cl_nombre","cl_numero_doc","Gender",
                                  "am_modelocl","cl_dir_localidad","cl_dir_provincia","vp_f_compra"]
                     if c in df.columns]
        rename_map = {
            "cl_apellido":"Apellido","cl_nombre":"Nombre","cl_numero_doc":"N° Doc",
            "Gender":"Género","am_modelocl":"Modelo","cl_dir_localidad":"Localidad",
            "cl_dir_provincia":"Provincia","vp_f_compra":"F. Compra"
        }
        tabla = df[cols_show].rename(columns=rename_map).head(500)
        if "F. Compra" in tabla.columns:
            tabla["F. Compra"] = tabla["F. Compra"].dt.strftime("%d/%m/%Y")
        st.dataframe(tabla, use_container_width=True, hide_index=True, height=320)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-size:10px;color:#333350;letter-spacing:1px;'>"
    "PEUGEOT - BASE DE CLIENTES</p>",
    unsafe_allow_html=True
)
