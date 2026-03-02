# logiche/logica_draft12.py
from .logica_draft_generic import generate_ds_rounds, build_schedule_from_rounds

def solve_draft12(destri, sinistri):
    """
    destri: list di 6 nomi
    sinistri: list di 6 nomi
    ritorna: pd.DataFrame con Turno, Campo, Coppia A, Coppia B (6 turni)
    """
    if len(destri) != 6 or len(sinistri) != 6:
        raise ValueError("solve_draft12 richiede 6 destri e 6 sinistri")
    base_rounds = generate_ds_rounds(destri, sinistri)
    return build_schedule_from_rounds(base_rounds)
