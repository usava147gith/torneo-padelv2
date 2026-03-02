# from .logica_draft_generic import generate_ds_rounds, build_schedule_from_rounds
from .logica_draft_generic import generate_ds_rounds, build_schedule_with_backtracking

def solve_draft12(destri, sinistri):
    if len(destri) != 6 or len(sinistri) != 6:
        raise ValueError("solve_draft12 richiede 6 destri e 6 sinistri")
    base_rounds = generate_ds_rounds(destri, sinistri)
    return build_schedule_with_backtracking(base_rounds, set(destri))
