from ortools.sat.python import cp_model
import pandas as pd

N_PLAYERS = 16
N_TURNS = 8
GROUP_SIZE = 4
N_GROUPS = N_PLAYERS // GROUP_SIZE

def build_model():
    model = cp_model.CpModel()
    x = {}
    for p in range(N_PLAYERS):
        for t in range(N_TURNS):
            for g in range(N_GROUPS):
                x[p, t, g] = model.NewBoolVar(f"x_p{p}_t{t}_g{g}")

    for p in range(N_PLAYERS):
        for t in range(N_TURNS):
            model.Add(sum(x[p, t, g] for g in range(N_GROUPS)) == 1)

    for t in range(N_TURNS):
        for g in range(N_GROUPS):
            model.Add(sum(x[p, t, g] for p in range(N_PLAYERS)) == GROUP_SIZE)

    return model, x

def build_pair_vars(model, x):
    pair = {}
    for t in range(N_TURNS):
        for g in range(N_GROUPS):
            for p1 in range(N_PLAYERS):
                for p2 in range(p1 + 1, N_PLAYERS):
                    b = model.NewBoolVar(f"pair_{p1}_{p2}_{t}_{g}")
                    pair[(p1, p2, t, g)] = b
                    model.Add(b <= x[p1, t, g])
                    model.Add(b <= x[p2, t, g])
    return pair

