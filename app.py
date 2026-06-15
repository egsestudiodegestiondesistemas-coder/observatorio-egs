
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime
import io

st.set_page_config(
    page_title="EGS | Observatorio Municipal",
    page_icon="🌱",
    layout="wide"
)

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

DATA_DIR = Path("data")
EXPORT_DIR = Path("exports")
ASSETS_DIR = Path("assets")

DATA_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

BASE_FILE = DATA_DIR / "historico_reclamos.csv"

EGS_GREEN = "#13362F"
EGS_GREEN_2 = "#2B5D54"
EGS_LIGHT = "#F4F7F5"
EGS_LIGHT_GREEN = "#D8E7B8"
EGS_GRAY = "#6B7280"
EGS_WHITE = "#FFFFFF"

# IMPORTANTE:
# Para versión demo comercial se usan credenciales simples.
# Para producción municipal definitiva conviene pasar esto a Streamlit Secrets.
USERS = {
    "yamila_vocos": {
        "password": "EGS@YV_2026!Territorial",
        "nombre": "Yamila Vocos",
        "rol": "Administradora EGS",
        "permisos": [
            "dashboard", "formulario", "carga", "mapa", "analisis",
            "hotspots", "semaforo", "informe", "exportar", "guia", "admin"
        ],
    },
    "municipio_gestor": {
        "password": "Municipio2026!",
        "nombre": "Usuario Municipal",
        "rol": "Gestor municipal",
        "permisos": [
            "dashboard", "formulario", "carga", "mapa", "analisis",
            "hotspots", "semaforo", "informe", "exportar", "guia"
        ],
    },
    "consulta_municipal": {
        "password": "Consulta2026!",
        "nombre": "Consulta institucional",
        "rol": "Solo lectura",
        "permisos": [
            "dashboard", "mapa", "analisis", "hotspots", "semaforo", "informe", "exportar"
        ],
    },
}

CATEGORIAS = [
    "Baches",
    "Iluminación",
    "Pérdida de agua",
    "Arbolado",
    "Residuos",
    "Drenaje urbano",
    "Veredas",
    "Espacios verdes",
    "Señalización",
    "Otro",
]

ESTADOS = ["Pendiente", "En proceso", "Resuelto", "Cerrado"]
PRIORIDADES = ["Baja", "Media", "Alta", "Crítica"]

PESOS_CATEGORIA = {
    "Pérdida de agua": 9,
    "Drenaje urbano": 9,
    "Arbolado": 8,
    "Iluminación": 7,
    "Baches": 6,
    "Residuos": 6,
    "Veredas": 4,
    "Espacios verdes": 5,
    "Señalización": 4,
    "Otro": 5,
}

PESOS_PRIORIDAD = {
    "Baja": 4,
    "Media": 6,
    "Alta": 8,
    "Crítica": 10,
}

# =========================================================
# ESTILO EGS
# =========================================================

