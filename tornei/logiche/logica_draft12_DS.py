import pandas as pd

# ---------------------------------------------------------
# 1. Generazione coppie D–S (round robin bipartito rigido)
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
# 2. Pattern avversari
# ---------------------------------------------------------
PATTERN_6 = [
    [(0,1),(2,3),(4,5)],
    [(0,2),(1,3),(4,5)],
    [(0,3),(1,4),(2,5)],
    [(0,4),(1,5),(2,3)],
    [(0,5),(1,2),(3,4)],
    [(1,5),(0,4),(2,3)],
]

PATTERN_12 = [
    [(0,2),(1,4),(3,5)],
    [(0,3),(1,5),(2,4)],
    [(0,4),(2,5),(1,3)],
    [(0,5),(1,2),(3,4)],
    [(1,3),(0,2),(4,5)],
    [(2,4),(0,1),(3,5)],
]


# ---------------------------------------------------------
# 3. Calcolo del “costo” di un pattern
# ---------------------------------------------------------
def pattern_cost(turno, pattern, team_clash, player_clash):
    cost = 0

    for a, b in pattern:
        tA = turno[a]
        tB = turno[b]

        # team-team
        key_team = tuple(sorted([tA, tB]))
        cost += team_clash.get(key_team, 0)

        # player-player
        A1, A2 = tA
        B1, B2 = tB
        for pA in [A1, A2]:
            for pB in [B1, B2]:
                key_player = tuple(sorted([pA, pB]))
                cost += player_clash.get(key_player, 0)

    return cost


# ---------------------------------------------------------
# 4. Scegli il pattern con costo minimo
# ---------------------------------------------------------
def choose_best_pattern(turno, patterns, team_clash, player_clash):
    best = None
    best_cost = float("inf")

    for pattern in patterns:
        c = pattern_cost(turno, pattern, team_clash, player_clash)
        if c < best_cost:
            best_cost = c
            best = pattern

    return best


# ---------------------------------------------------------
# 5. Solver principale
# ---------------------------------------------------------
def solve_draft12_DS(right_players, left_players, num_turni):

    base_rounds = generate_ds_rounds(right_players, left_players)
    schedule = []

    team_clash = {}
    player_clash = {}

    # primi 6 turni
    for turno_idx, turno in enumerate(base_rounds, start=1):

        pattern = choose_best_pattern(turno, PATTERN_6, team_clash, player_clash)

        for campo_idx, (a, b) in enumerate(pattern, start=1):
            tA = turno[a]
            tB = turno[b]

            # aggiorna team-team
            key_team = tuple(sorted([tA, tB]))
            team_clash[key_team] = team_clash.get(key_team, 0) + 1

            # aggiorna player-player
            A1, A2 = tA
            B1, B2 = tB
            for pA in [A1, A2]:
                for pB in [B1, B2]:
                    key_player = tuple(sorted([pA, pB]))
                    player_clash[key_player] = player_clash.get(key_player, 0) + 1

            schedule.append({
                "Turno": turno_idx,
                "Campo": campo_idx,
                "Coppia A": f"{A1} & {A2}",
                "Coppia B": f"{B1} & {B2}",
            })

    # secondi 6 turni
    if num_turni == 12:
        for turno_idx, turno in enumerate(base_rounds, start=7):

            pattern = choose_best_pattern(turno, PATTERN_12, team_clash, player_clash)

            for campo_idx, (a, b) in enumerate(pattern, start=1):
                tA = turno[a]
                tB = turno[b]

                key_team = tuple(sorted([tA, tB]))
                team_clash[key_team] = team_clash.get(key_team, 0) + 1

                A1, A2 = tA
                B1, B2 = tB
                for pA in [A1, A2]:
                    for pB in [B1, B2]:
                        key_player = tuple(sorted([pA, pB]))
                        player_clash[key_player] = player_clash.get(key_player, 0) + 1

                schedule.append({
                    "Turno": turno_idx,
                    "Campo": campo_idx,
                    "Coppia A": f"{A1} & {A2}",
                    "Coppia B": f"{B1} & {B2}",
                })

    return pd.DataFrame(schedule)
