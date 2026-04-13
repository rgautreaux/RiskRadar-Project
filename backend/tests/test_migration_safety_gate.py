from db.migrations import safety_gate


def test_safety_gate_passes_when_all_checks_pass(monkeypatch):
    monkeypatch.setattr(safety_gate, "run_preflight", lambda strict, enforce_contract=False: 0)
    monkeypatch.setattr(safety_gate, "run_schema_drift_check", lambda: 0)
    monkeypatch.setattr(safety_gate, "run_validation", lambda: 0)
    monkeypatch.setattr(safety_gate, "run_monitoring", lambda: 0)

    assert safety_gate.run_safety_gate() == 0


def test_safety_gate_fails_when_any_check_fails(monkeypatch):
    monkeypatch.setattr(safety_gate, "run_preflight", lambda strict, enforce_contract=False: 2)
    monkeypatch.setattr(safety_gate, "run_schema_drift_check", lambda: 0)
    monkeypatch.setattr(safety_gate, "run_validation", lambda: 0)
    monkeypatch.setattr(safety_gate, "run_monitoring", lambda: 0)

    assert safety_gate.run_safety_gate() == 2


def test_safety_gate_uses_non_strict_preflight_when_configured(monkeypatch):
    observed_preflight_args: list[tuple[bool, bool]] = []

    def _fake_preflight(strict: bool, enforce_contract: bool = False) -> int:
        observed_preflight_args.append((strict, enforce_contract))
        return 0

    monkeypatch.setattr(safety_gate, "run_preflight", _fake_preflight)
    monkeypatch.setattr(safety_gate, "run_schema_drift_check", lambda: 0)
    monkeypatch.setattr(safety_gate, "run_validation", lambda: 0)
    monkeypatch.setattr(safety_gate, "run_monitoring", lambda: 0)
    monkeypatch.setenv("MIGRATION_PREFLIGHT_STRICT", "false")
    monkeypatch.delenv("MIGRATION_NORMALIZATION_CONTRACT_REQUIRED", raising=False)

    assert safety_gate.run_safety_gate() == 0
    assert observed_preflight_args == [(False, False)]


def test_safety_gate_passes_contract_flag_to_preflight(monkeypatch):
    observed_preflight_args: list[tuple[bool, bool]] = []

    def _fake_preflight(strict: bool, enforce_contract: bool = False) -> int:
        observed_preflight_args.append((strict, enforce_contract))
        return 0

    monkeypatch.setattr(safety_gate, "run_preflight", _fake_preflight)
    monkeypatch.setattr(safety_gate, "run_schema_drift_check", lambda: 0)
    monkeypatch.setattr(safety_gate, "run_validation", lambda: 0)
    monkeypatch.setattr(safety_gate, "run_monitoring", lambda: 0)
    monkeypatch.setenv("MIGRATION_PREFLIGHT_STRICT", "true")
    monkeypatch.setenv("MIGRATION_NORMALIZATION_CONTRACT_REQUIRED", "true")

    assert safety_gate.run_safety_gate() == 0
    assert observed_preflight_args == [(True, True)]
