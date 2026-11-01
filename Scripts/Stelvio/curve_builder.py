import numpy as np


def path_length(points):
    """Ukupna duzina polilinije u metrima."""
    points = np.asarray(points, dtype=float)

    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError("Ocekuje se niz oblika (N, 2)")

    if not np.all(np.isfinite(points)):
        raise ValueError("Koordinate moraju biti konacne")

    if len(points) < 2:
        return 0.0

    segments = np.diff(points, axis=0)
    return float(np.sum(np.linalg.norm(segments, axis=1)))


def unit_tangent(p0, p1):
    """Jedinicni vektor pravca od p0 do p1."""
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)

    if p0.shape != (2,) or p1.shape != (2,):
        raise ValueError("Tacke moraju imati po dve koordinate")

    if not np.all(np.isfinite(p0)) or not np.all(np.isfinite(p1)):
        raise ValueError("Koordinate moraju biti konacne")

    direction = p1 - p0
    length = np.linalg.norm(direction)

    if length == 0:
        raise ValueError("Tangenta nije definisana za jednake tacke")

    return direction / length

def tangent_angle(p0, p1):
    """Ugao pravca od p0 do p1, u stepenima [0, 360)."""
    tangent = unit_tangent(p0, p1)

    angle = np.degrees(
        np.arctan2(tangent[1], tangent[0])
    )

    return float(angle % 360.0)

def signed_turn_angle(p0, p1, p2):
    """Potpisana promena pravca u tacki p1, u stepenima."""
    incoming = unit_tangent(p0, p1)
    outgoing = unit_tangent(p1, p2)

    cross = (
        incoming[0] * outgoing[1]
        - incoming[1] * outgoing[0]
    )

    dot = np.dot(incoming, outgoing)

    return float(np.degrees(np.arctan2(cross, dot)))


def radius_from_three_points(p0, p1, p2):
    """Radijus kruznice kroz tri tacke, u metrima."""
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)

    if any(p.shape != (2,) for p in (p0, p1, p2)):
        raise ValueError("Svaka tacka mora imati dve koordinate")

    if not all(np.all(np.isfinite(p)) for p in (p0, p1, p2)):
        raise ValueError("Koordinate moraju biti konacne")

    a = np.linalg.norm(p1 - p0)
    b = np.linalg.norm(p2 - p1)
    c = np.linalg.norm(p2 - p0)

    if min(a, b, c) == 0:
        raise ValueError("Tacke moraju biti razlicite")

    cross = np.cross(
        p1 - p0,
        p2 - p0
    )

    double_area = abs(float(cross))

    if double_area < 1e-12 * max(a, b, c)**2:
        return float("inf")

    return float(a * b * c / (2.0 * double_area))


def minimum_path_radius(points):
    """Najmanji procenjeni radijus duz polilinije."""
    points = np.asarray(points, dtype=float)

    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError("Ocekuje se niz oblika (N, 2)")

    if not np.all(np.isfinite(points)):
        raise ValueError("Koordinate moraju biti konacne")

    if len(points) < 3:
        return float("inf")

    radii = [
        radius_from_three_points(
            points[i - 1],
            points[i],
            points[i + 1]
        )
        for i in range(1, len(points) - 1)
    ]

    return float(min(radii))


def cubic_bezier_path(p0, p1, p2, p3, samples=1001):
    """Generise uzorkovanu kubnu Bezierovu krivu."""

    if not isinstance(samples, (int, np.integer)) or samples < 2:
        raise ValueError("samples mora biti ceo broj >= 2")

    control = np.asarray([p0, p1, p2, p3], dtype=float)

    if control.shape != (4, 2):
        raise ValueError("Ocekuju se cetiri 2D kontrolne tacke")

    if not np.all(np.isfinite(control)):
        raise ValueError("Kontrolne tacke moraju biti konacne")

    t = np.linspace(0.0, 1.0, samples)
    u = 1.0 - t

    return (
        u[:, None]**3 * control[0]
        + 3 * (u**2 * t)[:, None] * control[1]
        + 3 * (u * t**2)[:, None] * control[2]
        + t[:, None]**3 * control[3]
    )


def cubic_bezier_tangents(p0, p1, p2, p3):
    """Analiticke tangente kubne Bezierove krive."""

    return {
        "entry_angle": tangent_angle(p0, p1),
        "exit_angle": tangent_angle(p2, p3),
    }


def cubic_bezier_radius(p0, p1, p2, p3, t):
    """Radijus zakrivljenosti kubne Bezierove krive u parametru t."""

    if not np.isfinite(t) or not 0.0 <= t <= 1.0:
        raise ValueError("t mora biti u intervalu [0, 1]")

    p = np.asarray([p0, p1, p2, p3], dtype=float)

    if p.shape != (4, 2) or not np.all(np.isfinite(p)):
        raise ValueError("Ocekuju se cetiri konacne 2D tacke")

    u = 1.0 - t

    d1 = 3 * (
        u**2 * (p[1] - p[0])
        + 2*u*t * (p[2] - p[1])
        + t**2 * (p[3] - p[2])
    )

    d2 = 6 * (
        u * (p[2] - 2*p[1] + p[0])
        + t * (p[3] - 2*p[2] + p[1])
    )

    speed = np.linalg.norm(d1)

    if speed == 0:
        return float("nan")

    cross = d1[0]*d2[1] - d1[1]*d2[0]

    if cross == 0:
        return float("inf")

    return float(speed**3 / abs(cross))


