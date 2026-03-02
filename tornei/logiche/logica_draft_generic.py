# logiche/logica_draft_generic.py
import pandas as pd
import copy

# -----------------------
# Parametri configurabili
# -----------------------
WEIGHT_TEAM = 3
WEIGHT_PLAYER = 1
WEIGHT_RIGHT_MULT = 1.5
MAX_REPEAT = 2               # vincolo hard: non più di 2 incontri player-player
MAX_BACKTRACK_DEPTH = 2      # quanti turni indietro provare il backtracking
HARD_PENALTY = 1000000       # costo molto alto per violare il vincolo (usato come fallback)

# ---------------------------------------------------------
# 1) Generazione round bipartiti (ogni right con ogni left)
# ---------------------------------------------------------
def generate_ds_rounds(right_players, left_players):
    m = len(right_players)
    if m != len(left_players):
        raise ValueError("right_players e left_players devono avere stessa lunghezza")
    rounds = []
    for k in range(m):
        turno = []
        for i in range(m):
            r = right_players[i]
            s = left_players[(i + k) % m]
            turno.append((r, s))
        rounds.append(turno)
    return rounds

# ---------------------------------------------------------
# 2) Generazione pattern di accoppiamento (rotazioni)
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 3) Funzioni di costo e verifica vincoli
# ---------------------------------------------------------
def pattern_cost(turno, pattern, team_clash, player_clash, right_set):
    cost = 0
    for a, b in pattern:
        tA = turno[a]
        tB = turno[b]

        # team-team
        key_team = tuple(sorted([tA, tB]))
        cost += WEIGHT_TEAM * team_clash.get(key_team, 0)

        # player-player
        A1, A2 = tA
        B1, B2 = tB
        for pA in [A1, A2]:
            for pB in [B1, B2]:
                key_player = tuple(sorted([pA, pB]))
                base = player_clash.get(key_player, 0)
                w = WEIGHT_PLAYER + base
                if (pA in right_set) or (pB in right_set):
                    w *= WEIGHT_RIGHT_MULT
                cost += w
                if base >= MAX_REPEAT:
                    cost += HARD_PENALTY
    return cost

def violates_hard_constraint(turno, pattern, player_clash):
    # ritorna True se applicando questo pattern si supera MAX_REPEAT per qualche coppia
    for a, b in pattern:
        tA = turno[a]
        tB = turno[b]
        A1, A2 = tA
        B1, B2 = tB
        for pA in [A1, A2]:
            for pB in [B1, B2]:
                key_player = tuple(sorted([pA, pB]))
                if player_clash.get(key_player, 0) >= MAX_REPEAT:
                    return True
    return False

# ---------------------------------------------------------
# 4) Scelta pattern con fallback e ordinamento
# ---------------------------------------------------------
def rank_patterns(turno, patterns, team_clash, player_clash, right_set):
    scored = []
    for pattern in patterns:
        c = pattern_cost(turno, pattern, team_clash, player_clash, right_set)
        scored.append((c, pattern))
    scored.sort(key=lambda x: x[0])
    return scored

