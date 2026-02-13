import streamlit as st
import pandas as pd
import numpy as np
import json
from io import BytesIO


def get_solver(num_turni):
    if num_turni == 8:
        from .logiche.logica_draft12_8turni import solve_draft12
    else:
        from .logiche.logica_draft12_11turni import solve_draft12
    return solve_draft12



# ---------------------------------------------------------
# COMPONENTI GRAFICI
# ---------------------------------------------------------
def render_match_card(turno, campo, coppiaA, coppiaB, risultato):
    st.markdown(
        f"""
    <div class="match-card">
        <div class="match-title">Turno {turno} — Campo {campo}</div>
        <div class="match-team">A: {coppiaA}</div>
        <div class="match-team">B: {coppiaB}</div>
        <div class="match-result">Risultato: {risultato if risultato else "—"}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )



def render_classifica(df):
    for player, row in df.iterrows():
        st.markdown(
            f"""
        <div class="classifica-row">
            <div class="classifica-name">{player}</div>
            <div class="classifica-points">{row['Punti']} pts</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# METRICHE
# ---------------------------------------------------------
def calcola_metriche(df_cal, names):
    n = len(names)
    compagni = np.zeros((n, n), dtype=int)
    avversari = np.zeros((n, n), dtype=int)

    idx = {name: i for i, name in enumerate(names)}

    for _, row in df_cal.iterrows():
        a1, a2 = row["Coppia A"].split(" & ")
        b1, b2 = row["Coppia B"].split(" & ")

        i1, i2 = idx[a1], idx[a2]
        j1, j2 = idx[b1], idx[b2]

        compagni[i1, i2] += 1
        compagni[i2, i1] += 1
        compagni[j1, j2] += 1
        compagni[j2, j1] += 1

        for x in [i1, i2]:
            for y in [j1, j2]:
                avversari[x, y] += 1
                avversari[y, x] += 1

    return (
        pd.DataFrame(compagni, index=names, columns=names),
        pd.DataFrame(avversari, index=names, columns=names),
    )


# ---------------------------------------------------------
# CLASSIFICA
# ---------------------------------------------------------
def calcola_classifica(df_cal, names):
    classifica = {
        nome: {"Punti": 0, "Game_vinti": 0, "Game_persi": 0, "Diff_game": 0}
        for nome in names
    }

    for _, row in df_cal.iterrows():
        if not row["Risultato"]:
            continue

        try:
            ga, gb = map(int, row["Risultato"].replace(" ", "").split("-"))
        except Exception:
            continue

        a1, a2 = row["Coppia A"].split(" & ")
        b1, b2 = row["Coppia B"].split(" & ")

        for p in [a1, a2]:
            classifica[p]["Punti"] += ga
            classifica[p]["Game_vinti"] += ga
            classifica[p]["Game_persi"] += gb

        for p in [b1, b2]:
            classifica[p]["Punti"] += gb
            classifica[p]["Game_vinti"] += gb
            classifica[p]["Game_persi"] += ga

    for p in classifica:
        classifica[p]["Diff_game"] = (
            classifica[p]["Game_vinti"] - classifica[p]["Game_persi"]
        )

    df = pd.DataFrame.from_dict(classifica, orient="index")
    df.index.name = "Giocatore"
    return df.sort_values(by=["Punti", "Diff_game", "Game_vinti"], ascending=False)


# ---------------------------------------------------------
# UI PRINCIPALE
# ---------------------------------------------------------
def run():
    st.header("Draft 12 giocatori")

    # ---------------------------------------------------------
    # CARICAMENTO TORNEO
    # ---------------------------------------------------------
    st.subheader("📂 Carica torneo salvato")
    uploaded = st.file_uploader("Carica file JSON del torneo", type="json")
    if uploaded:
        data = json.load(uploaded)
        st.session_state.draft12_calendario = pd.DataFrame(data["calendario"])
        st.session_state.draft12_risultati = data["risultati"]
        st.session_state.draft12_giocatori = data["giocatori"]
        st.success("Torneo caricato!")

    # ---------------------------------------------------------
    # INSERIMENTO GIOCATORI
    # ---------------------------------------------------------
    if "draft12_giocatori" not in st.session_state:
        with st.form("draft12_giocatori_form"):
            giocatori = []
            col1, col2 = st.columns(2)

            with col1:
                for i in range(1, 7):
                    giocatori.append(st.text_input(f"Giocatore {i}", value=f"G{i}"))

            with col2:
                for i in range(7, 13):
                    giocatori.append(st.text_input(f"Giocatore {i}", value=f"G{i}"))

            conferma = st.form_submit_button("Conferma giocatori")

        if conferma:
            st.session_state.draft12_giocatori = giocatori
            st.rerun()

        st.stop()

    giocatori = st.session_state.draft12_giocatori

    num_turni = st.selectbox("Numero di turni", [8, 11], index=0)

    # ---------------------------------------------------------
    # GENERA CALENDARIO
    # ---------------------------------------------------------
    if st.button("Genera calendario draft 12"):
        solve = get_solver(num_turni)
        st.session_state.draft12_calendario = solve(giocatori, num_turni)

        st.session_state.draft12_risultati = [""] * len(st.session_state.draft12_calendario)

    if "draft12_calendario" not in st.session_state:
        return

    df_cal = st.session_state.draft12_calendario.copy()

    # ---------------------------------------------------------
    # RISULTATI
    # ---------------------------------------------------------
    st.subheader("Risultati")

    for i in range(len(df_cal)):
        label = (
            f"Turno {df_cal.loc[i,'Turno']} - Campo {df_cal.loc[i,'Campo']}: "
            f"{df_cal.loc[i,'Coppia A']} vs {df_cal.loc[i,'Coppia B']}"
        )
        st.session_state.draft12_risultati[i] = st.text_input(
            label,
            value=st.session_state.draft12_risultati[i],
            key=f"draft12_ris_{i}",
        )

    df_cal["Risultato"] = st.session_state.draft12_risultati

    # ---------------------------------------------------------
    # CARD + TABELLA
    # ---------------------------------------------------------
    st.subheader("Partite (card)")
    for _, row in df_cal.iterrows():
        col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 3, 2])
        col1.write(f"Turno {row['Turno']}")
        col2.write(f"Campo {row['Campo']}")
        col3.write(row["Coppia A"])
        col4.write(row["Coppia B"])
        col5.write(row["Risultato"] or "—")

    st.subheader("Calendario (tabella)")
    st.dataframe(df_cal, use_container_width=True)

    # ---------------------------------------------------------
    # METRICHE
    # ---------------------------------------------------------
    st.subheader("Metriche")
    df_comp, df_avv = calcola_metriche(df_cal, giocatori)

    st.markdown("#### Compagni")
    st.dataframe(df_comp.style.background_gradient(cmap="Blues"))

    st.markdown("#### Avversari")
    st.dataframe(df_avv.style.background_gradient(cmap="Oranges"))

    # ---------------------------------------------------------
    # CLASSIFICA
    # ---------------------------------------------------------
    st.subheader("🏆 Classifica")

    df_classifica = calcola_classifica(df_cal, giocatori)

    # Tabella leggibile con CSS migliorato
    st.dataframe(df_classifica, use_container_width=True)

    # ---------------------------------------------------------
    # TOOLBAR (ONE-CLICK)
    # ---------------------------------------------------------
    st.subheader("Azioni torneo")

    colA, colB, colC = st.columns(3)

    # 🔄 RIGENERA TORNEO
    with colA:
        if st.button("🔄 Rigenera torneo"):
            st.session_state.clear()
            st.rerun()

    # 💾 SALVA TORNEO
    with colB:
        data = {
            "giocatori": giocatori,
            "calendario": df_cal.to_dict(orient="records"),
            "risultati": st.session_state.draft12_risultati,
        }
        st.download_button(
            "💾 Salva torneo",
            data=json.dumps(data).encode("utf-8"),
            file_name="torneo_draft12.json",
            mime="application/json",
            key="download_json",
        )

    # 📊 ESPORTA EXCEL
    with colC:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_cal.to_excel(writer, sheet_name="Calendario", index=False)
            df_comp.to_excel(writer, sheet_name="Compagni")
            df_avv.to_excel(writer, sheet_name="Avversari")
            df_classifica.to_excel(writer, sheet_name="Classifica")

        st.download_button(
            "📊 Esporta Excel",
            data=output.getvalue(),
            file_name="draft12_completo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel",
        )
