import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

st.set_page_config(
    page_title="Método de los Trapecios",
    layout="wide",
)

# --- Estilos personalizados con más color en letras y módulos ---
st.markdown(
    """
    <style>
    /* Fondo general y tipografía */
    .stApp {
        background: linear-gradient(160deg, #0b1120 0%, #0f172a 55%, #131c31 100%);
        color: #f1f5f9;
    }
    /* Sidebar colorido */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #172554 100%);
        border-right: 2px solid #06b6d4;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label {
        color: #38bdf8 !important;
        font-weight: 600 !important;
    }
    /* Banner principal */
    .hero-box {
        background: linear-gradient(90deg, rgba(6,182,212,0.18) 0%, rgba(99,102,241,0.18) 50%, rgba(16,185,129,0.18) 100%);
        border: 1px solid rgba(56, 189, 248, 0.45);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.2rem;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #22d3ee, #34d399, #fbbf24);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub {
        color: #cbd5e1;
        font-size: 0.95rem;
        margin-top: 0.35rem;
        margin-bottom: 0;
    }
    /* Tarjetas métricas con colores diferenciados */
    .kpi-card {
        border-radius: 14px;
        padding: 1rem 1.15rem;
        background-color: rgba(15, 23, 42, 0.85);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
    }
    .kpi-cyan   { border: 1.5px solid #06b6d4; border-top: 5px solid #22d3ee; }
    .kpi-green  { border: 1.5px solid #10b981; border-top: 5px solid #34d399; }
    .kpi-rose   { border: 1.5px solid #f43f5e; border-top: 5px solid #fb7185; }
    .kpi-amber  { border: 1.5px solid #f59e0b; border-top: 5px solid #fbbf24; }
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-bottom: 0.25rem;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        font-family: monospace;
    }
    .kpi-foot {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }
    /* Módulos de contenido */
    .module-badge {
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 0.75rem;
    }
    /* Botón de confirmar cambios */
    div[data-testid="stFormSubmitButton"] > button {
        width: 100%;
        background: linear-gradient(90deg, #06b6d4 0%, #10b981 100%) !important;
        color: #020617 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        filter: brightness(1.12);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Catálogo de funciones elegibles como lista ---
FUNCIONES_DISPONIBLES = {
    "Exponencial: f(x) = exp(x)": {
        "fn": lambda x: np.exp(x),
        "formula": "exp(x)",
        "nota": "Ejemplo original de tu script Python.",
    },
    "Seno: f(x) = sin(x)": {
        "fn": lambda x: np.sin(x),
        "formula": "sin(x)",
        "nota": "Onda trigonométrica periódica.",
    },
    "Coseno: f(x) = cos(x)": {
        "fn": lambda x: np.cos(x),
        "formula": "cos(x)",
        "nota": "Función trigonométrica par.",
    },
    "Parábola: f(x) = x²": {
        "fn": lambda x: x**2,
        "formula": "x^2",
        "nota": "Función cuadrática convexa.",
    },
    "Cúbica: f(x) = x³ - 2x + 2": {
        "fn": lambda x: x**3 - 2 * x + 2,
        "formula": "x^3 - 2x + 2",
        "nota": "Polinomio de tercer grado.",
    },
    "Racional: f(x) = 1 / (1 + x²)": {
        "fn": lambda x: 1.0 / (1.0 + x**2),
        "formula": "1 / (1 + x^2)",
        "nota": "Curva cuya integral en [0, 1] es π/4.",
    },
    "Campana Gaussiana: f(x) = exp(-x²)": {
        "fn": lambda x: np.exp(-(x**2)),
        "formula": "exp(-x^2)",
        "nota": "Distribución gaussiana clásica.",
    },
    "Raíz Cuadrada: f(x) = √x  (requiere a ≥ 0)": {
        "fn": lambda x: np.sqrt(x),
        "formula": "sqrt(x)",
        "nota": "Función cóncava definida para x ≥ 0.",
    },
    "Logaritmo Natural: f(x) = ln(x)  (requiere a > 0)": {
        "fn": lambda x: np.log(x),
        "formula": "ln(x)",
        "nota": "Definida únicamente para x > 0.",
    },
    "Polinomio: f(x) = 3x² - 2x + 1": {
        "fn": lambda x: 3 * (x**2) - 2 * x + 1,
        "formula": "3x^2 - 2x + 1",
        "nota": "Polinomio cuadrático general.",
    },
}


def areatrapecio(y0, y1, dx):
    return ((y1 + y0) * dx) / 2.0


def metodo_trapecios(fn, a, b, N):
    """Calcula el área bajo la curva usando N trapecios (N + 1 puntos)."""
    X = np.linspace(a, b, N + 1)
    with np.errstate(all="ignore"):
        Y = fn(X)
    dx = (b - a) / N
    area_total = float(np.sum(areatrapecio(Y[:-1], Y[1:], dx)))
    return area_total, X, Y, dx


def integral_referencia_simpson(fn, a, b, n_ref=100000):
    """Calcula el valor exacto de referencia con Simpson 1/3 de alta precisión."""
    if n_ref % 2 != 0:
        n_ref += 1
    X_ref = np.linspace(a, b, n_ref + 1)
    with np.errstate(all="ignore"):
        Y_ref = fn(X_ref)
    h = (b - a) / n_ref
    return float(
        (h / 3.0)
        * (Y_ref[0] + Y_ref[-1] + 4.0 * np.sum(Y_ref[1:-1:2]) + 2.0 * np.sum(Y_ref[2:-1:2]))
    )


# --- Estado inicial confirmado (no cambia hasta pulsar el botón) ---
if "config_confirmada" not in st.session_state:
    st.session_state.config_confirmada = {
        "nombre_fn": "Exponencial: f(x) = exp(x)",
        "a": 0.0,
        "b": 6.0,
        "N": 10,
    }

# --- Encabezado principal ---
st.markdown(
    """
    <div class="hero-box">
        <h1 class="hero-title">Simulador del Método de los Trapecios</h1>
        <p class="hero-sub">
            Selecciona una función de la lista, ajusta los límites <strong>[a, b]</strong> y el número de segmentos <strong>N</strong>,
            y presiona <span style="color:#34d399;font-weight:700;">Confirmar Cambios y Calcular</span> para actualizar los gráficos.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Barra lateral con Formulario (evita recálculo automático) ---
with st.sidebar:
    st.markdown("### Panel de Configuración")
    st.markdown(
        "<p style='color:#cbd5e1;font-size:0.85rem;'>Realiza tus cambios y confirma con el botón inferior.</p>",
        unsafe_allow_html=True,
    )

    with st.form("form_trapecios"):
        lista_nombres = list(FUNCIONES_DISPONIBLES.keys())
        idx_actual = lista_nombres.index(st.session_state.config_confirmada["nombre_fn"])

        nombre_seleccionado = st.selectbox(
            "Elige la función f(x):",
            options=lista_nombres,
            index=idx_actual,
        )
        a_input = st.number_input(
            "Límite inferior (a):",
            value=float(st.session_state.config_confirmada["a"]),
            format="%.4f",
        )
        b_input = st.number_input(
            "Límite superior (b):",
            value=float(st.session_state.config_confirmada["b"]),
            format="%.4f",
        )
        n_input = st.number_input(
            "Número de segmentos (N):",
            min_value=1,
            max_value=1000000,
            value=int(st.session_state.config_confirmada["N"]),
            step=1,
        )

        confirmar = st.form_submit_button("Confirmar Cambios y Calcular")

    if confirmar:
        st.session_state.config_confirmada = {
            "nombre_fn": nombre_seleccionado,
            "a": float(a_input),
            "b": float(b_input),
            "N": int(n_input),
        }
        st.success("Parámetros confirmados y actualizados.")

# Usar siempre los últimos valores confirmados
cfg = st.session_state.config_confirmada
nombre_fn = cfg["nombre_fn"]
a = cfg["a"]
b = cfg["b"]
N_usuario = cfg["N"]
info_fn = FUNCIONES_DISPONIBLES[nombre_fn]
fn = info_fn["fn"]

# --- Validaciones de intervalo y dominio ---
if a >= b:
    st.error(f"Error en límites: 'a' ({a}) debe ser estrictamente menor que 'b' ({b}). Modifica los límites y presiona Confirmar.")
    st.stop()

area_usuario, X_trap, Y_trap, dx_usuario = metodo_trapecios(fn, a, b, N_usuario)
valor_exacto = integral_referencia_simpson(fn, a, b)

if not (np.all(np.isfinite(Y_trap)) and np.isfinite(area_usuario) and np.isfinite(valor_exacto)):
    st.error(
        f"La función '{info_fn['formula']}' no está definida o diverge en algún punto de [{a}, {b}]. "
        "Revisa el dominio (por ejemplo, √x requiere a ≥ 0 y ln(x) requiere a > 0) y presiona Confirmar."
    )
    st.stop()

error_abs = abs(area_usuario - valor_exacto)
error_rel = (error_abs / abs(valor_exacto) * 100.0) if abs(valor_exacto) > 1e-12 else 0.0

# --- Módulo de Tarjetas Métricas Coloridas ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""
        <div class="kpi-card kpi-cyan">
            <div class="kpi-label" style="color:#22d3ee;">ÁREA APROXIMADA (TRAPECIOS)</div>
            <div class="kpi-value" style="color:#67e8f9;">{area_usuario:.6f}</div>
            <div class="kpi-foot">N = {N_usuario:,} · Δx = {dx_usuario:.5f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""
        <div class="kpi-card kpi-green">
            <div class="kpi-label" style="color:#34d399;">VALOR EXACTO (REFERENCIA)</div>
            <div class="kpi-value" style="color:#6ee7b7;">{valor_exacto:.6f}</div>
            <div class="kpi-foot">f(x) = {info_fn['formula']} en [{a}, {b}]</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"""
        <div class="kpi-card kpi-rose">
            <div class="kpi-label" style="color:#fb7185;">ERROR ABSOLUTO |A - I|</div>
            <div class="kpi-value" style="color:#fda4af;">{error_abs:.4e}</div>
            <div class="kpi-foot">Diferencia respecto al valor exacto</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f"""
        <div class="kpi-card kpi-amber">
            <div class="kpi-label" style="color:#fbbf24;">ERROR RELATIVO (%)</div>
            <div class="kpi-value" style="color:#fde68a;">{error_rel:.4f}%</div>
            <div class="kpi-foot">{info_fn['nota']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- Módulos de Visualización en Pestañas ---
tab_trap, tab_conv, tab_tabla = st.tabs(
    ["Gráfico de Trapecios", "Convergencia Logarítmica", "Tabla de Resultados"]
)

with tab_trap:
    st.markdown(
        '<span class="module-badge" style="background:#083344;color:#22d3ee;border:1px solid #06b6d4;">Módulo 1 · Visualización Geométrica bajo la Curva</span>',
        unsafe_allow_html=True,
    )
    fig1, ax1 = plt.subplots(figsize=(11, 5))
    fig1.patch.set_facecolor("#0f172a")
    ax1.set_facecolor("#1e293b")

    X_suave = np.linspace(a, b, 500)
    Y_suave = fn(X_suave)
    ax1.plot(X_suave, Y_suave, color="#22d3ee", linewidth=2.5, label=f"Curva f(x) = {info_fn['formula']}")

    if N_usuario <= 120:
        X_vis, Y_vis = X_trap, Y_trap
    else:
        X_vis = np.linspace(a, b, 121)
        Y_vis = fn(X_vis)
        st.info("Se muestran 120 trapecios representativos en el dibujo para mantener la claridad visual.")

    for i in range(len(X_vis) - 1):
        es_positivo = (Y_vis[i] + Y_vis[i + 1]) >= 0
        color_relleno = "#38bdf8" if es_positivo else "#fb7185"
        color_borde = "#facc15" if i % 2 == 0 else "#34d399"
        verts = [
            (X_vis[i], 0),
            (X_vis[i], Y_vis[i]),
            (X_vis[i + 1], Y_vis[i + 1]),
            (X_vis[i + 1], 0),
        ]
        ax1.add_patch(Polygon(verts, facecolor=color_relleno, edgecolor=color_borde, alpha=0.32, linewidth=1.1))

    ax1.axhline(0, color="#94a3b8", linewidth=1.0)
    ax1.set_title(
        f"Método de los Trapecios · {info_fn['formula']}  (N = {N_usuario}, Δx = {dx_usuario:.4f})",
        color="#fde047",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax1.set_xlabel("x", color="#38bdf8", fontsize=11, fontweight="bold")
    ax1.set_ylabel("f(x)", color="#34d399", fontsize=11, fontweight="bold")
    ax1.tick_params(colors="#cbd5e1")
    for spine in ax1.spines.values():
        spine.set_color("#475569")
    ax1.grid(True, linestyle="--", color="#475569", alpha=0.5)
    leg1 = ax1.legend(facecolor="#0f172a", edgecolor="#38bdf8")
    for text in leg1.get_texts():
        text.set_color("#f8fafc")

    st.pyplot(fig1)
    plt.close(fig1)

with tab_conv:
    st.markdown(
        '<span class="module-badge" style="background:#064e3b;color:#34d399;border:1px solid #10b981;">Módulo 2 · Convergencia en Escala Logarítmica</span>',
        unsafe_allow_html=True,
    )
    lista_n = [10, 100, 1000, 10000, 100000]
    areas_obtenidas = [metodo_trapecios(fn, a, b, n)[0] for n in lista_n]
    errores = [abs(area - valor_exacto) for area in areas_obtenidas]

    fig2, ax2 = plt.subplots(figsize=(11, 5))
    fig2.patch.set_facecolor("#0f172a")
    ax2.set_facecolor("#1e293b")
    ax2.set_xscale("log")

    ax2.axhline(
        y=valor_exacto,
        color="#fb7185",
        linestyle="solid",
        linewidth=2.2,
        label=f"Valor exacto ≈ {valor_exacto:.6f}",
    )
    ax2.plot(lista_n, areas_obtenidas, "--", color="#fbbf24", linewidth=1.8, alpha=0.85)
    ax2.scatter(lista_n, areas_obtenidas, color="#34d399", edgecolor="#022c22", s=95, zorder=5, label="Área por trapecios")

    ax2.set_xlabel("Valor de N en Escala Logarítmica", color="#38bdf8", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Área aproximada obtenida", color="#34d399", fontsize=11, fontweight="bold")
    ax2.set_title(
        f"Convergencia Logarítmica para f(x) = {info_fn['formula']}",
        color="#fde047",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax2.tick_params(colors="#cbd5e1")
    for spine in ax2.spines.values():
        spine.set_color("#475569")
    ax2.grid(True, which="both", linestyle="--", color="#475569", alpha=0.5)
    leg2 = ax2.legend(facecolor="#0f172a", edgecolor="#10b981")
    for text in leg2.get_texts():
        text.set_color("#f8fafc")

    st.pyplot(fig2)
    plt.close(fig2)

with tab_tabla:
    st.markdown(
        '<span class="module-badge" style="background:#451a03;color:#fbbf24;border:1px solid #f59e0b;">Módulo 3 · Comparativa Numérica por N</span>',
        unsafe_allow_html=True,
    )
    lista_n = [10, 100, 1000, 10000, 100000]
    areas_tabla = [metodo_trapecios(fn, a, b, n)[0] for n in lista_n]
    errores_tabla = [abs(area - valor_exacto) for area in areas_tabla]

    st.dataframe(
        {
            "N (Segmentos)": lista_n,
            "Puntos (N + 1)": [n + 1 for n in lista_n],
            "Δx = (b - a) / N": [(b - a) / n for n in lista_n],
            "Área Aproximada": areas_tabla,
            "Error Absoluto": errores_tabla,
        },
        use_container_width=True,
    )