def minimum_bezier_radius(p0, p1, p2, p3, intervals=100):
    """Numericki trazi minimalni radijus kubne Bezierove krive."""

    from scipy.optimize import minimize_scalar

    if not isinstance(intervals, (int, np.integer)) or intervals < 1:
        raise ValueError("intervals mora biti pozitivan ceo broj")

    def radius(t):
        return cubic_bezier_radius(p0, p1, p2, p3, t)

    ts = np.linspace(0.0, 1.0, intervals + 1)

    candidates = [
        (radius(0.0), 0.0),
        (radius(1.0), 1.0),
    ]

    for a, b in zip(ts[:-1], ts[1:]):
        result = minimize_scalar(
            radius,
            bounds=(a, b),
            method="bounded",
            options={"xatol": 1e-12},
        )

        if result.success and np.isfinite(result.fun):
            candidates.append((result.fun, result.x))

    r_min, t_min = min(candidates)

    return {
        "minimum_radius": float(r_min),
        "parameter": float(t_min),
    }


def bezier_control_points(
    start,
    end,
    entry_angle,
    exit_angle,
    entry_handle,
    exit_handle,
):
    """Konstruise cetiri Bezierove kontrolne tacke."""

    if not np.all(np.isfinite([
        entry_angle, exit_angle,
        entry_handle, exit_handle
    ])):
        raise ValueError("Parametri moraju biti konacni")

    if entry_handle <= 0 or exit_handle <= 0:
        raise ValueError("Duzine rucica moraju biti pozitivne")

    p0 = np.asarray(start, dtype=float)
    p3 = np.asarray(end, dtype=float)

    if p0.shape != (2,) or p3.shape != (2,):
        raise ValueError("Ocekuju se 2D tacke")

    if not np.all(np.isfinite(p0)) or not np.all(np.isfinite(p3)):
        raise ValueError("Koordinate moraju biti konacne")

    a0 = np.radians(entry_angle)
    a1 = np.radians(exit_angle)

    d0 = np.array([np.cos(a0), np.sin(a0)])
    d1 = np.array([np.cos(a1), np.sin(a1)])

    p1 = p0 + entry_handle * d0
    p2 = p3 - exit_handle * d1

    return p0, p1, p2, p3


def solve_exit_handle(
    start,
    end,
    entry_angle,
    exit_angle,
    entry_handle,
    target_radius=4.5,
    lower=2.0,
    upper=2.5,
):
    """Nalazi izlaznu rucicu za zadati minimalni radijus."""

    from scipy.optimize import brentq

    if not np.isfinite(target_radius) or target_radius <= 0:
        raise ValueError("target_radius mora biti pozitivan")

    if not (
        np.isfinite(lower)
        and np.isfinite(upper)
        and 0 < lower < upper
    ):
        raise ValueError("Neispravne granice pretrage")

    def radius_error(handle):
        points = bezier_control_points(
            start,
            end,
            entry_angle,
            exit_angle,
            entry_handle,
            handle,
        )

        result = minimum_bezier_radius(*points)

        return result["minimum_radius"] - target_radius

    f_lower = radius_error(lower)
    f_upper = radius_error(upper)

    if not (np.isfinite(f_lower) and np.isfinite(f_upper)):
        raise ValueError("Radijus nije konacan na granicama")

    if f_lower * f_upper > 0:
        raise ValueError(
            "Interval ne obuhvata resenje za zadati radijus"
        )

    return float(
        brentq(
            radius_error,
            lower,
            upper,
            xtol=1e-10,
        )
    )


def find_radius_bracket(
    radius_error,
    lower=0.5,
    upper=10.0,
    steps=100,
):
    """Pronalazi interval u kojem greska radijusa menja znak."""

    if not (
        np.isfinite(lower)
        and np.isfinite(upper)
        and 0 < lower < upper
    ):
        raise ValueError("Neispravne granice pretrage")

    if not isinstance(steps, (int, np.integer)) or steps < 1:
        raise ValueError("steps mora biti pozitivan ceo broj")

    handles = np.linspace(lower, upper, steps + 1)

    previous_handle = None
    previous_error = None

    for handle in handles:
        error = float(radius_error(handle))

        if not np.isfinite(error):
            continue

        if error == 0:
            return float(handle), float(handle)

        if previous_error is not None:
            if np.sign(error) != np.sign(previous_error):
                return float(previous_handle), float(handle)

        previous_handle = handle
        previous_error = error

    raise ValueError("Nije pronadjen interval promene znaka")


def auto_exit_handle(
    start,
    end,
    entry_angle,
    exit_angle,
    entry_handle,
    target_radius=4.5,
    search_lower=0.5,
    search_upper=5.0,
    search_steps=20,
):
    """Automatski pronalazi izlaznu Bezierovu rucicu."""

    def radius_error(handle):
        points = bezier_control_points(
            start,
            end,
            entry_angle,
            exit_angle,
            entry_handle,
            handle,
        )

        result = minimum_bezier_radius(*points)

        return result["minimum_radius"] - target_radius

    lower, upper = find_radius_bracket(
        radius_error,
        lower=search_lower,
        upper=search_upper,
        steps=search_steps,
    )

    if lower == upper:
        return lower

    return solve_exit_handle(
        start=start,
        end=end,
        entry_angle=entry_angle,
        exit_angle=exit_angle,
        entry_handle=entry_handle,
        target_radius=target_radius,
        lower=lower,
        upper=upper,
    )


