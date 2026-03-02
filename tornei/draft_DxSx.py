import streamlit as st
import pandas as pd
import numpy as np
import json
from io import BytesIO

# importa le logiche (assumi che esistano i due moduli)
from .logiche.logica_draft16_DxSx import solve_draft16
from .logiche.logica_draft12_DxSx import solve_draft12

# ---------------------------------------------------------
# COMPONENTI GRAFICI
# ---------------------------------------------------------
def render_match_card(turno, campo, coppiaA, coppiaB, risultato):
    st.markdown(
        f"""
        <div class="match-card">
            <div class="match-title">Turno {turno} — Campo {campo}</div>
            <div>A: {coppiaA}</div>
            <div>B: {coppiaB}</div>
            <div>Risultato: {risultato if risultato else "—"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_classifica_premium(df):
    for player, row in df.iterrows():
        diff = row["Diff_game"]
        st.markdown(
            f"""
            <div class="classifica-card">
                <div class="classifica-name">{player}</div>
                <div>
                    <span class="classifica-points">{row['Punti']} pts</span>
                    <span class="classifica-diff">{'+' if diff>=0 else ''}{diff}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
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
        if not row.get("Risultato"):
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
# HELPERS per stato (chiavi separate per 12/16)
# ---------------------------------------------------------
def keys_for_mode(mode):
    # mode: "12" o "16"
    return {
        "giocatori": f"draft{mode}_giocatori",
        "calendario": f"draft{mode}_calendario",
        "risultati": f"draft{mode}_risultati",
    }


def validate_players_list(players, expected_count):
    # rimuove spazi e controlla duplicati e conteggio
    cleaned = [p.strip() for p in players]
    if len(cleaned) != expected_count:
        return False, f"Numero giocatori errato: attesi {expected_count}, trovati {len(cleaned)}"
    dup = [p for p in set(cleaned) if cleaned.count(p) > 1]
    if dup:
        return False, f"Nomi duplicati trovati: {', '.join(dup)}"
    if any(p == "" for p in cleaned):
        return False, "Tutti i nomi devono essere non vuoti"
    return True, cleaned


# ---------------------------------------------------------
# UI PRINCIPALE
# ---------------------------------------------------------
def run():
    st.header("🎾 Draft giocatori (12 o 16) 🎾")

    # scelta modalità
    mode = st.radio("Seleziona modalità", options=["16 giocatori", "12 giocatori"], index=0)
    mode_key = "16" if mode.startswith("16") else "12"
    keys = keys_for_mode(mode_key)

    st.subheader("📂 Carica torneo salvato")
    uploaded = st.file_uploader("Carica file JSON del torneo", type="json")
    if uploaded:
        data = json.load(uploaded)
        giocatori = data.get("giocatori")
        calendario = pd.DataFrame(data.get("calendario", []))
        risultati = data.get("risultati", [""] * len(calendario))

        st.session_state[keys["giocatori"]] = giocatori
        st.session_state[keys["calendario"]] = calendario
        st.session_state[keys["risultati"]] = risultati
        st.success("Torneo caricato!")

    # ---------------------------------------------------------
    # INSERIMENTO GIOCATORI (differenziato per modalità)
    # ---------------------------------------------------------
    if keys["giocatori"] not in st.session_state:
        with st.form(f"{mode_key}_giocatori_form"):
            giocatori = []
            n = 8 if mode_key == "16" else 6
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Destri**")
                for i in range(1, n + 1):
                    giocatori.append(st.text_input(f"Destro {i}", value=f"D{i}"))

            with col2:
                st.markdown("**Sinistri**")
                for i in range(1, n + 1):
                    giocatori.append(st.text_input(f"Sinistro {i}", value=f"S{i}"))

            conferma = st.form_submit_button("Conferma giocatori")

        if conferma:
            ok, result = validate_players_list(giocatori, 2 * n)
            if not ok:
                st.error(result)
            else:
                st.session_state[keys["giocatori"]] = result
                st.rerun()

        st.stop()

    giocatori = st.session_state[keys["giocatori"]]

    # ---------------------------------------------------------
    # GENERA CALENDARIO (usa la logica corretta)
    # ---------------------------------------------------------
    if st.button(f"Genera calendario draft {mode_key}"):
        n = 8 if mode_key == "16" else 6
        # split destri / sinistri: primi n sono destri, successivi n sinistri
        destri = giocatori[:n]
        sinistri = giocatori[n:]
        if mode_key == "16":
            st.session_state[keys["calendario"]] = solve_draft16(destri, sinistri)
        else:
            st.session_state[keys["calendario"]] = solve_draft12(destri, sinistri)
        st.session_state[keys["risultati"]] = [""] * len(st.session_state[keys["calendario"]])

    if keys["calendario"] not in st.session_state:
        return

    df_cal = st.session_state[keys["calendario"]].copy()

    # ---------------------------------------------------------
    # RISULTATI
    # ---------------------------------------------------------
    st.subheader("Risultati")
    if keys["risultati"] not in st.session_state:
        st.session_state[keys["risultati"]] = [""] * len(df_cal)

    for i in range(len(df_cal)):
        label = (
            f"Turno {df_cal.loc[i,'Turno']} - Campo {df_cal.loc[i,'Campo']}: "
            f"{df_cal.loc[i,'Coppia A']} vs {df_cal.loc[i,'Coppia B']}"
        )
        st.session_state[keys["risultati"]][i] = st.text_input(
            label,
            value=st.session_state[keys["risultati"]][i],
            key=f"{mode_key}_ris_{i}",
        )

    df_cal["Risultato"] = st.session_state[keys["risultati"]]

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
    st.dataframe(df_comp.style.background_gradient(cmap="Greens"))

    st.markdown("#### Avversari")
    st.dataframe(df_avv.style.background_gradient(cmap="Greens"))

    # ---------------------------------------------------------
    # CLASSIFICA PREMIUM
    # ---------------------------------------------------------
    st.subheader("Classifica")
    df_classifica = calcola_classifica(df_cal, giocatori)
    render_classifica_premium(df_classifica)

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
            "risultati": st.session_state[keys["risultati"]],
            "modalita": mode_key
        }
        st.download_button(
            "💾 Salva torneo",
            data=json.dumps(data).encode("utf-8"),
            file_name=f"torneo_draft{mode_key}.json",
            mime="application/json",
            key=f"download_json_{mode_key}",
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
            file_name=f"draft{mode_key}_completo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_excel_{mode_key}",
        )
