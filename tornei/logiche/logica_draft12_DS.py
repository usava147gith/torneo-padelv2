import pandas as pd

# ---------------------------------------------------------
# 1. Generazione coppie D–S (round robin bipartito)
# ---------------------------------------------------------
def generate_ds_rounds(right_players, left_players):
    rounds = []
    n = 6
    for k in range(n):
        turno = []
        for i in range(n):
            r = right_players[i]
            s = left_players[(i + k) % n]
            turno.append((r, s))
        rounds.append(turno)
    return rounds


# ---------------------------------------------------------
# 2. Pattern avversari per i primi 6 turni
# ---------------------------------------------------------
PATTERN_6 = [
    [(0,1),(2,3),(4,5)],
    [(0,2),(1,3),(4,5)],
    [(0,3),(1,4),(2,5)],
    [(0,4),(1,5),(2,3)],
    [(0,5),(1,2),(3,4)],
    [(1,5),(0,4),(2,3)],
]

# ---------------------------------------------------------
# 3. Pattern avversari per i turni 7–12 (no rematch)
# ---------------------------------------------------------
PATTERN_12 = [
    [(0,2),(1,4),(3,5)],
    [(0,3),(1,5),(2,4)],
    [(0,4),(2,5),(1,3)],
    [(0,5),(1,2),(3,4)],
    [(1,3),(0,2),(4,5)],
    [(2,4),(0,1),(3,5)],
]


def pair_teams_no_repeat(teams, turno_idx, num_turni):
    if num_turni == 6:
        pattern = PATTERN_6[(turno_idx - 1) % 6]
    else:
        if turno_idx <= 6:
            pattern = PATTERN_6[(turno_idx - 1) % 6]
        else:
            pattern = PATTERN_12[(turno_idx - 7) % 6]

    matches = []
    for a, b in pattern:
        matches.append((teams[a], teams[b]))
    return matches


# ---------------------------------------------------------
# 4. Solver principale
# ---------------------------------------------------------
def solve_draft12_DS(right_players, left_players, num_turni):

    base_rounds = generate_ds_rounds(right_players, left_players)
    schedule = []

    # primi 6 turni
    for turno_idx, turno in enumerate(base_rounds, start=1):
        matches = pair_teams_no_repeat(turno, turno_idx, num_turni)
        for campo_idx, match in enumerate(matches, start=1):
            schedule.append({
                "Turno": turno_idx,
                "Campo": campo_idx,
                "Coppia A": f"{match[0][0]} & {match[0][1]}",
                "Coppia B": f"{match[1][0]} & {match[1][1]}",
            })

    # secondi 6 turni (solo se richiesti)
    if num_turni == 12:
        for turno_idx, turno in enumerate(base_rounds, start=7):
            matches = pair_teams_no_repeat(turno, turno_idx, num_turni)
            for campo_idx, match in enumerate(matches, start=1):
                schedule.append({
                    "Turno": turno_idx,
                    "Campo": campo_idx,
                    "Coppia A": f"{match[0][0]} & {match[0][1]}",
                    "Coppia B": f"{match[1][0]} & {match[1][1]}",
                })

    return pd.DataFrame(schedule)
