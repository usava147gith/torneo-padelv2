import pandas as pd
import itertools

# ---------------------------------------------------------
# 1. Genera tutte le possibili coppie D–S (permutazioni sinistri)
# ---------------------------------------------------------
def generate_all_teamings(right_players, left_players):
    for perm in itertools.permutations(left_players):
        yield [(right_players[i], perm[i]) for i in range(6)]


# ---------------------------------------------------------
# 2. Pattern avversari (6 match possibili)
# ---------------------------------------------------------
PATTERNS = [
    [(0,1),(2,3),(4,5)],
    [(0,2),(1,3),(4,5)],
    [(0,3),(1,4),(2,5)],
    [(0,4),(1,5),(2,3)],
    [(0,5),(1,2),(3,4)],
    [(1,5),(0,4),(2,3)],
]


# ---------------------------------------------------------
# 3. Controllo validità match (team + giocatori)
# ---------------------------------------------------------
def match_is_valid(tA, tB, team_clash, player_clash):
    # team-team
    key_team = tuple(sorted([tA, tB]))
    if team_clash.get(key_team, 0) >= 2:
        return False

    # player-player
    A1, A2 = tA
    B1, B2 = tB
    for pA in [A1, A2]:
        for pB in [B1, B2]:
            key_player = tuple(sorted([pA, pB]))
            if player_clash.get(key_player, 0) >= 2:
                return False

    return True


# ---------------------------------------------------------
# 4. Applica un pattern e verifica se è valido
# ---------------------------------------------------------
def pattern_is_valid(teams, pattern, team_clash, player_clash):
    for a, b in pattern:
        if not match_is_valid(teams[a], teams[b], team_clash, player_clash):
            return False
    return True


# ---------------------------------------------------------
# 5. Aggiorna contatori
# ---------------------------------------------------------
def apply_pattern(teams, pattern, team_clash, player_clash):
    for a, b in pattern:
        tA = teams[a]
        tB = teams[b]

        # team-team
        key_team = tuple(sorted([tA, tB]))
        team_clash[key_team] = team_clash.get(key_team, 0) + 1

        # player-player
        A1, A2 = tA
        B1, B2 = tB
        for pA in [A1, A2]:
            for pB in [B1, B2]:
                key_player = tuple(sorted([pA, pB]))
                player_clash[key_player] = player_clash.get(key_player, 0) + 1


# ---------------------------------------------------------
# 6. Backtracking ricorsivo
# ---------------------------------------------------------
def solve_turn(turn_idx, right_players, left_players, num_turni,
               team_clash, player_clash, schedule):

    if turn_idx > num_turni:
        return True  # soluzione trovata

    # prova tutte le permutazioni dei sinistri
    for teams in generate_all_teamings(right_players, left_players):

        # prova tutti i pattern
        for pattern in PATTERNS:

            if not pattern_is_valid(teams, pattern, team_clash, player_clash):
                continue

            # salva stato per backtracking
            saved_team = team_clash.copy()
            saved_player = player_clash.copy()

            # applica pattern
            apply_pattern(teams, pattern, team_clash, player_clash)

            # aggiungi al calendario
            for campo_idx, (a, b) in enumerate(pattern, start=1):
                tA = teams[a]
                tB = teams[b]
                schedule.append({
                    "Turno": turn_idx,
                    "Campo": campo_idx,
                    "Coppia A": f"{tA[0]} & {tA[1]}",
                    "Coppia B": f"{tB[0]} & {tB[1]}",
                })

            # ricorsione
            if solve_turn(turn_idx + 1, right_players, left_players, num_turni,
                          team_clash, player_clash, schedule):
                return True

            # backtracking
            team_clash.clear()
            team_clash.update(saved_team)
            player_clash.clear()
            player_clash.update(saved_player)

            # rimuovi partite aggiunte
            for _ in range(6):
                schedule.pop()

    return False  # nessuna soluzione valida


# ---------------------------------------------------------
# 7. Solver principale
# ---------------------------------------------------------
def solve_draft12_DS(right_players, left_players, num_turni):

    team_clash = {}
    player_clash = {}
    schedule = []

    solve_turn(1, right_players, left_players, num_turni,
               team_clash, player_clash, schedule)

    return pd.DataFrame(schedule)
