"""Solver-status helpers."""
VALID_SOLVER_STATUSES={"optimal","infeasible","unbounded","solver_error"}
def is_success(status:str)->bool:
    if status not in VALID_SOLVER_STATUSES: raise ValueError(f"Unknown solver status: {status}")
    return status=="optimal"
