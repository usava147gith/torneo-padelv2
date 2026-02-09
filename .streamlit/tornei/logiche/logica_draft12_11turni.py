print("USO LOGICA 11 TURNI v1.0")

from ortools.sat.python import cp_model
import pandas as pd

N_PLAYERS = 12
GROUP_SIZE = 4
N_GROUPS = N_PLAYERS // GROUP_SIZE


def build_model(n_turns: int):
    model = cp_model.CpModel()
    x = {}

    for p in range(N_PLAYERS):
        for t in range(n_turns):
            for g in range(N_GROUPS):
                x[p, t, g] = model.NewBoolVar(f"x_{p}_{t}_{g}")

    for p in range(N_PLAYERS):
        for t in range(n_turns):
            model.Add(sum(x[p, t, g] for g in range(N_GROUPS)) == 1)

    for t in range(n_turns):
        for g in range(N_GROUPS):
            model.Add(sum(x[p, t, g] for p in range(N_PLAYERS)) == GROUP_SIZE)

    return model, x


def build_pair_vars(model, x, n_turns):
    pair = {}
    for t in range(n_turns):
        for g in range(N_GROUPS):
            for p1 in range(N_PLAYERS):
                for p2 in range(p1 + 1, N_PLAYERS):
                    b = model.NewBoolVar(f"pair_{p1}_{p2}_{t}_{g}")
                    model.Add(b <= x[p1, t, g])
                    model.Add(b <= x[p2, t, g])
                    pair[(p1, p2, t, g)] = b
    return pair


def add_constraints(model, x, n_turns):
    pair = build_pair_vars(model, x, n_turns)

    # 1 compagno per turno
    for t in range(n_turns):
        for g in range(N_GROUPS):
            for p in range(N_PLAYERS):
                comp_list = []
                for q in range(N_PLAYERS):
                    if p == q:
                        continue
                    i, j = sorted((p, q))
                    comp_list.append(pair[(i, j, t, g)])
                model.Add(sum(comp_list) == 1).OnlyEnforceIf(x[p, t, g])

    # 2 coppie per gruppo
    for t in range(n_turns):
        for g in range(N_GROUPS):
            model.Add(
                sum(pair[(i, j, t, g)]
                    for i in range(N_PLAYERS)
                    for j in range(i + 1, N_PLAYERS)) == 2
            )

    # COMPAGNI TOTALI
    comp = [[model.NewIntVar(0, n_turns, f"comp_{i}_{j}")
             for j in range(N_PLAYERS)]
            for i in range(N_PLAYERS)]

    for i in range(N_PLAYERS):
        for j in range(i + 1, N_PLAYERS):
            model.Add(
                comp[i][j] ==
                sum(pair[(i, j, t, g)]
                    for t in range(n_turns)
                    for g in range(N_GROUPS))
            )
            model.Add(comp[j][i] == comp[i][j])

    # STESSO GRUPPO
    same_group = {}
    for i in range(N_PLAYERS):
        for j in range(i + 1, N_PLAYERS):
            for t in range(n_turns):
                sg = model.NewBoolVar(f"sg_{i}_{j}_{t}")
                aux = []
                for g in range(N_GROUPS):
                    a = model.NewBoolVar(f"sg_aux_{i}_{j}_{t}_{g}")
                    model.Add(a <= x[i, t, g])
                    model.Add(a <= x[j, t, g])
                    model.Add(a >= x[i, t, g] + x[j, t, g] - 1)
                    aux.append(a)
                model.AddMaxEquality(sg, aux)
                same_group[(i, j, t)] = sg

    # COMPAGNI PER TURNO
    teammate_turn = {}
    for i in range(N_PLAYERS):
        for j in range(i + 1, N_PLAYERS):
            for t in range(n_turns):
                tt = model.NewBoolVar(f"tm_{i}_{j}_{t}")
                aux = []
                for g in range(N_GROUPS):
                    aux.append(pair[(i, j, t, g)])
                model.AddMaxEquality(tt, aux)
                teammate_turn[(i, j, t)] = tt

    # AVVERSARI PER TURNO
    opponent_turn = {}
    for i in range(N_PLAYERS):
        for j in range(i + 1, N_PLAYERS):
            for t in range(n_turns):
                opp = model.NewBoolVar(f"opp_{i}_{j}_{t}")
                sg = same_group[(i, j, t)]
                tt = teammate_turn[(i, j, t)]
                model.AddBoolAnd([sg, tt.Not()]).OnlyEnforceIf(opp)
                model.AddBoolOr([sg.Not(), tt]).OnlyEnforceIf(opp.Not())
                opponent_turn[(i, j, t)] = opp

    # AVVERSARI TOTALI
    opp = [[model.NewIntVar(0, n_turns, f"opp_{i}_{j}")
            for j in range(N_PLAYERS)]
           for i in range(N_PLAYERS)]

    for i in range(N_PLAYERS):
        for j in range(i + 1, N_PLAYERS):
            model.Add(
                opp[i][j] ==
                sum(opponent_turn[(i, j, t)] for t in range(n_turns))
            )
            model.Add(opp[j][i] == opp[i][j])

    # VINCOLO DURO: massimo 4 avversari
    for i in range(N_PLAYERS):
        for j in range(i + 1, N_PLAYERS):
            model.Add(opp[i][j] <= 4)

    # OBIETTIVO: minimizzare ripetizioni
    model.Minimize(
        3 * sum(comp[i][j] for i in range(N_PLAYERS) for j in range(i + 1, N_PLAYERS)) +
        sum(opp[i][j] for i in range(N_PLAYERS) for j in range(i + 1, N_PLAYERS))
    )

    return pair


def solve_draft12(names, num_turni=11):
    model, x = build_model(num_turni)
    pair = add_constraints(model, x, num_turni)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 90
    solver.parameters.num_search_workers = 8

    result = solver.Solve(model)
    if result not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("Nessuna soluzione trovata.")

    rows = []
    for t in range(num_turni):
        for g in range(N_GROUPS):
            coppie = []
            for i in range(N_PLAYERS):
                for j in range(i + 1, N_PLAYERS):
                    if solver.Value(pair[(i, j, t, g)]) == 1:
                        coppie.append((i, j))
            if len(coppie) == 2:
                (a1, a2), (b1, b2) = coppie
                rows.append({
                    "Turno": t + 1,
                    "Campo": g + 1,
                    "Coppia A": f"{names[a1]} & {names[a2]}",
                    "Coppia B": f"{names[b1]} & {names[b2]}",
                })

    return pd.DataFrame(rows)
