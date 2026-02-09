import streamlit as st
import pandas as pd
from io import BytesIO
from .logiche.logica_torneo_squadre import genera_torneo_squadre

def run():
    st.header("🏅 Torneo a squadre")

    st.markdown("Inserisci i nomi delle squadre e dei giocatori.")

    # Input squadre
    squadre = []
    for i in range(4):
        squadre.append(st.text_input(f"Nome squadra {i+1}", value=f"Squadra {i+1}"))

    # Input giocatori
    nomi_giocatori = {}
    for squadra in squadre:
        st.subheader(f"👥 Giocatori {squadra}")

        col1, col2 = st.columns(2)

        with col1:
            u1 = st.text_input(f"{squadra} - Uomo 1")
            u2 = st.text_input(f"{squadra} - Uomo 2")
            u3 = st.text_input(f"{squadra} - Uomo 3")

        with col2:
            d1 = st.text_input(f"{squadra} - Donna 1")
            d2 = st.text_input(f"{squadra} - Donna 2")
            d3 = st.text_input(f"{squadra} - Donna 3")

        nomi_giocatori[squadra] = [u1, u2, u3, d1, d2, d3]

    if st.button("🚀 Genera calendario"):
        risultati = genera_torneo_squadre(nomi_giocatori)

        df_cal = risultati["calendario"]
        df_ctrl = risultati["controllo"]
        df_comp = risultati["compagni"]
        df_ms = risultati["metriche_squadra"]
        df_mg = risultati["metriche_giocatore"]
        df_pct = risultati["percentuali"]

        st.success("🎉 Calendario generato con successo!")
        st.balloons()

        # Tabs
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

        # Download Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_cal.to_excel(writer, sheet_name="Calendario", index=False)
            df_ctrl.to_excel(writer, sheet_name="Controllo", index=False)
            df_comp.to_excel(writer, sheet_name="Compagni", index=False)
            df_ms.to_excel(writer, sheet_name="Metriche_squadre", index=False)
            df_mg.to_excel(writer, sheet_name="Metriche_giocatori", index=False)
            df_pct.to_excel(writer, sheet_name="Percentuali", index=False)

        st.download_button(
            label="⬇️ Scarica Excel",
            data=output.getvalue(),
            file_name="torneo_squadre.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
