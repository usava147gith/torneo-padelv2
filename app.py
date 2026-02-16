import streamlit as st

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tornei Padel",
    page_icon="static/torneipadel192.png",
    layout="wide"
)

# ---------------------------------------------------------
# CSS START VERDE (CORRETTO)
# ---------------------------------------------------------
st.markdown("""
<style>

/* BOTTONE 3D VERDE START (Streamlit button) */
button.start-btn {
    background: linear-gradient(180deg, #2ecc71 0%, #27ae60 100%) !important;
    color: white !important;
    padding: 14px 26px !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    border: none !important;
    cursor: pointer !important;
    box-shadow: 0px 6px 0px #1e8449 !important;
    transition: all 0.15s ease-in-out !important;
    width: 100% !important;
}

/* Effetto pressione */
button.start-btn:active {
    box-shadow: 0px 2px 0px #1e8449 !important;
    transform: translateY(4px) !important;
}

/* Hover su desktop */
@media (min-width: 600px) {
    button.start-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0px 8px 0px #1e8449 !important;
    }
}

</style>
""", unsafe_allow_html=True)



# ---------------------------------------------------------
# CSS AUTOSIZE TABELLA
# ---------------------------------------------------------
st.markdown("""
<style>
table {
    width: 100% !important;
}

td, th {
    white-space: normal !important;
    word-wrap: break-word !important;
    max-width: 120px;
}

@media (max-width: 600px) {
    td, th {
        font-size: 13px !important;
    }
}
</style>
""", unsafe_allow_html=True)



# ---------------------------------------------------------
# VIEWPORT MOBILE
# ---------------------------------------------------------
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1">
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOGO SIDEBAR
# ---------------------------------------------------------
st.sidebar.image("static/torneipadel320.png", width=120)
st.sidebar.title("🎾 Tornei Padel")

# ---------------------------------------------------------
# CSS ESTERNO
# ---------------------------------------------------------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------
# CSS INLINE
# ---------------------------------------------------------
st.markdown("""
<style>
label, .stTextInput label, .stSelectbox label {
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    color: #333 !important;
}
input[type="text"], input[type="number"] {
    font-size: 1.1rem !important;
    padding: 8px 10px !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    font-size: 1.1rem !important;
}
.dataframe th {
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    background-color: #f2f2f2 !important;
    padding: 12px !important;
    text-align: center !important;
}
.dataframe td {
    font-size: 1.1rem !important;
    padding: 10px !important;
    text-align: center !important;
}
.dataframe {
    border-collapse: separate !important;
    border-spacing: 0 8px !important;
}
.dataframe tbody tr {
    background-color: #ffffff !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
}
.dataframe tbody tr:hover {
    background-color: #fafafa !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PWA
# ---------------------------------------------------------
st.markdown("""
<link rel="manifest" href="manifest.json">
<script>
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register("service-worker.js");
    });
}
</script>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ONBOARDING CENTRATO (VERSIONE DEFINITIVA)
# ---------------------------------------------------------
if "onboarding_done" not in st.session_state:
    st.session_state.onboarding_done = False

if not st.session_state.onboarding_done:

    # Logo centrato
    st.markdown("<div style='text-align:center; margin-top:40px;'>", unsafe_allow_html=True)
    st.image("static/torneipadel192.png", width=120)
    st.markdown("</div>", unsafe_allow_html=True)

    # Bottone "Start" centrato con stile 3D verde
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_clicked = st.button("Start", key="start_button")

    # Applica la classe CSS al bottone Streamlit
    st.markdown("""
    <script>
    const btn = window.parent.document.querySelector('button[kind="secondary"]');
    if (btn) { btn.classList.add('start-btn'); }
    </script>
    """, unsafe_allow_html=True)

    if start_clicked:
        st.session_state.onboarding_done = True
        st.rerun()


    st.stop()

# ---------------------------------------------------------
# HEADER PAGINA PRINCIPALE
# ---------------------------------------------------------
col1, col2 = st.columns([1, 10])
with col1:
    st.image("static/torneipadel320.png", width=50)
with col2:
    st.markdown("<h1 style='margin:0;'>Tornei Padel</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# IMPORT TORNEI
# ---------------------------------------------------------
from tornei.torneo_squadre import run as run_torneo_squadre
from tornei.draft12 import run as run_draft12
from tornei.draft16 import run as run_draft16
from tornei.draft16_misto import run as run_draft16_misto
from tornei.campionato import run_campionato

# ---------------------------------------------------------
# SIDEBAR MENU
# ---------------------------------------------------------
st.sidebar.markdown("Seleziona il tipo di torneo")
scelta = st.sidebar.radio(
    "Seleziona un torneo",
    [
        "Torneo a squadre",
        "Draft 12 giocatori",
        "Draft 16 giocatori",
        "Draft misto 16 giocatori",
        "Campionato a squadre"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.info("V1.0 by Ugo Savarese")

# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------
if scelta == "Campionato a squadre":

    formato = st.sidebar.radio(
        "Formato campionato",
        ["12 squadre", "16 squadre", "20 squadre"]
    )

    if formato == "12 squadre":
        run_campionato(num_squadre=12)
    elif formato == "16 squadre":
        run_campionato(num_squadre=16)
    elif formato == "20 squadre":
        run_campionato(num_squadre=20)

    st.stop()

elif scelta == "Draft 12 giocatori":
    run_draft12()

elif scelta == "Draft 16 giocatori":
    run_draft16()

elif scelta == "Draft misto 16 giocatori":
    run_draft16_misto()

elif scelta == "Torneo a squadre":
    run_torneo_squadre()

else:
    st.markdown("Benvenuto! Scegli il tipo di torneo dalla barra laterale.")
