# prima (causa ImportError)
# from .logica_draft_generic import generate_ds_rounds, build_schedule_from_rounds

# dopo (corretto)
from .logica_draft_generic import generate_ds_rounds, build_schedule_with_backtracking

def solve_draft16(destri, sinistri):
    if len(destri) != 8 or len(sinistri) != 8:
        raise ValueError("solve_draft16 richiede 8 destri e 8 sinistri")
    base_rounds = generate_ds_rounds(destri, sinistri)
    return build_schedule_with_backtracking(base_rounds, set(destri))
