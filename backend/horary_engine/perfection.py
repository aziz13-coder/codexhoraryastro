from __future__ import annotations

from typing import Callable, Dict, Any, List

from horary_config import cfg
from .calculation.helpers import days_to_sign_exit
from .reception import TraditionalReceptionCalculator
try:
    from ..models import Planet, Aspect, HoraryChart
except ImportError:  # pragma: no cover - fallback when executed as script
    from models import Planet, Aspect, HoraryChart

CLASSICAL_PLANETS: List[Planet] = [
    Planet.SUN,
    Planet.MOON,
    Planet.MERCURY,
    Planet.VENUS,
    Planet.MARS,
    Planet.JUPITER,
    Planet.SATURN,
]

ASPECT_TYPES: List[Aspect] = [
    Aspect.CONJUNCTION,
    Aspect.SEXTILE,
    Aspect.SQUARE,
    Aspect.TRINE,
    Aspect.OPPOSITION,
]


def check_future_prohibitions(
    chart: HoraryChart,
    sig1: Planet,
    sig2: Planet,
    days_ahead: float,
    calc_future_aspect_time: Callable[[Any, Any, Aspect, float, float], float],
) -> Dict[str, Any]:
    """Scan for intervening aspects before a main perfection.

    Parameters
    ----------
    chart : HoraryChart
        Chart containing planetary positions.
    sig1, sig2 : Planet
        Significators forming the main perfection.
    days_ahead : float
        Time until the main perfection in days.
    calc_future_aspect_time : callable
        Function for computing time to a future aspect.
    """

    config = cfg()
    require_in_sign = getattr(getattr(config, "perfection", {}), "require_in_sign", True)
    allow_out_of_sign = getattr(getattr(config, "perfection", {}), "allow_out_of_sign", False)

    pos1 = chart.planets[sig1]
    pos2 = chart.planets[sig2]
    reception_calc = TraditionalReceptionCalculator()

    def _valid(t: float, p_a, p_b) -> bool:
        if t is None or t <= 0 or t >= days_ahead:
            return False
        if not require_in_sign:
            return True
        if allow_out_of_sign:
            return True
        exit_a = days_to_sign_exit(p_a.longitude, p_a.speed)
        exit_b = days_to_sign_exit(p_b.longitude, p_b.speed)
        return t < exit_a and t < exit_b

    for planet in CLASSICAL_PLANETS:
        if planet in (sig1, sig2):
            continue
        p_pos = chart.planets.get(planet)
        if not p_pos:
            continue

        for aspect in ASPECT_TYPES:
            t1 = calc_future_aspect_time(pos1, p_pos, aspect, chart.julian_day, days_ahead)
            t2 = calc_future_aspect_time(pos2, p_pos, aspect, chart.julian_day, days_ahead)

            if _valid(t1, pos1, p_pos) and _valid(t2, pos2, p_pos):
                # Both significators aspect the planet before main perfection
                if p_pos.speed > max(pos1.speed, pos2.speed):
                    t_event = max(t1, t2)
                    quality = (
                        "easier"
                        if aspect in (Aspect.CONJUNCTION, Aspect.TRINE, Aspect.SEXTILE)
                        else "with difficulty"
                    )
                    rec1 = reception_calc.calculate_comprehensive_reception(chart, planet, sig1)
                    rec2 = reception_calc.calculate_comprehensive_reception(chart, planet, sig2)
                    has_reception = rec1["type"] != "none" or rec2["type"] != "none"
                    reason = (
                        f"Perfection by translation ({aspect.display_name.lower()}): positive "
                        + (f"({quality})" if quality == "easier" else f"{quality}")
                    )
                    if has_reception and quality == "with difficulty":
                        reason += " (softened by reception)"
                    return {
                        "prohibited": False,
                        "type": "translation",
                        "translator": planet,
                        "t_event": t_event,
                        "aspect": aspect,
                        "quality": quality,
                        "reception": has_reception,
                        "reason": reason,
                    }
                if p_pos.speed < min(pos1.speed, pos2.speed):
                    t_event = max(t1, t2)
                    quality = (
                        "easier"
                        if aspect in (Aspect.CONJUNCTION, Aspect.TRINE, Aspect.SEXTILE)
                        else "with difficulty"
                    )
                    rec1 = reception_calc.calculate_comprehensive_reception(chart, planet, sig1)
                    rec2 = reception_calc.calculate_comprehensive_reception(chart, planet, sig2)
                    has_reception = rec1["type"] != "none" or rec2["type"] != "none"
                    reason = (
                        f"Perfection by collection ({aspect.display_name.lower()}): positive "
                        + (f"({quality})" if quality == "easier" else f"{quality}")
                    )
                    if has_reception and quality == "with difficulty":
                        reason += " (softened by reception)"
                    return {
                        "prohibited": False,
                        "type": "collection",
                        "collector": planet,
                        "t_event": t_event,
                        "aspect": aspect,
                        "quality": quality,
                        "reception": has_reception,
                        "reason": reason,
                    }
                # Neither translation nor collection: first contact prohibits
                if t1 <= t2:
                    return {
                        "prohibited": True,
                        "type": "prohibition",
                        "prohibitor": planet,
                        "significator": sig1,
                        "t_prohibition": t1,
                        "reason": f"{planet.value} {aspect.display_name.lower()}s {sig1.value} before perfection",
                    }
                else:
                    return {
                        "prohibited": True,
                        "type": "prohibition",
                        "prohibitor": planet,
                        "significator": sig2,
                        "t_prohibition": t2,
                        "reason": f"{planet.value} {aspect.display_name.lower()}s {sig2.value} before perfection",
                    }
            elif _valid(t1, pos1, p_pos):
                return {
                    "prohibited": True,
                    "type": "prohibition",
                    "prohibitor": planet,
                    "significator": sig1,
                    "t_prohibition": t1,
                    "reason": f"{planet.value} {aspect.display_name.lower()}s {sig1.value} before perfection",
                }
            elif _valid(t2, pos2, p_pos):
                return {
                    "prohibited": True,
                    "type": "prohibition",
                    "prohibitor": planet,
                    "significator": sig2,
                    "t_prohibition": t2,
                    "reason": f"{planet.value} {aspect.display_name.lower()}s {sig2.value} before perfection",
                }

    return {"prohibited": False, "type": "none", "reason": "No prohibitions detected"}
