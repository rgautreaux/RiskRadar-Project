import subprocess
import sys
from pathlib import Path


def test_parity_matrix_exists():
    p = Path("docs/PARITY_MATRIX.md")
    assert p.exists(), "docs/PARITY_MATRIX.md must exist"


def test_openapi_stub_exists():
    p = Path("docs/openapi/trip_service_parity.yaml")
    assert p.exists(), "OpenAPI parity stub must exist"


def test_validate_parity_matrix_script_runs():
    script = Path("tools/validate_parity_matrix.py")
    assert script.exists(), "Validator script must exist"
    res = subprocess.run([sys.executable, str(script)], capture_output=True)
    assert res.returncode == 0, f"Parity validation failed: {res.stderr.decode() }"


def test_validate_parity_matrix_script_accepts_matrix_arg():
    script = Path("tools/validate_parity_matrix.py")
    matrix = Path("docs/PARITY_MATRIX.md")
    res = subprocess.run([sys.executable, str(script), "--matrix", str(matrix)], capture_output=True)
    assert res.returncode == 0, f"Parity validation with --matrix failed: {res.stderr.decode()}"
