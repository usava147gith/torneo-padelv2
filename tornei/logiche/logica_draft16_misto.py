import pandas as pd

N_MEN = 8
N_WOMEN = 8
N_TURNS = 8
N_GROUPS = 4

MEN = list(range(N_MEN))
WOMEN = list(range(N_WOMEN))

def build_partners():
    partner = [[None]*N_TURNS for _ in MEN]
    for m in MEN:
        for t in range(N_TURNS):
            partner[m][t] = (m + t) % N_WOMEN
    return partner

def score_pairings(pairs, t, partner, men_vs_men, women_vs_women, men_vs_women, max_meet=3):
    score = 0
    for mA, mB in pairs:
        i, j = sorted((mA, mB))
        c_m = men_vs_men.get((i, j), 0)
        if c_m == 0:
            score -= 3
        elif c_m == 1:
            score += 1
        else:
            score += 10

        wA = partner[mA][t]
        wB = partner[mB][t]
        a, b = sorted((wA, wB))
        c_w = women_vs_women.get((a, b), 0)
        if c_w == 0:
            score -= 4
        elif c_w == 1:
            score += 2
        else:
            score += 15

        c_mw1 = men_vs_women.get((mA, wB), 0)
        if c_mw1 == 0:
            score -= 2
        elif c_mw1 == 1:
            score += 1
        else:
            score += 8

        c_mw2 = men_vs_women.get((mB, wA), 0)
        if c_mw2 == 0:
            score -= 2
        elif c_mw2 == 1:
            score += 1
        else:
            score += 8

    return score

def best_pairings_for_turn(men_list, t, partner, men_vs_men, women_vs_women, men_vs_women, max_meet=3):
    men_list = list(men_list)
    best = {"score": None, "pairs": None}

    def backtrack(remaining, current_pairs):
        nonlocal best
        if not remaining:
            s = score_pairings(current_pairs, t, partner, men_vs_men, women_vs_women, men_vs_women, max_meet)
            if best["pairs"] is None or s < best["score"]:
                best["score"] = s
                best["pairs"] = list(current_pairs)
            return

        m = remaining[0]
        for n in remaining[1:]:
            i, j = sorted((m, n))
            if men_vs_men.get((i, j), 0) >= max_meet:
                continue

            wA = partner[m][t]
            wB = partner[n][t]
            a, b = sorted((wA, wB))
            if women_vs_women.get((a, b), 0) >= max_meet:
                continue

            if men_vs_women.get((m, wB), 0) >= max_meet:
                continue
            if men_vs_women.get((n, wA), 0) >= max_meet:
                continue

            new_remaining = [x for x in remaining if x not in (m, n)]
            backtrack(new_remaining, current_pairs + [(m, n)])

    backtrack(men_list, [])
    return best["pairs"]

def build_schedule(names_men, names_women):
    if len(names_men) != N_MEN or len(names_women) != N_WOMEN:
        raise ValueError("Servono 8 nomi uomini e 8 nomi donne.")

    partner = build_partners()
    men_vs_men = {}
    women_vs_women = {}
    men_vs_women = {}
    schedule = []

    for t in range(N_TURNS):
        men_this_turn = MEN[:]
        pairs = best_pairings_for_turn(
            men_this_turn, t, partner, men_vs_men, women_vs_women, men_vs_women, max_meet=3
        )
        if pairs is None:
            raise RuntimeError(f"Impossibile trovare accoppiamenti al turno {t+1}")

        for g, (mA, mB) in enumerate(pairs):
            i, j = sorted((mA, mB))
            men_vs_men[(i, j)] = men_vs_men.get((i, j), 0) + 1

            wA = partner[mA][t]
            wB = partner[mB][t]
            a, b = sorted((wA, wB))
            women_vs_women[(a, b)] = women_vs_women.get((a, b), 0) + 1

            men_vs_women[(mA, wB)] = men_vs_women.get((mA, wB), 0) + 1
            men_vs_women[(mB, wA)] = men_vs_women.get((mB, wA), 0) + 1

            schedule.append((t+1, g+1, mA, wA, mB, wB))

    rows = []
    for turno, campo, mA, wA, mB, wB in schedule:
        rows.append({
            "Turno": turno,
            "Campo": campo,
            "Coppia A": f"{names_men[mA]} & {names_women[wA]}",
            "Coppia B": f"{names_men[mB]} & {names_women[wB]}",
        })

    df = pd.DataFrame(rows)
    return df

def solve_draft16_misto(names_men, names_women):
    return build_schedule(names_men, names_women)
