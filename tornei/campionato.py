import streamlit as st
import pandas as pd
import json
from io import BytesIO

# ---------------------------------------------------------
# GENERAZIONE CALENDARIO ROUND ROBIN (METODO CIRCLE)
# ---------------------------------------------------------
def genera_calendario(squadre):
    n = len(squadre)
    assert n % 2 == 0, "Il numero di squadre deve essere pari"

    lista = squadre.copy()
    fissa = lista[0]
    rotanti = lista[1:]

    giornate = []
    num_giornate = n - 1

    for _ in range(num_giornate):
        giornata = []

        left = [fissa] + rotanti[: (n // 2 - 1)]
        right = rotanti[(n // 2 - 1):][::-1]

        for a, b in zip(left, right):
            giornata.append((a, b))

        rotanti = rotanti[1:] + rotanti[:1]
        giornate.append(giornata)

    return giornate


# ---------------------------------------------------------
# PUNTEGGIO
# ---------------------------------------------------------
def punti_da_risultato(ris):
    if not ris:
        return (0, 0)

    try:
        a, b = map(int, ris.split("-"))
    except Exception:
        return (0, 0)

    if a == 2 and b == 0:
        return (3, 0)
    if a == 2 and b == 1:
        return (2, 1)
    if b == 2 and a == 1:
        return (1, 2)
    if b == 2 and a == 0:
        return (0, 3)

    return (0, 0)


# ---------------------------------------------------------
# CLASSIFICA
# ---------------------------------------------------------
def calcola_classifica(giornate, risultati, squadre):
    punti = {s: 0 for s in squadre}
    set_vinti = {s: 0 for s in squadre}
    set_persi = {s: 0 for s in squadre}
    partite_giocate = {s: 0 for s in squadre}

    idx = 0
    for giornata in giornate:
        for a, b in giornata:
            ris = risultati[idx]
            idx += 1

            pa, pb = punti_da_risultato(ris)
            punti[a] += pa
            punti[b] += pb

            if ris:
                partite_giocate[a] += 1
                partite_giocate[b] += 1

                sa, sb = map(int, ris.split("-"))
                set_vinti[a] += sa
                set_persi[a] += sb
                set_vinti[b] += sb
                set_persi[b] += sa

    df = pd.DataFrame({
        "Squadra": squadre,
        "Punti": [punti[s] for s in squadre],
        "Partite Giocate": [partite_giocate[s] for s in squadre],
        "Set Vinti": [set_vinti[s] for s in squadre],
        "Set Persi": [set_persi[s] for s in squadre],
        "Diff Set": [set_vinti[s] - set_persi[s] for s in squadre],
    })

    df = df.sort_values(by=["Punti", "Diff Set", "Set Vinti"], ascending=False)
    df.reset_index(drop=True, inplace=True)
    df.index = df.index + 1
    return df


# ---------------------------------------------------------
# UI PRINCIPALE CAMPIONATO
# ---------------------------------------------------------
def run_campionato(num_squadre: int):

    # ---------------------------------------------------------
    # TITOLO CON NOME CAMPIONATO
    # ---------------------------------------------------------
    nome = st.session_state.get(f"camp_nome_{num_squadre}", f"Campionato Padel — {num_squadre} squadre")

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:14px; margin:20px 0;">
        <span style="font-size:42px;">🏆</span>
        <h1 style="margin:0; font-weight:700;">{nome}</h1>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # CARICAMENTO CAMPIONATO SALVATO
    # ---------------------------------------------------------
    st.subheader("📂 Carica campionato salvato")
    uploaded = st.file_uploader("Carica file JSON del campionato", type="json", key=f"upload_{num_squadre}")

    if uploaded:
        data = json.load(uploaded)
        st.session_state[f"camp_nome_{num_squadre}"] = data.get("nome_campionato", nome)
        st.session_state[f"c_squadre_{num_squadre}"] = data["squadre"]
        st.session_state[f"c_giornate_{num_squadre}"] = data["giornate"]
        st.session_state[f"c_risultati_{num_squadre}"] = data["risultati"]
        st.success("Campionato caricato correttamente!")

    # ---------------------------------------------------------
    # INIZIALIZZAZIONE
    # ---------------------------------------------------------
    key_squadre = f"c_squadre_{num_squadre}"
    key_giornate = f"c_giornate_{num_squadre}"
    key_risultati = f"c_risultati_{num_squadre}"
    key_nome = f"camp_nome_{num_squadre}"

    if key_squadre not in st.session_state:

        st.subheader("🏷️ Nome del campionato")
        nome_camp = st.text_input("Inserisci il nome del campionato", value=nome)

        squadre_default = [f"S{i+1}" for i in range(num_squadre)]

        st.subheader("📋 Nomi squadre")
        squadre = []
        col1, col2 = st.columns(2)
        half = num_squadre // 2

        with col1:
            for i in range(half):
                squadre.append(st.text_input(f"Squadra {i+1}", squadre_default[i], key=f"sx_{num_squadre}_{i}"))

        with col2:
            for i in range(half, num_squadre):
                squadre.append(st.text_input(f"Squadra {i+1}", squadre_default[i], key=f"dx_{num_squadre}_{i}"))

        if st.button("✅ Conferma squadre e genera calendario", key=f"conf_squadre_{num_squadre}"):
            st.session_state[key_nome] = nome_camp
            st.session_state[key_squadre] = squadre
            st.session_state[key_giornate] = genera_calendario(squadre)
            num_partite = sum(len(g) for g in st.session_state[key_giornate])
            st.session_state[key_risultati] = [""] * num_partite
            st.rerun()

        st.stop()

    # ---------------------------------------------------------
    # CAMPIONATO GIÀ GENERATO
    # ---------------------------------------------------------
    nome = st.session_state[key_nome]
    squadre = st.session_state[key_squadre]
    giornate = st.session_state[key_giornate]
    risultati = st.session_state[key_risultati]

    st.subheader("📅 Risultati delle giornate")

    idx = 0
    for g_idx, giornata in enumerate(giornate, start=1):
        with st.expander(f"Giornata {g_idx}", expanded=False):
            for a, b in giornata:
                label = f"{a} vs {b}"
                options = ["", "2-0", "2-1", "1-2", "0-2"]
                current = risultati[idx] if risultati[idx] in options else ""
                risultati[idx] = st.selectbox(
                    label,
                    options,
                    index=options.index(current),
                    key=f"ris_{num_squadre}_{idx}"
                )
                idx += 1

    st.session_state[key_risultati] = risultati

    # ---------------------------------------------------------
    # CLASSIFICA
    # ---------------------------------------------------------
    st.subheader("🏅 Classifica")
    df_classifica = calcola_classifica(giornate, risultati, squadre)
    st.dataframe(df_classifica, use_container_width=True)

    # ---------------------------------------------------------
    # AZIONI
    # ---------------------------------------------------------
    st.subheader("⚙️ Azioni campionato")
    colA, colB, colC = st.columns(3)

    with colA:
        if st.button("🔄 Reset campionato", key=f"reset_{num_squadre}"):
            del st.session_state[key_squadre]
            del st.session_state[key_giornate]
            del st.session_state[key_risultati]
            del st.session_state[key_nome]
            st.rerun()

    with colB:
        data = {
            "nome_campionato": nome,
            "squadre": squadre,
            "giornate": giornate,
            "risultati": risultati,
        }
        st.download_button(
            "💾 Salva campionato (JSON)",
            data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=f"campionato_{num_squadre}_squadre.json",
            mime="application/json",
            key=f"save_json_{num_squadre}"
        )

    with colC:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_classifica.to_excel(writer, sheet_name="Classifica", index_label="Posizione")
        st.download_button(
            "📊 Esporta classifica (Excel)",
            data=output.getvalue(),
            file_name=f"classifica_{num_squadre}_squadre.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"save_xlsx_{num_squadre}"
        )