def add_constraints_v7_5(model, x):
    pair = build_pair_vars(model, x)

    for t in range(N_TURNS):
        for g in range(N_GROUPS):
            for p in range(N_PLAYERS):
                involved = []
                for q in range(N_PLAYERS):
                    if p == q:
                        continue
                    i, j = sorted((p, q))
                    involved.append(pair[(i, j, t, g)])
                model.Add(sum(involved) == 1).OnlyEnforceIf(x[p, t, g])
                model.Add(sum(involved) == 0).OnlyEnforceIf(x[p, t, g].Not())

    for t in range(N_TURNS):
        for g in range(N_GROUPS):
            model.Add(
                sum(pair[(i, j, t, g)]
                    for i in range(N_PLAYERS)
                    for j in range(i + 1, N_PLAYERS))
                == 2
            )

    comp = [[model.NewIntVar(0, N_TURNS, f"comp_{i}_{j}")
             for j in range(N_PLAYERS)]
             for i in range(N_PLAYERS)]

    for p1 in range(N_PLAYERS):
        for p2 in range(p1 + 1, N_PLAYERS):
            model.Add(
                comp[p1][p2] ==
                sum(pair[(p1, p2, t, g)]
                    for t in range(N_TURNS)
                    for g in range(N_GROUPS))
            )
            model.Add(comp[p2][p1] == comp[p1][p2])

    max_comp = model.NewIntVar(0, 1, "max_comp")
    for i in range(N_PLAYERS):
        for j in range(i + 1, N_PLAYERS):
            model.Add(comp[i][j] <= max_comp)

    same_group = {}
    for p1 in range(N_PLAYERS):
        for p2 in range(p1 + 1, N_PLAYERS):
            for t in range(N_TURNS):
                sg = model.NewBoolVar(f"same_group_{p1}_{p2}_{t}")
                aux = []
                for g in range(N_GROUPS):
                    a = model.NewBoolVar(f"sg_aux_{p1}_{p2}_{t}_{g}")
                    model.Add(a <= x[p1, t, g])
                    model.Add(a <= x[p2, t, g])
                    model.Add(a >= x[p1, t, g] + x[p2, t, g] - 1)
                    aux.append(a)
                if aux:
                    model.AddMaxEquality(sg, aux)
                else:
                    model.Add(sg == 0)
                same_group[(p1, p2, t)] = sg

    teammate_turn = {}
    for p1 in range(N_PLAYERS):
        for p2 in range(p1 + 1, N_PLAYERS):
            for t in range(N_TURNS):
                tt = model.NewBoolVar(f"tm_turn_{p1}_{p2}_{t}")
                aux = []
                for g in range(N_GROUPS):
                    aux.append(pair[(p1, p2, t, g)])
                if aux:
                    model.AddMaxEquality(tt, aux)
                else:
                    model.Add(tt == 0)
                teammate_turn[(p1, p2, t)] = tt

    opponent_turn = {}
    for p1 in range(N_PLAYERS):
        for p2 in range(p1 + 1, N_PLAYERS):
            for t in range(N_TURNS):
                opp_t = model.NewBoolVar(f"opp_turn_{p1}_{p2}_{t}")
                sg = same_group[(p1, p2, t)]
                tt = teammate_turn[(p1, p2, t)]
                model.AddBoolAnd([sg, tt.Not()]).OnlyEnforceIf(opp_t)
                model.AddBoolOr([sg.Not(), tt]).OnlyEnforceIf(opp_t.Not())
                opponent_turn[(p1, p2, t)] = opp_t

    opp = [[model.NewIntVar(0, N_TURNS, f"opp_{i}_{j}")
            for j in range(N_PLAYERS)]
            for i in range(N_PLAYERS)]

    for p1 in range(N_PLAYERS):
        for p2 in range(p1 + 1, N_PLAYERS):
            model.Add(
                opp[p1][p2] ==
                sum(opponent_turn[(p1, p2, t)] for t in range(N_TURNS))
            )
            model.Add(opp[p2][p1] == opp[p1][p2])

    max_opp = model.NewIntVar(0, 2, "max_opp")
    for i in range(N_PLAYERS):
        for j in range(i + 1, N_PLAYERS):
            model.Add(opp[i][j] <= max_opp)

    distinct_opp = [
        model.NewIntVar(0, N_PLAYERS - 1, f"distinct_opp_{i}")
        for i in range(N_PLAYERS)
    ]

    for i in range(N_PLAYERS):
        bools = []
        for j in range(N_PLAYERS):
            if i == j:
                continue
            b = model.NewBoolVar(f"has_opp_{i}_{j}")
            model.Add(opp[i][j] >= 1).OnlyEnforceIf(b)
            model.Add(opp[i][j] == 0).OnlyEnforceIf(b.Not())
            bools.append(b)
        model.Add(distinct_opp[i] == sum(bools))

    min_distinct = model.NewIntVar(0, N_PLAYERS - 1, "min_distinct")
    model.AddMinEquality(min_distinct, distinct_opp)

    two_count = [
        model.NewIntVar(0, N_PLAYERS, f"two_count_{i}")
        for i in range(N_PLAYERS)
    ]

    for i in range(N_PLAYERS):
        flags = []
        for j in range(N_PLAYERS):
            if i == j:
                continue
            b = model.NewBoolVar(f"opp2_{i}_{j}")
            model.Add(opp[i][j] == 2).OnlyEnforceIf(b)
            model.Add(opp[i][j] != 2).OnlyEnforceIf(b.Not())
            flags.append(b)
        model.Add(two_count[i] == sum(flags))

    model.Minimize(
        200 * max_opp +
        20 * sum(two_count[i] for i in range(N_PLAYERS)) +
        5 * sum(opp[i][j] for i in range(N_PLAYERS) for j in range(i + 1, N_PLAYERS)) -
        40 * min_distinct
    )

    return pair

def solve_draft16(names):
    if len(names) != N_PLAYERS:
        raise ValueError(f"Servono esattamente {N_PLAYERS} nomi.")

    model, x = build_model()
    pair = add_constraints_v7_5(model, x)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 300
    solver.parameters.num_search_workers = 8

    result = solver.Solve(model)
    if result not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("Nessuna soluzione trovata per il draft 16.")

    rows = []
    for t in range(N_TURNS):
        for g in range(N_GROUPS):
            coppie = []
            for p1 in range(N_PLAYERS):
                for p2 in range(p1 + 1, N_PLAYERS):
                    if solver.Value(pair[(p1, p2, t, g)]) == 1:
                        coppie.append((p1, p2))
            if len(coppie) != 2:
                continue
            (a1, a2), (b1, b2) = coppie
            rows.append({
                "Turno": t + 1,
                "Campo": g + 1,
                "Coppia A": f"{names[a1]} & {names[a2]}",
                "Coppia B": f"{names[b1]} & {names[b2]}",
            })

    df = pd.DataFrame(rows)
    return df