# ---------------------------------------------------------
# 5) Backtracking locale: prova alternative sui turni precedenti
# ---------------------------------------------------------
def build_schedule_with_backtracking(base_rounds, right_set):
    m = len(base_rounds[0])
    patterns = generate_pairing_patterns(m)

    schedule = [None] * len(base_rounds)   # salveremo pattern scelti per ogni turno
    team_clash = {}
    player_clash = {}

    # helper per applicare/unapply pattern su strutture clash
    def apply_pattern(turno, pattern):
        for a, b in pattern:
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

    def unapply_pattern(turno, pattern):
        for a, b in pattern:
            tA = turno[a]
            tB = turno[b]
            key_team = tuple(sorted([tA, tB]))
            team_clash[key_team] = team_clash.get(key_team, 0) - 1
            if team_clash[key_team] == 0:
                del team_clash[key_team]
            A1, A2 = tA
            B1, B2 = tB
            for pA in [A1, A2]:
                for pB in [B1, B2]:
                    key_player = tuple(sorted([pA, pB]))
                    player_clash[key_player] = player_clash.get(key_player, 0) - 1
                    if player_clash[key_player] == 0:
                        del player_clash[key_player]

    # procedura principale con backtracking locale
    for t_idx, turno in enumerate(base_rounds):
        # ottieni pattern ordinati per costo
        ranked = rank_patterns(turno, patterns, team_clash, player_clash, right_set)
        chosen = None

        # prova i pattern in ordine; se uno non viola vincolo hard lo scegliamo
        for cost, pattern in ranked:
            if not violates_hard_constraint(turno, pattern, player_clash):
                chosen = pattern
                break

        if chosen is not None:
            apply_pattern(turno, chosen)
            schedule[t_idx] = chosen
            continue

        # se qui, nessun pattern valido senza violare MAX_REPEAT: proviamo backtracking locale
        backtracked = False
        for depth in range(1, min(MAX_BACKTRACK_DEPTH, t_idx) + 1):
            prev_idx = t_idx - depth
            # salviamo lo stato corrente per rollback
            saved_team = copy.deepcopy(team_clash)
            saved_player = copy.deepcopy(player_clash)
            saved_schedule = schedule[:]

            # rimuoviamo gli effetti dei turni prev_idx..t_idx-1
            for undo_idx in range(prev_idx, t_idx):
                if schedule[undo_idx] is not None:
                    unapply_pattern(base_rounds[undo_idx], schedule[undo_idx])
                    schedule[undo_idx] = None

            # per il turno prev_idx proviamo alternative (secondo, terzo, ...)
            prev_ranked = rank_patterns(base_rounds[prev_idx], patterns, team_clash, player_clash, right_set)
            # scorri alternative diverse dalla già scelta (se esiste)
            for _, alt_pattern in prev_ranked:
                # se alt_pattern è identico a quello già provato prima, skip
                # (se schedule[prev_idx] era None, non c'è problema)
                # applichiamo alt_pattern e poi proviamo a ricostruire i turni successivi fino a t_idx
                apply_pattern(base_rounds[prev_idx], alt_pattern)
                schedule[prev_idx] = alt_pattern

                success = True
                # ricostruisci i turni successivi fino a t_idx
                for rebuild_idx in range(prev_idx + 1, t_idx + 1):
                    ranked_rebuild = rank_patterns(base_rounds[rebuild_idx], patterns, team_clash, player_clash, right_set)
                    found = False
                    for _, ptn in ranked_rebuild:
                        if not violates_hard_constraint(base_rounds[rebuild_idx], ptn, player_clash):
                            apply_pattern(base_rounds[rebuild_idx], ptn)
                            schedule[rebuild_idx] = ptn
                            found = True
                            break
                    if not found:
                        success = False
                        break

                if success:
                    backtracked = True
                    break
                # rollback e prova altra alternativa
                # rimuovi gli effetti applicati durante questo tentativo
                for idx_clear in range(prev_idx, t_idx + 1):
                    if schedule[idx_clear] is not None:
                        unapply_pattern(base_rounds[idx_clear], schedule[idx_clear])
                        schedule[idx_clear] = None
                # ripristina team/player clash allo stato prima del tentativo
                team_clash = copy.deepcopy(saved_team)
                player_clash = copy.deepcopy(saved_player)
                schedule = saved_schedule[:]

            if backtracked:
                break

        if not backtracked:
            # fallback: scegli il pattern con costo minimo anche se viola (evita crash)
            fallback_pattern = ranked[0][1]
            apply_pattern(turno, fallback_pattern)
            schedule[t_idx] = fallback_pattern

    # costruisci DataFrame finale
    rows = []
    for turno_idx, turno in enumerate(base_rounds, start=1):
        pattern = schedule[turno_idx - 1]
        for campo_idx, (a, b) in enumerate(pattern, start=1):
            tA = turno[a]
            tB = turno[b]
            A1, A2 = tA
            B1, B2 = tB
            rows.append({
                "Turno": turno_idx,
                "Campo": campo_idx,
                "Coppia A": f"{A1} & {A2}",
                "Coppia B": f"{B1} & {B2}",
            })
    return pd.DataFrame(rows)
