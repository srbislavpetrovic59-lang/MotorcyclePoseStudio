import numpy as np

from stelvio_transitions import (
    P411_BEZIER_POINTS,
    cubic_bezier_point,
)


def sample_p411_transition(segments=40):
    if segments < 1:
        raise ValueError("Broj segmenata mora biti pozitivan")

    p0, p1, p2, p3 = P411_BEZIER_POINTS

    return np.array([
        cubic_bezier_point(p0, p1, p2, p3, t)
        for t in np.linspace(0.0, 1.0, segments + 1)
    ])

def sample_p488_p493_transition(segments=120):
    from stelvio_transitions import load_p488_p493_spline

    if segments < 1:
        raise ValueError("Broj segmenata mora biti pozitivan")

    curve = load_p488_p493_spline()

    parameters = np.linspace(
        curve.x[0],
        curve.x[-1],
        segments + 1
    )

    return np.asarray(curve(parameters))

def insert_p411_transition(points):
    original = np.asarray(points, dtype=float)

    if original.ndim != 2 or original.shape[1] != 2:
        raise ValueError("Ocekuje se niz GPX tacaka oblika (N, 2)")

    if len(original) <= 410:
        raise ValueError("GPX trasa nema tacku P410")

    bezier = sample_p411_transition()

    return np.vstack([
        original[:410],
        bezier,
        original[410:]
    ])

def insert_p488_p493_transition(points):
    original = np.asarray(points, dtype=float)

    if original.ndim != 2 or original.shape[1] != 2:
        raise ValueError("Ocekuje se niz GPX tacaka oblika (N, 2)")

    if len(original) <= 493:
        raise ValueError("GPX trasa nema tacku P493")

    spline = sample_p488_p493_transition()

    if (
        np.linalg.norm(spline[0] - original[488]) > 1e-6
        or np.linalg.norm(spline[-1] - original[493]) > 1e-6
    ):
        raise ValueError("Krajevi splajna ne odgovaraju GPX tackama")

    return np.vstack([
        original[:488],
        spline,
        original[494:]
    ])

def build_stelvio_centerline(points):
    # Najpre rekonstruisemo kasniju serpentinu P488-P493.
    # Tako indeksi ranijih GPX tacaka ostaju nepromenjeni.
    result = insert_p488_p493_transition(points)

    # Zatim integrisemo Bezierovu krivu i
    # rekonstruisanu serpentinu P411-P415.
    result = insert_p411_p415_reconstructed_transition(result)

    return result

def densify_centerline(points, max_step=5.0):
    original = np.asarray(points, dtype=float)

    if max_step <= 0:
        raise ValueError("Korak mora biti pozitivan")

    if original.ndim != 2 or original.shape[1] != 2:
        raise ValueError("Ocekuju se tacke oblika (N, 2)")

    if len(original) < 2:
        raise ValueError("Potrebne su najmanje dve tacke")

    result = [original[0].copy()]

    for a, b in zip(original[:-1], original[1:]):
        distance = np.linalg.norm(b - a)

        segments = max(
            1,
            int(np.ceil(distance / max_step))
        )

        for k in range(1, segments + 1):
            t = k / segments
            result.append(a + t * (b - a))

    return np.asarray(result)


def insert_p411_p415_reconstructed_transition(points):
    from stelvio_transitions import (
        load_p411_p415_reconstructed_path,
    )

    original = np.asarray(points, dtype=float)

    if original.ndim != 2 or original.shape[1] != 2:
        raise ValueError(
            "Ocekuje se niz GPX tacaka oblika (N, 2)"
        )

    if len(original) <= 415:
        raise ValueError("GPX trasa nema tacku P415")

    bezier = sample_p411_transition(1000)
    reconstructed = load_p411_p415_reconstructed_path()

    if np.linalg.norm(
        bezier[-1] - reconstructed[0]
    ) > 1e-8:
        raise ValueError(
            "Bezier i rekonstruisana kriva se ne spajaju"
        )

    return np.vstack([
        original[:410],
        bezier,
        reconstructed[1:],
        original[415:],
    ])

