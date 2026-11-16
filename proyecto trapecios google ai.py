import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

st.set_page_config(
    page_title="Método de los Trapecios",
    layout="wide",
)


def evaluar_funcion(expr, x):
    """Evalúa de forma segura la función matemática ingresada por el usuario."""
    entorno = {
        "x": x,
        "np": np,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "arcsin": np.arcsin,
        "arccos": np.arccos,
        "arctan": np.arctan,
        "exp": np.exp,
        "log": np.log,
        "ln": np.log,
        "log10": np.log10,
        "sqrt": np.sqrt,
        "abs": np.abs,
        "pi": np.pi,
        "e": np.e,
    }
    expr_py = expr.replace("^", "**")
    resultado = eval(expr_py, {"__builtins__": {}}, entorno)

    if np.ndim(x) > 0 and np.ndim(resultado) == 0:
        return np.full_like(x, float(resultado), dtype=float)
    return resultado


def areatrapecio(y0, y1, dx):
    return ((y1 + y0) * dx) / 2.0


def metodo_trapecios(expr, a, b, N):
    """Calcula el área bajo la curva usando N trapecios (N + 1 puntos)."""
    X = np.linspace(a, b, N + 1)
    Y = evaluar_funcion(expr, X)
    dx = (b - a) / N
    # Suma vectorizada equivalente al bucle for i in range(N)
    area_total = float(np.sum(areatrapecio(Y[:-1], Y[1:], dx)))
    return area_total, X, Y, dx


def integral_referencia_simpson(expr, a, b, n_ref=100000):
    """Valor de referencia de alta precisión mediante la regla de Simpson 1/3."""
    if n_ref % 2 != 0:
        n_ref += 1
    X_ref = np.linspace(a, b, n_ref + 1)
    Y_ref = evaluar_funcion(expr, X_ref)
    h = (b - a) / n_ref
    return float(
        (h / 3.0)
        * (Y_ref[0] + Y_ref[-1] + 4.0 * np.sum(Y_ref[1:-1:2]) + 2.0 * np.sum(Y_ref[2:-1:2]))
    )


st.title("Calculadora del Método de los Trapecios")
st.markdown(
    "Ingresa una función $f(x)$, los límites de integración $[a, b]$ y el número de segmentos $N$."
)

# --- Barra lateral de parámetros ---
with st.sidebar:
    st.header("Parámetros de Integración")
    expr = st.text_input(
        "Función f(x)",
        value="exp(x)",
        help="Ejemplos: exp(x), sin(x), x^2 + 3*x, 1/(1+x^2), sqrt(x)",
    )
    a = st.number_input("Límite inferior (a)", value=0.0, format="%.4f")
    b = st.number_input("Límite superior (b)", value=6.0, format="%.4f")
    N_usuario = st.number_input(
        "Número de segmentos (N)",
        min_value=1,
        max_value=1000000,
        value=10,
        step=1,
    )
    st.caption("Funciones disponibles: exp, sin, cos, tan, sqrt, log, ln, abs, pi, e")

if a >= b:
    st.error("El límite inferior (a) debe ser estrictamente menor que el límite superior (b).")
    st.stop()

# --- Cálculo principal ---
try:
    area_usuario, X_trap, Y_trap, dx_usuario = metodo_trapecios(expr, a, b, int(N_usuario))
    valor_exacto = integral_referencia_simpson(expr, a, b)
    error_abs = abs(area_usuario - valor_exacto)
    error_rel = (error_abs / abs(valor_exacto) * 100.0) if abs(valor_exacto) > 1e-12 else 0.0
except Exception as err:
    st.error(f"No se pudo evaluar la función '{expr}' en [{a}, {b}]: {err}")
    st.stop()

# --- Métricas ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Área Aproximada (Trapecios)", f"{area_usuario:.6f}")
col2.metric("Valor Exacto (Referencia)", f"{valor_exacto:.6f}")
col3.metric("Error Absoluto", f"{error_abs:.4e}")
col4.metric("Error Relativo (%)", f"{error_rel:.4f}%")

# --- Gráficos ---
tab_trap, tab_conv = st.tabs(["Visualización de Trapecios", "Convergencia Logarítmica"])

with tab_trap:
    fig1, ax1 = plt.subplots(figsize=(10, 4.8))
    X_suave = np.linspace(a, b, 500)
    Y_suave = evaluar_funcion(expr, X_suave)
    ax1.plot(X_suave, Y_suave, color="#0284c7", linewidth=2, label=f"f(x) = {expr}")

    if N_usuario <= 120:
        X_vis, Y_vis = X_trap, Y_trap
    else:
        X_vis = np.linspace(a, b, 121)
        Y_vis = evaluar_funcion(expr, X_vis)
        st.info("Para mantener legible el gráfico, se muestran 120 trapecios representativos.")

    for i in range(len(X_vis) - 1):
        verts = [
            (X_vis[i], 0),
            (X_vis[i], Y_vis[i]),
            (X_vis[i + 1], Y_vis[i + 1]),
            (X_vis[i + 1], 0),
        ]
        ax1.add_patch(Polygon(verts, facecolor="#38bdf8", edgecolor="#0369a1", alpha=0.3))

    ax1.axhline(0, color="black", linewidth=0.8)
    ax1.set_title(f"Método de los Trapecios (N = {int(N_usuario)}, Δx = {dx_usuario:.4f})")
    ax1.set_xlabel("x")
    ax1.set_ylabel("f(x)")
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend()
    st.pyplot(fig1)
    plt.close(fig1)

with tab_conv:
    lista_n = [10, 100, 1000, 10000, 100000]
    areas_obtenidas = [metodo_trapecios(expr, a, b, n)[0] for n in lista_n]
    errores = [abs(area - valor_exacto) for area in areas_obtenidas]

    fig2, ax2 = plt.subplots(figsize=(10, 4.8))
    ax2.set_xscale("log")
    ax2.axhline(
        y=valor_exacto,
        color="red",
        linestyle="solid",
        linewidth=1.8,
        label=f"Valor exacto ≈ {valor_exacto:.6f}",
    )
    ax2.plot(lista_n, areas_obtenidas, "--", color="#10b981", alpha=0.7)
    ax2.scatter(lista_n, areas_obtenidas, color="#059669", zorder=5, label="Área aproximada")
    ax2.set_xlabel("Valor de N en Escala Logarítmica")
    ax2.set_ylabel("Área aproximada obtenida")
    ax2.set_title("Convergencia del Método de los Trapecios")
    ax2.grid(True, which="both", linestyle="--", alpha=0.4)
    ax2.legend()
    st.pyplot(fig2)
    plt.close(fig2)

    st.subheader("Tabla de Convergencia")
    st.dataframe(
        {
            "N (Segmentos)": lista_n,
            "Δx": [(b - a) / n for n in lista_n],
            "Área Aproximada": areas_obtenidas,
            "Error Absoluto": errores,
        },
        use_container_width=True,
    )