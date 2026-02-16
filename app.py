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
# CSS BOTTONE 3D + MENU A SINISTRA
# ---------------------------------------------------------
st.markdown("""
<style>

/* ----------------------------- */
/* 1) BOTTONE 3D TORNEI PADEL    */
/* ----------------------------- */
.title-container button {
    background: linear-gradient(180deg, #1e88e5 0%, #1565c0 100%) !important;
    color: white !important;
    padding: 16px 28px !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    border: none !important;
    cursor: pointer !important;
    box-shadow: 0px 6px 0px #0d47a1 !important;
    transition: all 0.15s ease-in-out !important;
    width: 100% !important;
}

/* Effetto pressione */
.title-container button:active {
    box-shadow: 0px 2px 0px #0d47a1 !important;
    transform: translateY(4px) !important;
}

/* Hover su desktop */
@media (min-width: 600px) {
    .title-container button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0px 8px 0px #0d47a1 !important;
    }
}

/* ----------------------------- */
/* 2) MENU A SINISTRA            */
/* ----------------------------- */
header [data-testid="stToolbar"] button {
    position: absolute !important;
    left: 10px !important;
    top: 10px !important;
    z-index: 9999 !important;
}

header [data-testid="stToolbar"] button::after {
    content: " MENU";
    font-size: 18px;
    font-weight: 600;
    margin-left: 6px;
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
# ONBOARDING CENTRATO
# ---------------------------------------------------------
if "onboarding_done" not in st.session_state:
    st.session_state.onboarding_done = False

if not st.session_state.onboarding_done:

    st.markdown("""
    <div style="text-align:center; margin-top:40px;">
        <img src="static/torneipadel320.png" width="140" style="margin-bottom:20px;">
        <h2 style="margin-bottom: 0.5rem;">Benvenuto in Tornei Padel</h2>
        <p style="font-size: 17px; color: #6E6E73;">
            Organizza tornei, crea squadre e genera partite in modo semplice e veloce.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    if st.button("Inizia", key="start_button"):
        st.session_state.onboarding_done = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# BOTTONE 3D "TORNEI PADEL" CENTRALE
# ---------------------------------------------------------
st.markdown("<div class='title-container'>", unsafe_allow_html=True)
home_clicked = st.button("Tornei Padel", key="home_button")
st.markdown("</div>", unsafe_allow_html=True)

if home_clicked:
    st.session_state["page"] = "home"

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
