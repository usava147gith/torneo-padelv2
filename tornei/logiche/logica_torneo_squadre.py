import pandas as pd
from collections import defaultdict

# ---------------------------------------------------------
# Schema coppie (rimane identico, funziona molto bene)
# ---------------------------------------------------------

schema_coppie_indici = [
    [(0, 1), (3, 4)],
    [(0, 2), (3, 5)],
    [(1, 2), (4, 5)],
    [(0, 3), (1, 4)],
    [(0, 4), (1, 5)],
    [(0, 5), (2, 4)],
    [(1, 3), (2, 5)],
    [(2, 3), (4, 5)],
]

# ---------------------------------------------------------
# Generazione dinamica degli abbinamenti
# ---------------------------------------------------------

def genera_abbinamenti(squadre):
    """
    Genera gli abbinamenti per 8 turni usando i nomi delle squadre inseriti dall'utente.
    squadre: lista di 4 nomi
    """
    assert len(squadre) == 4, "Devono esserci esattamente 4 squadre."

    # Round robin base (3 turni)
    base = [
        [(squadre[0], squadre[1]), (squadre[2], squadre[3])],
        [(squadre[0], squadre[2]), (squadre[1], squadre[3])],
        [(squadre[0], squadre[3]), (squadre[1], squadre[2])],
    ]

    # Round robin doppio (6 turni)
    abbinamenti = base + base

    # Aggiungiamo 2 turni extra ripetendo i primi due (come nel file originale)
    abbinamenti += base[:2]

    return abbinamenti  # totale = 8 turni


# ---------------------------------------------------------
# Funzione principale
# ---------------------------------------------------------

