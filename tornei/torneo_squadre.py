import streamlit as st
import pandas as pd
from io import BytesIO
import json

from .logiche.logica_torneo_squadre import genera_torneo_squadre


def run():
    # ---------------------------------------------------------
    # TITOLO CON NOME TORNEO
    # ---------------------------------------------------------
    nome = st.session_state.get("ts_nome", "Torneo a squadre")

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:14px; margin:20px 0;">
        <span style="font-size:42px;">🎾</span>
        <h1 style="margin:0; font-weight:700;">{nome}</h1>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # CARICAMENTO TORNEO SALVATO
    # ---------------------------------------------------------
    st.subheader("📂 Carica torneo salvato")
    uploaded = st.file_uploader("Carica file JSON del torneo", type="json", key="upload_torneo_squadre")

    if uploaded:
        data = json.load(uploaded)
        st.session_state["ts_nome"] = data.get("nome_torneo", "Torneo a squadre")
        st.session_state["ts_squadre"] = data["squadre"]
        st.session_state["ts_giocatori"] = data["giocatori"]
        st.session_state["ts_risultati"] = data["risultati"]
        st.success("Torneo caricato correttamente!")

    # ---------------------------------------------------------
    # INIZIALIZZAZIONE TORNEO
    # ---------------------------------------------------------
    if "ts_squadre" not in st.session_state:

        st.subheader("🏷️ Nome del torneo")
        nome_torneo = st.text_input("Inserisci il nome del torneo", value="Torneo a squadre")

        st.markdown("### Inserisci i nomi delle squadre e dei giocatori.")

        # Input squadre
        squadre = []
        for i in range(4):
            squadre.append(st.text_input(f"Nome squadra {i+1}", value=f"Squadra {i+1}", key=f"squadra_{i}"))

        # Input giocatori
        nomi_giocatori = {}
        for squadra in squadre:
            st.subheader(f"👥 Giocatori {squadra}")

            col1, col2 = st.columns(2)

            with col1:
                u1 = st.text_input(f"{squadra} - Uomo 1", key=f"{squadra}_u1")
                u2 = st.text_input(f"{squadra} - Uomo 2", key=f"{squadra}_u2")
                u3 = st.text_input(f"{squadra} - Uomo 3", key=f"{squadra}_u3")

            with col2:
                d1 = st.text_input(f"{squadra} - Donna 1", key=f"{squadra}_d1")
                d2 = st.text_input(f"{squadra} - Donna 2", key=f"{squadra}_d2")
                d3 = st.text_input(f"{squadra} - Donna 3", key=f"{squadra}_d3")

            nomi_giocatori[squadra] = [u1, u2, u3, d1, d2, d3]

        if st.button("🚀 Genera calendario"):
            risultati = genera_torneo_squadre(nomi_giocatori)

            st.session_state["ts_nome"] = nome_torneo
            st.session_state["ts_squadre"] = squadre
            st.session_state["ts_giocatori"] = nomi_giocatori
            st.session_state["ts_risultati"] = risultati

            st.rerun()

        st.stop()

    # ---------------------------------------------------------
    # TORNEO GIÀ GENERATO O RIPRISTINATO
    # ---------------------------------------------------------
    nome = st.session_state["ts_nome"]
    squadre = st.session_state["ts_squadre"]
    giocatori = st.session_state["ts_giocatori"]
    risultati = st.session_state["ts_risultati"]

    df_cal = risultati["calendario"]
    df_ctrl = risultati["controllo"]
    df_comp = risultati["compagni"]
    df_ms = risultati["metriche_squadra"]
    df_mg = risultati["metriche_giocatore"]
    df_pct = risultati["percentuali"]

    st.success("🎉 Torneo pronto!")

    # ---------------------------------------------------------
    # TABS RISULTATI
    # ---------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📅 Calendario",
        "📊 Controllo giocate",
        "🤝 Compagni",
        "🏆 Metriche squadre",
        "👤 Metriche giocatori",
        "📈 Percentuali"
    ])

    with tab1:
        st.dataframe(df_cal)

    with tab2:
        st.dataframe(df_ctrl)

    with tab3:
        st.dataframe(df_comp)

    with tab4:
        st.dataframe(df_ms)

    with tab5:
        st.dataframe(df_mg)

    with tab6:
        st.dataframe(df_pct)

    # ---------------------------------------------------------
    # SALVATAGGIO TORNEO
    # ---------------------------------------------------------
    st.subheader("💾 Salva torneo")

    data = {
        "nome_torneo": nome,
        "squadre": squadre,
        "giocatori": giocatori,
        "risultati": risultati,
    }

    st.download_button(
        "⬇️ Salva torneo (JSON)",
        data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="torneo_squadre.json",
        mime="application/json",
    )

    # ---------------------------------------------------------
    # ESPORTAZIONE EXCEL
    # ---------------------------------------------------------
    st.subheader("📊 Esporta Excel")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_cal.to_excel(writer, sheet_name="Calendario", index=False)
        df_ctrl.to_excel(writer, sheet_name="Controllo", index=False)
        df_comp.to_excel(writer, sheet_name="Compagni", index=False)
        df_ms.to_excel(writer, sheet_name="Metriche_squadra", index=False)
        df_mg.to_excel(writer, sheet_name="Metriche_giocatore", index=False)
        df_pct.to_excel(writer, sheet_name="Percentuali", index=False)

    st.download_button(
        label="⬇️ Scarica Excel",
        data=output.getvalue(),
        file_name="torneo_squadre.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
