"""OMIE source adapter helpers; runtime case uses offline versioned snapshots."""


def marginalpdbc_filename(date_yyyymmdd: str) -> str:
    if len(date_yyyymmdd) != 8 or not date_yyyymmdd.isdigit():
        raise ValueError("date_yyyymmdd must be YYYYMMDD digits")
    return f"marginalpdbc_{date_yyyymmdd}.1"


def public_download_url(date_yyyymmdd: str) -> str:
    name = marginalpdbc_filename(date_yyyymmdd)
    return f"https://www.omie.es/es/file-download?filename={name}&parents=marginalpdbc"
