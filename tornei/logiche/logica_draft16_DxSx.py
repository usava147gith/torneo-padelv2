# logiche/logica_draft16.py
from .logica_draft_generic import generate_ds_rounds, build_schedule_from_rounds

def solve_draft16(destri, sinistri):
    """
    destri: list di 8 nomi (D0..D7)
    sinistri: list di 8 nomi (S0..S7)
    ritorna: pd.DataFrame con Turno, Campo, Coppia A, Coppia B (8 turni)
    """
    if len(destri) != 8 or len(sinistri) != 8:
        raise ValueError("solve_draft16 richiede 8 destri e 8 sinistri")
    base_rounds = generate_ds_rounds(destri, sinistri)
    return build_schedule_from_rounds(base_rounds)