def inject_css():
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {EGS_LIGHT}; }}
    .block-container {{ padding-top: 1.4rem; max-width: 1480px; }}
    [data-testid="stSidebar"] {{ background: #EEF3F0; }}
    .egs-header {{
        background: linear-gradient(135deg, {EGS_GREEN}, {EGS_GREEN_2});
        color: white;
        padding: 34px 38px;
        border-radius: 24px;
        margin-bottom: 26px;
        box-shadow: 0 8px 20px rgba(19,54,47,0.14);
    }}
    .egs-header h1 {{ font-size: 42px; margin-bottom: 6px; letter-spacing: -0.5px; }}
    .egs-header p {{ font-size: 16px; color: #E7F0EC; margin: 4px 0; }}
    .metric-card {{
        background: white;
        border: 1px solid #DDE5E0;
        border-radius: 20px;
        padding: 20px;
        min-height: 145px;
        box-shadow: 0 4px 12px rgba(19,54,47,0.05);
    }}
    .metric-card h4 {{ color: {EGS_GREEN}; font-size: 15px; margin-bottom: 12px; }}
    .metric-card h2 {{ font-size: 32px; margin: 0; color: #17202A; }}
    .metric-card p {{ color: {EGS_GRAY}; font-size: 13px; }}
    .alert-box {{
        background: white;
        border-left: 7px solid {EGS_GREEN};
        border-radius: 14px;
        padding: 18px;
        margin: 12px 0px;
        box-shadow: 0 4px 12px rgba(19,54,47,0.05);
    }}
    .role-chip {{
        background: {EGS_GREEN};
        color: white;
        border-radius: 999px;
        padding: 6px 12px;
        display: inline-block;
        font-size: 13px;
        margin-top: 4px;
    }}
    .small-note {{ color: {EGS_GRAY}; font-size: 13px; }}
    .municipal-badge {{
        background: {EGS_LIGHT_GREEN};
        color: {EGS_GREEN};
        border-radius: 999px;
        padding: 7px 13px;
        display: inline-block;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# =========================================================
# LOGIN
# =========================================================

def login_screen():
    st.markdown(f"""
    <div class="egs-header">
        <span class="municipal-badge">Versión municipal · acceso autorizado</span>
        <h1>EGS | Observatorio Territorial Municipal</h1>
        <p>Gestión ambiental · análisis territorial · seguimiento de incidencias urbanas · indicadores estratégicos</p>
        <p class="small-note">Plataforma de uso técnico para equipos de gestión y toma de decisiones.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.15, 1])
    with col2:
        st.markdown("### Ingreso al sistema")
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar", use_container_width=True):
            user = USERS.get(usuario.strip().lower())
            if user and password == user["password"]:
                st.session_state["logged"] = True
                st.session_state["usuario"] = usuario.strip().lower()
                st.session_state["nombre"] = user["nombre"]
                st.session_state["rol"] = user["rol"]
                st.session_state["permisos"] = user["permisos"]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

        st.info("Acceso exclusivo para usuarios autorizados de EGS y equipo municipal.")

if "logged" not in st.session_state:
    st.session_state["logged"] = False

if not st.session_state["logged"]:
    login_screen()
    st.stop()

def has_perm(perm):
    return perm in st.session_state.get("permisos", [])

# =========================================================
# DATOS
# =========================================================

def demo_data():
    return pd.DataFrame([
        ["2026-01-10", "Baches", "Bache en esquina", "Av. Libertador 1200", "Centro", -31.4275, -62.0821, "Pendiente", "Media", "", 6, "Carga demo"],
        ["2026-01-18", "Iluminación", "Luminaria apagada", "Bv. 9 de Julio 850", "Centro", -31.4301, -62.0812, "Resuelto", "Alta", "2026-01-25", 7, "Carga demo"],
        ["2026-02-03", "Pérdida de agua", "Pérdida constante", "Córdoba 300", "Sarmiento", -31.4259, -62.0910, "En proceso", "Alta", "", 9, "Carga demo"],
        ["2026-02-20", "Arbolado", "Rama con riesgo", "Mitre 600", "Roca", -31.4210, -62.0844, "Pendiente", "Alta", "", 8, "Carga demo"],
        ["2026-03-14", "Residuos", "Acumulación de residuos", "Italia 950", "San Cayetano", -31.4330, -62.0744, "Resuelto", "Media", "2026-03-20", 6, "Carga demo"],
        ["2026-03-21", "Drenaje urbano", "Calle anegada", "Av. Rosario 1800", "Independencia", -31.4365, -62.0895, "Pendiente", "Alta", "", 9, "Carga demo"],
        ["2026-04-04", "Veredas", "Vereda rota", "Belgrano 700", "Centro", -31.4282, -62.0799, "Pendiente", "Baja", "", 4, "Carga demo"],
        ["2026-04-27", "Baches", "Pozo grande", "Urquiza 1100", "Roca", -31.4225, -62.0878, "En proceso", "Media", "", 7, "Carga demo"],
        ["2026-09-08", "Iluminación", "Zona oscura", "Avellaneda 1400", "Sarmiento", -31.4267, -62.0932, "Resuelto", "Alta", "2026-09-18", 8, "Carga demo"],
        ["2026-10-02", "Pérdida de agua", "Pérdida sobre calzada", "San Martín 400", "Centro", -31.4279, -62.0804, "Pendiente", "Alta", "", 10, "Carga demo"],
    ], columns=[
        "fecha", "categoria", "descripcion", "direccion", "barrio",
        "latitud", "longitud", "estado", "prioridad", "fecha_resolucion",
        "criticidad", "fuente"
    ])

def ensure_columns(df):
    required = [
        "fecha", "categoria", "descripcion", "direccion", "barrio",
        "latitud", "longitud", "estado", "prioridad", "fecha_resolucion",
        "criticidad", "fuente"
    ]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    return df[required]

def load_base():
    if BASE_FILE.exists():
        df = pd.read_csv(BASE_FILE)
        return ensure_columns(df)
    df = demo_data()
    df.to_csv(BASE_FILE, index=False)
    return df

def save_base(df):
    df = ensure_columns(df)
    df.to_csv(BASE_FILE, index=False)

def normalize_columns(df):
    mapping = {
        "fecha": ["fecha", "date", "created", "timestamp", "fecha_reclamo", "fecha de carga", "fecha carga"],
        "categoria": ["categoria", "categoría", "tipo", "tipo_reclamo", "reclamo", "problema"],
        "descripcion": ["descripcion", "descripción", "detalle", "observacion", "observación", "comentario", "descripcion reclamo"],
        "direccion": ["direccion", "dirección", "address", "domicilio", "ubicacion", "ubicación"],
        "barrio": ["barrio", "sector", "zona"],
        "latitud": ["latitud", "latitude", "lat"],
        "longitud": ["longitud", "longitude", "lon", "lng"],
        "estado": ["estado", "status", "situacion", "situación"],
        "prioridad": ["prioridad", "priority", "urgencia"],
        "fecha_resolucion": ["fecha_resolucion", "fecha resolución", "fecha_cierre", "cierre", "resolved"],
        "criticidad": ["criticidad", "indice", "índice", "riesgo", "prioridad_egs"],
        "fuente": ["fuente", "origen", "source"],
    }

    cols_lower = {str(c).lower().strip(): c for c in df.columns}
    result = pd.DataFrame()

    for target, aliases in mapping.items():
        found = None
        for alias in aliases:
            if alias.lower() in cols_lower:
                found = cols_lower[alias.lower()]
                break
        result[target] = df[found] if found else ""

    result["fecha"] = pd.to_datetime(result["fecha"], errors="coerce")
    result["fecha_resolucion"] = pd.to_datetime(result["fecha_resolucion"], errors="coerce")
    result["latitud"] = pd.to_numeric(result["latitud"], errors="coerce")
    result["longitud"] = pd.to_numeric(result["longitud"], errors="coerce")
    result["criticidad"] = pd.to_numeric(result["criticidad"], errors="coerce")

    result["categoria"] = result["categoria"].fillna("Sin categoría").replace("", "Sin categoría")
    result["estado"] = result["estado"].fillna("Pendiente").replace("", "Pendiente")
    result["barrio"] = result["barrio"].fillna("Sin barrio").replace("", "Sin barrio")
    result["prioridad"] = result["prioridad"].fillna("Media").replace("", "Media")
    result["fuente"] = result["fuente"].fillna("Carga externa").replace("", "Carga externa")

    result["criticidad"] = result.apply(
        lambda r: calcular_criticidad(r["categoria"], r["prioridad"]) if pd.isna(r["criticidad"]) else r["criticidad"],
        axis=1
    )

    return result.dropna(subset=["fecha"])

def prepare(df):
    df = ensure_columns(df.copy())
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["fecha_resolucion"] = pd.to_datetime(df["fecha_resolucion"], errors="coerce")
    df["latitud"] = pd.to_numeric(df["latitud"], errors="coerce")
    df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")
    df["criticidad"] = pd.to_numeric(df["criticidad"], errors="coerce").fillna(5)
    df["categoria"] = df["categoria"].fillna("Sin categoría").replace("", "Sin categoría")
    df["estado"] = df["estado"].fillna("Pendiente").replace("", "Pendiente")
    df["barrio"] = df["barrio"].fillna("Sin barrio").replace("", "Sin barrio")
    df["direccion"] = df["direccion"].fillna("")
    df["prioridad"] = df["prioridad"].fillna("Media").replace("", "Media")
    df["fuente"] = df["fuente"].fillna("Sin fuente").replace("", "Sin fuente")
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    df["dias_resolucion"] = (df["fecha_resolucion"] - df["fecha"]).dt.days
    df["estado_limpio"] = df["estado"].astype(str).str.lower().str.strip()
    df["activo"] = ~df["estado_limpio"].isin(["resuelto", "cerrado", "finalizado"])
    df["dias_abierto"] = (pd.Timestamp.now().normalize() - df["fecha"]).dt.days
    return df.dropna(subset=["fecha"])

def read_upload(file):
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def calcular_criticidad(categoria, prioridad):
    categoria_score = PESOS_CATEGORIA.get(str(categoria).strip(), 5)
    prioridad_score = PESOS_PRIORIDAD.get(str(prioridad).strip(), 6)
    return round((categoria_score * 0.65) + (prioridad_score * 0.35), 1)

# =========================================================
# ANÁLISIS
# =========================================================

def territorial_ranking(df):
    if df.empty:
        return pd.DataFrame(columns=[
            "barrio", "incidencias", "criticidad_promedio", "casos_activos",
            "casos_resueltos", "indice_egs", "nivel_prioridad"
        ])

    ranking = df.groupby("barrio").agg(
        incidencias=("categoria", "count"),
        criticidad_promedio=("criticidad", "mean"),
        casos_activos=("activo", "sum"),
        casos_resueltos=("activo", lambda x: (~x).sum()),
        dias_abierto_promedio=("dias_abierto", "mean")
    ).reset_index()

    ranking["indice_egs"] = (
        ranking["incidencias"] * 1.5 +
        ranking["criticidad_promedio"] * 2 +
        ranking["casos_activos"] * 1.4 +
        (ranking["dias_abierto_promedio"].fillna(0) / 30)
    ).round(1)

    ranking["nivel_prioridad"] = ranking["indice_egs"].apply(
        lambda x: "Prioridad 1 - Crítica" if x >= 25 else
                  "Prioridad 2 - Alta" if x >= 18 else
                  "Prioridad 3 - Media" if x >= 10 else
                  "Prioridad 4 - Baja"
    )

    return ranking.sort_values("indice_egs", ascending=False)

def semaforo_gestion(df):
    total = len(df)
    if total == 0:
        return "Sin datos", 0
    resueltos = len(df[df["estado_limpio"].isin(["resuelto", "cerrado", "finalizado"])])
    tasa = round((resueltos / total) * 100, 1)
    if tasa >= 80:
        return "🟢 Excelente", tasa
    if tasa >= 50:
        return "🟡 A mejorar", tasa
    return "🔴 Crítico", tasa

def lectura_automatica(df):
    if df.empty:
        return "No hay datos suficientes para generar lectura automática."
    ranking = territorial_ranking(df)
    top_barrio = ranking.iloc[0]["barrio"] if not ranking.empty else "-"
    top_cat = df["categoria"].value_counts().idxmax()
    activos = int(df["activo"].sum())
    total = len(df)
    estado, tasa = semaforo_gestion(df)
    return (
        f"Durante el período analizado se registraron {total} incidencias. "
        f"La categoría predominante fue {top_cat}. "
        f"El sector con mayor prioridad territorial fue {top_barrio}. "
        f"Actualmente permanecen {activos} casos activos. "
        f"La tasa de resolución estimada es {tasa}% ({estado})."
    )

# =========================================================
# INFORMES Y EXPORTACIÓN
# =========================================================

def generar_informe_tecnico_html(df, selected_months):
    total = len(df)
    activos = int(df["activo"].sum()) if total else 0
    cerrados = total - activos
    estado, tasa = semaforo_gestion(df)
    criticidad = round(df["criticidad"].mean(), 1) if total else 0
    cat_top = df["categoria"].value_counts().idxmax() if total else "-"
    barrio_top = df["barrio"].value_counts().idxmax() if total else "-"
    ranking = territorial_ranking(df)
    prioridad_1 = len(ranking[ranking["nivel_prioridad"].str.contains("Crítica", na=False)]) if not ranking.empty else 0
    periodo = ", ".join(selected_months) if selected_months else "Todos los registros"
    fecha = datetime.now().strftime("%d/%m/%Y")
    lectura = lectura_automatica(df)

    ranking_html = ranking.head(15).to_html(index=False) if not ranking.empty else "<p>Sin datos suficientes para ranking territorial.</p>"

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <title>Informe Técnico Municipal EGS</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 42px; color: #17202A; }}
        .cover {{ background: #13362F; color: white; padding: 42px; border-radius: 18px; }}
        .cover h1 {{ font-size: 34px; }}
        .sub {{ color: #D8E7B8; font-size: 15px; }}
        h2 {{ color: #13362F; border-bottom: 2px solid #D8E7B8; padding-bottom: 6px; margin-top: 28px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 12px; }}
        th, td {{ border: 1px solid #DDE5E0; padding: 8px; text-align: left; }}
        th {{ background: #F4F7F5; color: #13362F; }}
        .metric {{ display: inline-block; width: 30%; margin: 8px; padding: 18px; background: #F4F7F5; border-radius: 12px; vertical-align: top; }}
        .metric b {{ font-size: 26px; color: #13362F; }}
        .note {{ background: #F4F7F5; border-left: 6px solid #13362F; padding: 16px; margin: 14px 0; }}
        .footer {{ margin-top: 36px; font-size: 12px; color: #6B7280; }}
    </style>
    </head>
    <body>
        <div class="cover">
            <h1>EGS | Informe Técnico Municipal</h1>
            <p class="sub">Observatorio Territorial · Gestión ambiental · Indicadores estratégicos · Seguimiento de incidencias urbanas</p>
            <p><b>Período analizado:</b> {periodo}</p>
            <p><b>Fecha de emisión:</b> {fecha}</p>
        </div>

        <h2>1. Síntesis ejecutiva</h2>
        <div class="metric"><p>Incidencias registradas</p><b>{total}</b></div>
        <div class="metric"><p>Casos activos</p><b>{activos}</b></div>
        <div class="metric"><p>Casos cerrados</p><b>{cerrados}</b></div>
        <div class="metric"><p>Tasa de resolución</p><b>{tasa}%</b></div>
        <div class="metric"><p>Estado general</p><b>{estado}</b></div>
        <div class="metric"><p>Criticidad media EGS</p><b>{criticidad}</b></div>

        <h2>2. Lectura automática</h2>
        <div class="note">{lectura}</div>

        <h2>3. Resultados principales</h2>
        <p>La categoría predominante fue <b>{cat_top}</b>. El sector con mayor concentración territorial fue <b>{barrio_top}</b>. Se identificaron <b>{prioridad_1}</b> sectores con prioridad crítica según el Índice Territorial EGS.</p>

        <h2>4. Metodología del Índice Territorial EGS</h2>
        <p>El Índice Territorial EGS combina cantidad de incidencias, criticidad promedio, casos activos y antigüedad promedio de los casos. Esta ponderación permite priorizar sectores donde coinciden recurrencia, gravedad técnica y falta de resolución.</p>
        <div class="note"><b>Fórmula aplicada:</b> Índice EGS = incidencias × 1,5 + criticidad promedio × 2 + casos activos × 1,4 + antigüedad promedio / 30.</div>

        <h2>5. Ranking territorial</h2>
        {ranking_html}

        <h2>6. Recomendaciones técnicas</h2>
        <ul>
            <li>Sostener la carga mensual normalizada.</li>
            <li>Validar coordenadas para mejorar precisión cartográfica.</li>
            <li>Completar fecha de resolución en todos los casos cerrados.</li>
            <li>Priorizar sectores clasificados como Prioridad 1 - Crítica.</li>
            <li>Cruzar incidencias con capas SIG municipales: barrios, escuelas, centros de salud, espacios verdes, drenaje e infraestructura crítica.</li>
            <li>Utilizar la serie histórica como insumo de planificación, mantenimiento urbano y comunicación institucional.</li>
        </ul>

        <h2>7. Cierre</h2>
        <p>El Observatorio Territorial EGS transforma datos operativos en indicadores territoriales, permitiendo pasar de la recepción de reclamos a una herramienta técnica de priorización, seguimiento y planificación municipal.</p>

        <div class="footer">
            EGS | Estudio de Gestión de Sistemas · Informe generado automáticamente desde el Observatorio Territorial Municipal.
        </div>
    </body>
    </html>
    """
    return html

def generar_informe_txt(df, selected_months):
    total = len(df)
    activos = int(df["activo"].sum()) if total else 0
    cerrados = total - activos
    estado, tasa = semaforo_gestion(df)
    cat_top = df["categoria"].value_counts().idxmax() if total else "-"
    barrio_top = df["barrio"].value_counts().idxmax() if total else "-"
    criticidad = round(df["criticidad"].mean(), 1) if total else 0
    periodo = ", ".join(selected_months) if selected_months else "Todos los registros"
    return f"""EGS | INFORME TÉCNICO MUNICIPAL

Período analizado: {periodo}
Fecha de emisión: {datetime.now().strftime("%d/%m/%Y")}

Síntesis:
- Incidencias registradas: {total}
- Casos activos: {activos}
- Casos cerrados: {cerrados}
- Tasa de resolución: {tasa}%
- Estado general: {estado}
- Criticidad media EGS: {criticidad}

Resultados:
La categoría predominante fue {cat_top}. El sector con mayor concentración territorial fue {barrio_top}.

Lectura técnica:
{lectura_automatica(df)}

Metodología:
El Índice Territorial EGS combina cantidad de incidencias, criticidad promedio, casos activos y antigüedad de casos.

Recomendaciones:
- Sostener carga mensual normalizada.
- Validar coordenadas.
- Completar fecha de resolución.
- Priorizar sectores críticos.
- Usar la serie histórica para planificación territorial.
- Cruzar la base con capas SIG municipales.

Cierre:
El Observatorio Territorial EGS transforma datos operativos en indicadores y prioridades para la toma de decisiones municipales.
"""

def excel_download(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="base_filtrada")
        if not df.empty:
            df.groupby("categoria").size().reset_index(name="cantidad").to_excel(writer, index=False, sheet_name="por_categoria")
            df.groupby("barrio").size().reset_index(name="cantidad").to_excel(writer, index=False, sheet_name="por_barrio")
            df.groupby("mes").size().reset_index(name="cantidad").to_excel(writer, index=False, sheet_name="evolucion_mensual")
            territorial_ranking(df).to_excel(writer, index=False, sheet_name="indice_egs")
    return output.getvalue()

def plantilla_excel():
    plantilla = pd.DataFrame([{
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "categoria": "Baches",
        "descripcion": "Descripción breve de la incidencia",
        "direccion": "Dirección o referencia",
        "barrio": "Centro",
        "latitud": -31.4275,
        "longitud": -62.0821,
        "estado": "Pendiente",
        "prioridad": "Media",
        "fecha_resolucion": "",
        "criticidad": "",
        "fuente": "Carga municipal"
    }])
    return excel_download(plantilla)

# =========================================================
# CARGA BASE Y FILTROS
# =========================================================

df = prepare(load_base())

ALL_MODULES = {
    "Dashboard municipal": "dashboard",
    "Nueva incidencia": "formulario",
    "Carga mensual": "carga",
    "Mapa territorial": "mapa",
    "Análisis territorial": "analisis",
    "Hotspots urbanos": "hotspots",
    "Semáforo de gestión": "semaforo",
    "Informe técnico": "informe",
    "Exportar": "exportar",
    "Guía de columnas": "guia",
}

available_modules = [m for m, p in ALL_MODULES.items() if has_perm(p)]

with st.sidebar:
    st.markdown("## Panel operativo")
    st.caption("Observatorio EGS para uso interno y equipo municipal.")
    st.markdown(f"**{st.session_state['nombre']}**")
    st.markdown(f"<span class='role-chip'>{st.session_state['rol']}</span>", unsafe_allow_html=True)

    module = st.radio("Módulo", available_modules)

    st.divider()

    if has_perm("admin"):
        if st.button("Reiniciar base demo"):
            save_base(demo_data())
            st.rerun()

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    meses = sorted(df["mes"].dropna().unique().tolist())
    selected_months = st.multiselect("Filtrar por mes", meses, default=meses)

    categorias_filtro = sorted(df["categoria"].dropna().unique().tolist())
    selected_cats = st.multiselect("Filtrar por categoría", categorias_filtro, default=categorias_filtro)

if selected_months:
    dff = df[df["mes"].isin(selected_months)].copy()
else:
    dff = df.copy()

if selected_cats:
    dff = dff[dff["categoria"].isin(selected_cats)].copy()

st.markdown("""
<div class="egs-header">
    <span class="municipal-badge">Versión Municipal V2</span>
    <h1>EGS | Observatorio Territorial Municipal</h1>
    <p>Estudio de Gestión de Sistemas · Análisis territorial · Gestión ambiental · Indicadores estratégicos · Seguimiento de incidencias urbanas</p>
    <p class="small-note">Plataforma preparada para uso técnico municipal, carga mensual, análisis espacial e informes automáticos.</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# MÓDULOS
# =========================================================

if module == "Dashboard municipal":
    total = len(dff)
    activos = int(dff["activo"].sum()) if total else 0
    resueltos = total - activos
    criticidad = round(dff["criticidad"].mean(), 1) if total else 0
    dias = round(dff["dias_resolucion"].dropna().mean(), 1) if dff["dias_resolucion"].notna().any() else 0
    estado_gestion, tasa_resolucion = semaforo_gestion(dff)

    st.markdown("## Tablero ejecutivo municipal")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    cards = [
        (c1, "Incidencias registradas", total, "Registros filtrados"),
        (c2, "Casos activos", activos, "Pendientes o en proceso"),
        (c3, "Casos cerrados", resueltos, "Resolución informada"),
        (c4, "Criticidad media EGS", criticidad, "Escala técnica interna"),
        (c5, "Tiempo medio", dias, "Días de resolución"),
        (c6, "Gestión", estado_gestion, f"{tasa_resolucion}% resuelto"),
    ]

    for col, title, value, label in cards:
        col.markdown(f"""<div class="metric-card"><h4>{title}</h4><h2>{value}</h2><p>{label}</p></div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="alert-box"><b>Lectura técnica automática:</b><br>{lectura_automatica(dff)}</div>""", unsafe_allow_html=True)

    monthly = df.groupby("mes").size().reset_index(name="cantidad")
    if len(monthly) >= 2:
        last = monthly.iloc[-1]
        prev = monthly.iloc[-2]
        diff = int(last["cantidad"] - prev["cantidad"])
        pct = round((diff / prev["cantidad"]) * 100, 1) if prev["cantidad"] else 0
        st.info(f"Comparación mensual: {last['mes']} registra {last['cantidad']} incidencias frente a {prev['cantidad']} en {prev['mes']}. Variación: {diff:+} casos ({pct:+}%).")

    col1, col2 = st.columns(2)
    with col1:
        cat_df = dff.groupby("categoria").size().reset_index(name="cantidad").sort_values("cantidad", ascending=False)
        fig = px.bar(cat_df, x="categoria", y="cantidad", title="Incidencias por categoría", text="cantidad")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.pie(dff, names="estado", title="Estado de gestión", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = px.line(df.groupby("mes").size().reset_index(name="cantidad"), x="mes", y="cantidad", markers=True, title="Evolución mensual")
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        barrio = dff.groupby("barrio").size().reset_index(name="cantidad").sort_values("cantidad", ascending=False).head(10)
        fig = px.bar(barrio, x="cantidad", y="barrio", orientation="h", title="Top sectores críticos")
        st.plotly_chart(fig, use_container_width=True)

elif module == "Nueva incidencia":
    st.markdown("## Nueva incidencia")
    st.write("Formulario interno para cargar incidencias desde EGS o equipo municipal. Para carga ciudadana masiva se recomienda mantener AppSheet o formulario externo.")

    with st.form("form_nueva_incidencia", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha", value=datetime.now())
            categoria = st.selectbox("Categoría", CATEGORIAS)
            estado = st.selectbox("Estado", ESTADOS)
            prioridad = st.selectbox("Prioridad", PRIORIDADES, index=1)
            barrio = st.text_input("Barrio / sector", value="")
        with col2:
            direccion = st.text_input("Dirección / referencia")
            latitud = st.number_input("Latitud", value=-31.4275, format="%.6f")
            longitud = st.number_input("Longitud", value=-62.0821, format="%.6f")
            fecha_resolucion = st.date_input("Fecha de resolución", value=None)
            fuente = st.text_input("Fuente", value="Carga manual EGS")

        descripcion = st.text_area("Descripción", height=110)

        submitted = st.form_submit_button("Guardar incidencia")

        if submitted:
            criticidad = calcular_criticidad(categoria, prioridad)
            nuevo = pd.DataFrame([{
                "fecha": fecha.strftime("%Y-%m-%d"),
                "categoria": categoria,
                "descripcion": descripcion,
                "direccion": direccion,
                "barrio": barrio if barrio else "Sin barrio",
                "latitud": latitud,
                "longitud": longitud,
                "estado": estado,
                "prioridad": prioridad,
                "fecha_resolucion": fecha_resolucion.strftime("%Y-%m-%d") if fecha_resolucion else "",
                "criticidad": criticidad,
                "fuente": fuente,
            }])
            base = load_base()
            combined = pd.concat([base, nuevo], ignore_index=True)
            save_base(combined)
            st.success("Incidencia guardada correctamente. El tablero queda actualizado.")
            st.rerun()

elif module == "Carga mensual":
    st.markdown("## Carga mensual automatizada")
    st.write("Subí el CSV o Excel exportado desde AppSheet, formulario municipal o base externa. El sistema normaliza columnas y actualiza todo el observatorio.")

    col1, col2 = st.columns([1, 1])
    with col1:
        mes_carga = st.text_input("Mes de carga", value=datetime.now().strftime("%Y-%m"))
    with col2:
        st.download_button("Descargar plantilla Excel", plantilla_excel(), file_name="plantilla_carga_municipal_egs.xlsx")

    uploaded = st.file_uploader("Archivo CSV o Excel", type=["csv", "xlsx", "xls"])

    if uploaded:
        raw = read_upload(uploaded)
        norm = normalize_columns(raw)
        norm["fuente"] = norm["fuente"].replace("", f"Carga mensual {mes_carga}")

        st.success(f"Archivo leído correctamente: {len(norm)} registros detectados.")
        st.dataframe(norm.head(40), use_container_width=True)

        if st.button("Incorporar al histórico"):
            base = load_base()
            combined = pd.concat([base, norm], ignore_index=True)
            combined = combined.drop_duplicates(
                subset=["fecha", "categoria", "descripcion", "direccion"],
                keep="last"
            )
            save_base(combined)
            st.success("Carga mensual incorporada. El observatorio ya quedó actualizado.")
            st.rerun()

elif module == "Mapa territorial":
    st.markdown("## Mapa territorial de incidencias")
    map_df = dff.dropna(subset=["latitud", "longitud"])

    if map_df.empty:
        st.warning("No hay coordenadas válidas para mapear.")
    else:
        center_lat = map_df["latitud"].mean()
        center_lon = map_df["longitud"].mean()

        fig = px.scatter_map(
            map_df,
            lat="latitud",
            lon="longitud",
            color="categoria",
            size="criticidad",
            hover_name="categoria",
            hover_data=["descripcion", "direccion", "barrio", "estado", "prioridad", "criticidad"],
            zoom=12,
            height=660,
            title="Distribución georreferenciada de incidencias"
        )
        fig.update_layout(
            map_style="open-street-map",
            map_center={"lat": center_lat, "lon": center_lon},
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.density_map(
            map_df,
            lat="latitud",
            lon="longitud",
            z="criticidad",
            radius=28,
            zoom=12,
            height=620,
            title="Mapa de densidad territorial por criticidad"
        )
        fig2.update_layout(
            map_style="open-street-map",
            map_center={"lat": center_lat, "lon": center_lon},
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        st.plotly_chart(fig2, use_container_width=True)

elif module == "Análisis territorial":
    st.markdown("## Análisis territorial EGS")
    ranking = territorial_ranking(dff)

    st.markdown("### Índice de Prioridad Territorial EGS")
    st.write("El índice combina cantidad de incidencias, criticidad promedio, casos activos y antigüedad promedio de los casos.")

    st.dataframe(ranking, use_container_width=True)

    if not ranking.empty:
        fig = px.bar(
            ranking.head(12),
            x="indice_egs",
            y="barrio",
            color="nivel_prioridad",
            orientation="h",
            title="Ranking de prioridad territorial"
        )
        st.plotly_chart(fig, use_container_width=True)

        top = ranking.iloc[0]
        st.markdown(
            f"""<div class="alert-box"><b>Lectura automática EGS:</b><br>
            El sector con mayor prioridad territorial es <b>{top['barrio']}</b>, 
            con {int(top['incidencias'])} incidencias, criticidad promedio 
            {round(top['criticidad_promedio'], 1)} e índice EGS {top['indice_egs']}.</div>""",
            unsafe_allow_html=True
        )

elif module == "Hotspots urbanos":
    st.markdown("## Hotspots urbanos")
    st.write("Detección automática de concentración territorial, categorías dominantes y direcciones recurrentes.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Barrios con mayor concentración")
        barrios = dff["barrio"].value_counts().reset_index()
        barrios.columns = ["barrio", "cantidad"]
        st.dataframe(barrios.head(10), use_container_width=True)
        if not barrios.empty:
            fig = px.bar(barrios.head(10), x="cantidad", y="barrio", orientation="h", title="Hotspots por barrio")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Direcciones recurrentes")
        direcciones = dff["direccion"].value_counts().reset_index()
        direcciones.columns = ["direccion", "cantidad"]
        st.dataframe(direcciones.head(10), use_container_width=True)
        if not direcciones.empty:
            fig = px.bar(direcciones.head(10), x="cantidad", y="direccion", orientation="h", title="Hotspots por dirección")
            st.plotly_chart(fig, use_container_width=True)

    if len(dff) > 0:
        barrio_top = dff["barrio"].value_counts().idxmax()
        categoria_top = dff["categoria"].value_counts().idxmax()
        porcentaje = round((dff["barrio"].value_counts().max() / len(dff)) * 100, 1)
        st.info(f"Lectura automática: el {porcentaje}% de las incidencias se concentra en {barrio_top}. La categoría dominante es {categoria_top}.")

elif module == "Semáforo de gestión":
    st.markdown("## Semáforo de gestión")
    st.write("Evaluación visual de desempeño por categoría.")

    estado, tasa = semaforo_gestion(dff)
    st.markdown(f"""<div class="alert-box"><h3>Estado general: {estado}</h3><p>Tasa de resolución estimada: <b>{tasa}%</b></p></div>""", unsafe_allow_html=True)

    if not dff.empty:
        sem_cat = dff.groupby("categoria").agg(
            total=("categoria", "count"),
            activos=("activo", "sum")
        ).reset_index()
        sem_cat["resueltos"] = sem_cat["total"] - sem_cat["activos"]
        sem_cat["tasa_resolucion"] = round((sem_cat["resueltos"] / sem_cat["total"]) * 100, 1)
        sem_cat["semaforo"] = sem_cat["tasa_resolucion"].apply(
            lambda x: "🟢 Excelente" if x >= 80 else "🟡 A mejorar" if x >= 50 else "🔴 Crítico"
        )
        st.dataframe(sem_cat, use_container_width=True)
        fig = px.bar(sem_cat, x="categoria", y="tasa_resolucion", color="semaforo", title="Tasa de resolución por categoría")
        st.plotly_chart(fig, use_container_width=True)

elif module == "Informe técnico":
    st.markdown("## Informe técnico municipal EGS")
    st.write("Generación automática de informe técnico territorial en formato HTML y TXT.")

    informe_txt = generar_informe_txt(dff, selected_months)
    informe_html = generar_informe_tecnico_html(dff, selected_months)

    st.text_area("Vista rápida del informe", informe_txt, height=460)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Descargar informe técnico HTML",
            informe_html.encode("utf-8"),
            file_name="informe_tecnico_municipal_egs.html",
            mime="text/html"
        )
    with col2:
        st.download_button(
            "Descargar informe técnico TXT",
            informe_txt.encode("utf-8"),
            file_name="informe_tecnico_municipal_egs.txt",
            mime="text/plain"
        )

elif module == "Exportar":
    st.markdown("## Exportación de datos")
    st.download_button(
        "Descargar base filtrada CSV",
        dff.to_csv(index=False).encode("utf-8"),
        file_name="base_filtrada_egs.csv"
    )
    st.download_button(
        "Descargar informe Excel",
        excel_download(dff),
        file_name="observatorio_territorial_municipal_egs.xlsx"
    )

elif module == "Guía de columnas":
    st.markdown("## Guía para cargar datos reales")
    guia = pd.DataFrame({
        "columna_recomendada": [
            "fecha", "categoria", "descripcion", "direccion", "barrio",
            "latitud", "longitud", "estado", "prioridad", "fecha_resolucion", "criticidad", "fuente"
        ],
        "ejemplo": [
            "2026-06-15", "Baches", "Bache en esquina", "Av. Libertador 1200", "Centro",
            "-31.4275", "-62.0821", "Pendiente", "Alta", "2026-06-20", "8", "AppSheet"
        ],
        "obligatoria": [
            "Sí", "Sí", "No", "No", "No", "No", "No", "No", "No", "No", "No", "No"
        ]
    })
    st.dataframe(guia, use_container_width=True)
    st.download_button(
        "Descargar plantilla Excel",
        plantilla_excel(),
        file_name="plantilla_carga_municipal_egs.xlsx"
    )
