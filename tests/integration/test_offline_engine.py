from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_engine_has_no_runtime_network_imports() -> None:
    forbidden = ("import requests", "import httpx", "import aiohttp", "urllib.request")
    for path in (ROOT / "src" / "industrial_energy_lab").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden), f"Network import found in {path}"
