"""Rebuild the versioned representative Castellón ceramic electrical case."""
from pathlib import Path
from industrial_energy_lab.case_studies.ceramic_castellon import build_case

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    meta = build_case(ROOT / "cases" / "ceramic_castellon")
    print(f"Built {meta['case_version']} / {meta['dataset_version']}")
    print(meta["load"]["statistics"])
