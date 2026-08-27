"""Run each pytest file in an isolated process to avoid cumulative HiGHS degradation."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TEST_FILES = sorted((ROOT / "tests").glob("**/test_*.py"))


def count_tests(path: Path) -> int:
    import ast
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sum(
        1 for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    )


def main() -> int:
    streamlit_available = importlib.util.find_spec("streamlit") is not None
    passed_files = 0
    skipped_tests = 0
    expected_tests = 0
    for path in TEST_FILES:
        rel = path.relative_to(ROOT)
        n = count_tests(path)
        expected_tests += n
        if rel.as_posix() == "tests/integration/test_streamlit_smoke.py" and not streamlit_available:
            print(f"SKIP {rel} ({n} test): optional Streamlit dependency is unavailable")
            skipped_tests += n
            continue
        print(f"RUN  {rel} ({n} tests)", flush=True)
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(rel), "--disable-warnings"],
            cwd=ROOT,
            check=False,
        )
        if proc.returncode != 0:
            print(f"FAIL {rel} (exit {proc.returncode})")
            return proc.returncode
        passed_files += 1
    passed_tests = expected_tests - skipped_tests
    print(
        f"TEST MATRIX OK: {passed_tests} passed / {skipped_tests} skipped "
        f"across {len(TEST_FILES)} files ({passed_files} executed files)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
