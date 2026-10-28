"""Transparent heuristic ranking; not a trained model or investment recommendation."""
from typing import Any

def rank_observation(*, momentum_pct: float | None, relative_volume: float | None,
                     volatility_pct: float | None) -> dict[str, Any]:
    missing = [name for name, value in {
        "momentum_pct": momentum_pct,
        "relative_volume": relative_volume,
        "volatility_pct": volatility_pct,
    }.items() if value is None]
    if missing:
        return {"status": "unavailable", "score": None, "missing_inputs": missing,
                "method": "transparent_heuristic_v1"}
    # Bound each component to reduce extreme-input domination.
    momentum = max(-10.0, min(10.0, float(momentum_pct))) / 10.0
    volume = max(0.0, min(3.0, float(relative_volume))) / 3.0
    volatility = max(0.0, min(10.0, float(volatility_pct))) / 10.0
    score = 50.0 + 30.0 * momentum + 15.0 * (volume - 0.5) - 10.0 * volatility
    score = round(max(0.0, min(100.0, score)), 2)
    return {"status": "computed", "score": score,
            "method": "transparent_heuristic_v1",
            "disclaimer": "Experimental score, not a probability of profit or a trained AI prediction."}
