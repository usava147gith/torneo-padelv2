# logiche/logica_draft_generic.py
import pandas as pd

def generate_ds_rounds(right_players, left_players):
    m = len(right_players)
    rounds = []
    for k in range(m):
        turno = []
        for i in range(m):
            r = right_players[i]
            s = left_players[(i + k) % m]
            turno.append((r, s))
        rounds.append(turno)
    return rounds

def generate_pairing_patterns(m):
    patterns = []
    base_indices = list(range(m))
    for shift in range(m):
        rotated = [(base_indices[(i + shift) % m]) for i in range(m)]
        pairs = []
        for k in range(m // 2):
            a = rotated[k]
            b = rotated[m - 1 - k]
            pairs.append((a, b))
        patterns.append(pairs)
    return patterns

def pattern_cost(turno, pattern, team_clash, player_clash):
    cost = 0
    for a, b in pattern:
        tA = turno[a]
        tB = turno[b]
        key_team = tuple(sorted([tA, tB]))
        cost += team_clash.get(key_team, 0)
        A1, A2 = tA
        B1, B2 = tB
        for pA in [A1, A2]:
            for pB in [B1, B2]:
                key_player = tuple(sorted([pA, pB]))
                cost += player_clash.get(key_player, 0)
    return cost

def choose_best_pattern(turno, patterns, team_clash, player_clash):
    best = None
    best_cost = float("inf")
    for pattern in patterns:
        c = pattern_cost(turno, pattern, team_clash, player_clash)
        if c < best_cost:
            best_cost = c
            best = pattern
    return best

def build_schedule_from_rounds(base_rounds):
    m = len(base_rounds[0])
    patterns = generate_pairing_patterns(m)
    schedule = []
    team_clash = {}
    player_clash = {}

    for turno_idx, turno in enumerate(base_rounds, start=1):
        pattern = choose_best_pattern(turno, patterns, team_clash, player_clash)
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
