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
# SCRITTA "MENU" ACCANTO ALL’ICONA DELLA SIDEBAR
# (versione compatibile con Streamlit 1.30+)
# ---------------------------------------------------------
st.markdown("""
<style>

/* Scritta MENU accanto al pulsante della sidebar */
[data-testid="collapsedControl"] button svg {
    margin-right: 6px;
}

[data-testid="collapsedControl"] button::after {
    content: " Menu";
    font-size: 16px;
    font-weight: 600;
    color: #444;
}

/* Allineamento */
[data-testid="collapsedControl"] button {
    display: flex;
    align-items: center;
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
st.sidebar.image("static/varcaturopadel.png", width=120)
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
# PWA (puoi rimuoverla se vuoi evitare conflitti)
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
# ONBOARDING
# ---------------------------------------------------------
if "onboarding_done" not in st.session_state:
    st.session_state.onboarding_done = False

if not st.session_state.onboarding_done:

    st.image("static/varcaturopadel.png", width=90)

    st.markdown("""
    <div class="fade-in" style="
        background: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        max-width: 400px;
        margin: 4rem auto;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
    ">
        <h2 style="margin-bottom: 0.5rem;">Benvenuto in Tornei Padel</h2>
        <p style="font-size: 17px; color: #6E6E73;">
            Organizza tornei, crea squadre e genera partite in modo semplice e veloce.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Inizia"):
        st.session_state.onboarding_done = True
        st.rerun()

    st.stop()

# ---------------------------------------------------------
# HEADER PAGINA PRINCIPALE
# ---------------------------------------------------------
col1, col2 = st.columns([1, 10])
with col1:
    st.image("static/varcaturopadel.png", width=50)
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