def genera_torneo_squadre(squadre_dict):

    # Lista squadre nell'ordine inserito dall'utente
    lista_squadre = list(squadre_dict.keys())
    
    # Mappa giocatore -> genere ("U" o "D") 
    genere = {} 
    for squadra, lista in squadre_dict.items(): 
        for idx, g in enumerate(lista): 
            if not g: 
                continue # salta eventuali campi vuoti if idx < 3: genere[g] = "U" else: genere[g] = "D"
            if idx < 3: 
                genere[g] = "U" 
            else: 
                genere[g] = "D"
                
    # Generiamo gli abbinamenti dinamici
    abbinamenti_turni = genera_abbinamenti(lista_squadre)

    # Funzioni interne
    def tipo_coppia(g1, g2):
        s1 = genere.get(g1, None)
        s2 = genere.get(g2, None)

        if s1 == "U" and s2 == "U":
            return "MM"
        if s1 == "D" and s2 == "D":
            return "FF"
        return "MF"


    def coppie_squadra(nome_squadra, turno):
        gioc = squadre_dict[nome_squadra]
        return [(gioc[i], gioc[j]) for i, j in schema_coppie_indici[turno]]

    # -------------------------
    # CALENDARIO
    # -------------------------
    righe = []

    for turno_idx in range(8):
        turno = turno_idx + 1
        sfide = abbinamenti_turni[turno_idx]
        campo = 1

        for A, B in sfide:
            coppieA = coppie_squadra(A, turno_idx)
            coppieB = coppie_squadra(B, turno_idx)

            inA = {g for c in coppieA for g in c}
            inB = {g for c in coppieB for g in c}

            tuttiA = set(squadre_dict[A])
            tuttiB = set(squadre_dict[B])

            ripA = list(tuttiA - inA)
            ripB = list(tuttiB - inB)

            uomoA = next((g for g in ripA if genere.get(g) == "U"), "")
            donnaA = next((g for g in ripA if genere.get(g) == "D"), "")
            uomoB = next((g for g in ripB if genere.get(g) == "U"), "")
            donnaB = next((g for g in ripB if genere.get(g) == "D"), "")


            for idx in range(2):
                gA1, gA2 = coppieA[idx]
                gB1, gB2 = coppieB[idx]

                tipo = tipo_coppia(gA1, gA2)

                righe.append({
                    "Turno": turno,
                    "Campo": campo,
                    "Squadra_A": A,
                    "Giocatore_A1": gA1,
                    "Giocatore_A2": gA2,
                    "Squadra_B": B,
                    "Giocatore_B1": gB1,
                    "Giocatore_B2": gB2,
                    "Tipo_coppia": tipo,
                    "Uomo_riposo_A": uomoA,
                    "Donna_riposo_A": donnaA,
                    "Uomo_riposo_B": uomoB,
                    "Donna_riposo_B": donnaB,
                })

                campo += 1

    df_cal = pd.DataFrame(righe)

    # -------------------------
    # CONTROLLO GIOCATE / RIPOSI
    # -------------------------
    conteggio_giocate = defaultdict(int)
    conteggio_riposi = defaultdict(int)

    for _, r in df_cal.iterrows():
        for g in [r["Giocatore_A1"], r["Giocatore_A2"], r["Giocatore_B1"], r["Giocatore_B2"]]:
            conteggio_giocate[g] += 1

    for turno in range(1, 9):
        df_t = df_cal[df_cal["Turno"] == turno]
        in_campo = {s: set() for s in squadre_dict}

        for _, r in df_t.iterrows():
            in_campo[r["Squadra_A"]].update([r["Giocatore_A1"], r["Giocatore_A2"]])
            in_campo[r["Squadra_B"]].update([r["Giocatore_B1"], r["Giocatore_B2"]])

        for s, lista in squadre_dict.items():
            rip = set(lista) - in_campo[s]
            for g in rip:
                conteggio_riposi[g] += 1

    df_controllo = pd.DataFrame([
        {"Squadra": s, "Giocatore": g, "Giocate": conteggio_giocate[g], "Riposi": conteggio_riposi[g]}
        for s in squadre_dict
        for g in squadre_dict[s]
    ])

    # -------------------------
    # COMPAGNI
    # -------------------------
    conteggio_compagni = defaultdict(int)

    for turno_idx in range(8):
        for s in squadre_dict:
            coppie = coppie_squadra(s, turno_idx)
            for g1, g2 in coppie:
                conteggio_compagni[(g1, g2)] += 1
                conteggio_compagni[(g2, g1)] += 1

    df_compagni = pd.DataFrame([
        {"Giocatore": g, "Compagno": c, "Partite_insieme": cnt}
        for (g, c), cnt in conteggio_compagni.items()
        if g != c
    ])

    # -------------------------
    # METRICHE
    # -------------------------
    metriche_squadra = defaultdict(lambda: {"MM": 0, "FF": 0, "MF": 0})
    metriche_giocatore = defaultdict(lambda: {"MM": 0, "FF": 0, "MF": 0})

    for _, r in df_cal.iterrows():
        tipo = r["Tipo_coppia"]
        metriche_squadra[r["Squadra_A"]][tipo] += 1
        metriche_squadra[r["Squadra_B"]][tipo] += 1

        for g in [r["Giocatore_A1"], r["Giocatore_A2"], r["Giocatore_B1"], r["Giocatore_B2"]]:
            metriche_giocatore[g][tipo] += 1

    df_metriche_squadra = pd.DataFrame([
        {"Squadra": s, "MM": d["MM"], "FF": d["FF"], "MF": d["MF"], "Totale": d["MM"] + d["FF"] + d["MF"]}
        for s, d in metriche_squadra.items()
    ])

    df_metriche_giocatore = pd.DataFrame([
        {"Giocatore": g, "MM": d["MM"], "FF": d["FF"], "MF": d["MF"], "Totale": d["MM"] + d["FF"] + d["MF"]}
        for g, d in metriche_giocatore.items()
    ])

    df_percentuali = df_metriche_squadra.copy()
    df_percentuali["Perc_MM"] = df_percentuali["MM"] / df_percentuali["Totale"]
    df_percentuali["Perc_FF"] = df_percentuali["FF"] / df_percentuali["Totale"]
    df_percentuali["Perc_MF"] = df_percentuali["MF"] / df_percentuali["Totale"]

    return {
        "calendario": df_cal,
        "controllo": df_controllo,
        "compagni": df_compagni,
        "metriche_squadra": df_metriche_squadra,
        "metriche_giocatore": df_metriche_giocatore,
        "percentuali": df_percentuali,
    }
