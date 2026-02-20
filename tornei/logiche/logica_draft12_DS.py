import pandas as pd

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


def pair_teams_variant(teams, variant_id):
    if variant_id == 0:
        return [
            (teams[0], teams[1]),
            (teams[2], teams[3]),
            (teams[4], teams[5]),
        ]
    else:
        return [
            (teams[0], teams[2]),
            (teams[1], teams[4]),
            (teams[3], teams[5]),
        ]


def solve_draft12_DS(players, num_turni):
    right = players[:6]
    left = players[6:]

    base_rounds = generate_ds_rounds(right, left)

    schedule = []

    # primi 6 turni
    for turno_idx, turno in enumerate(base_rounds, start=1):
        matches = pair_teams_variant(turno, variant_id=0)
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
            matches = pair_teams_variant(turno, variant_id=1)
            for campo_idx, match in enumerate(matches, start=1):
                schedule.append({
                    "Turno": turno_idx,
                    "Campo": campo_idx,
                    "Coppia A": f"{match[0][0]} & {match[0][1]}",
                    "Coppia B": f"{match[1][0]} & {match[1][1]}",
                })

    return pd.DataFrame(schedule)
