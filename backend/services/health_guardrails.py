from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class UserHealthProfile:
    user_id: Optional[int] = None
    allergies: List[str] = None  # e.g., ['peanuts', 'shellfish']
    has_asthma: bool = False
    has_heart_condition: bool = False
    medications: List[str] = None


def _contains_allergy(user: UserHealthProfile, allergen: str) -> bool:
    if not user or not user.allergies:
        return False
    return allergen.lower() in (a.lower() for a in user.allergies)


def evaluate_health_risk(user: UserHealthProfile, candidate: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate health risk for a candidate itinerary item/place.

    Args:
        user: UserHealthProfile (opt-in; may be None)
        candidate: dict describing the item (type, tags, place metadata)
        context: dict with live signals (aqi, heat_index, alerts, timestamp)

    Returns:
        dict with keys: safe (bool), reasons (List[str]), clinician_review_required (bool), explainability (dict)
    """
    reasons: List[str] = []
    clinician_required = False
    confidence = 1.0
    sources: List[str] = []

    aqi = context.get("aqi")
    heat_index = context.get("heat_index")
    alerts = context.get("alerts", [])

    # Rule: Asthma + AQI > 150
    if user and user.has_asthma and aqi is not None:
        sources.append("AQI")
        if aqi > 150:
            reasons.append("User has asthma and current AQI is >150: outdoor exertion unsafe.")
            clinician_required = False
            confidence = min(confidence, 0.95)

    # Rule: Severe nut allergy + place indicates nuts
    place_allergen_flags = []
    if isinstance(candidate.get("place"), dict):
        place_allergen_flags = candidate["place"].get("allergen_flags", [])

    if user and user.allergies:
        for a in user.allergies:
            if a.lower() in ("peanut", "nuts", "tree nuts"):
                if any(f.lower().find("nut") != -1 or f.lower().find("peanut") != -1 for f in place_allergen_flags):
                    reasons.append("Place reports nut allergen flags that may expose a user with severe nut allergy.")
                    clinician_required = True
                    confidence = min(confidence, 0.9)
                    sources.append("place.allergen_flags")

    # Rule: Heart condition + heat advisory (heat_index threshold)
    if user and user.has_heart_condition and heat_index is not None:
        sources.append("heat_index")
        if heat_index >= 100:
            reasons.append("User has heart condition and heat index is high: reduce exertion and seek cool environments.")
            clinician_required = False
            confidence = min(confidence, 0.9)

    # If any active emergency alert in context (fires, floods) treat as high-risk
    for alert in alerts:
        if alert.get("severity") in ("critical", "severe"):
            reasons.append(f"Active alert: {alert.get('title')}")
            clinician_required = True if alert.get("type") == "health" else clinician_required
            confidence = min(confidence, 0.8)
            sources.append(alert.get("source", "alert"))

    safe = len(reasons) == 0

    explainability = {
        "why": reasons or ["No deterministic health guardrail triggered."],
        "confidence": confidence,
        "sources": sources,
        "timestamp": context.get("timestamp")
    }

    return {
        "safe": safe,
        "reasons": reasons,
        "clinician_review_required": clinician_required,
        "explainability": explainability,
    }


__all__ = ["UserHealthProfile", "evaluate_health_risk"]