import pytest
from backend.services.health_guardrails import UserHealthProfile, evaluate_health_risk


def test_asthma_aqi_rule_triggers():
    user = UserHealthProfile(user_id=1, allergies=[], has_asthma=True)
    candidate = {"place": {}}
    context = {"aqi": 160, "timestamp": "2026-05-25T12:00:00Z"}
    result = evaluate_health_risk(user, candidate, context)
    assert result["safe"] is False
    assert any("aqi" in reason.lower() or "asthma" in reason.lower() for reason in result["reasons"])


def test_nut_allergy_triggers_clinician_review():
    user = UserHealthProfile(user_id=2, allergies=["peanut"], has_asthma=False)
    candidate = {"place": {"allergen_flags": ["contains_peanut"]}}
    context = {"aqi": 50, "timestamp": "2026-05-25T12:00:00Z"}
    result = evaluate_health_risk(user, candidate, context)
    assert result["clinician_review_required"] is True
    assert any("nut" in reason.lower() or "peanut" in reason.lower() for reason in result["reasons"])


def test_heart_heat_rule_triggers():
    user = UserHealthProfile(user_id=3, allergies=[], has_heart_condition=True)
    candidate = {"place": {}}
    context = {"heat_index": 102, "timestamp": "2026-05-25T12:00:00Z"}
    result = evaluate_health_risk(user, candidate, context)
    assert result["safe"] is False
    assert any("heat" in reason.lower() for reason in result["reasons"])
