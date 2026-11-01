import numpy as np

from curve_builder import (
    path_length,
    minimum_path_radius,
    tangent_angle,
)


def validate_curve(points):
    """Osnovna geometrijska analiza uzorkovane putanje."""

    points = np.asarray(points, dtype=float)

    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError("Ocekuje se niz oblika (N, 2)")

    if len(points) < 3:
        raise ValueError("Potrebne su najmanje tri tacke")

    if not np.all(np.isfinite(points)):
        raise ValueError("Koordinate moraju biti konacne")

    if np.any(np.linalg.norm(np.diff(points, axis=0), axis=1) == 0):
        raise ValueError("Putanja sadrzi ponovljene susedne tacke")

    return {
        "point_count": len(points),
        "length": path_length(points),
        "minimum_radius": minimum_path_radius(points),
        "entry_angle": tangent_angle(points[0], points[1]),
        "exit_angle": tangent_angle(points[-2], points[-1]),
    }


def point_deviations(path, reference_points):
    """Najkraca rastojanja referentnih tacaka do uzorkovane putanje."""

    path = np.asarray(path, dtype=float)
    reference_points = np.asarray(reference_points, dtype=float)

    for name, array in [
        ("path", path),
        ("reference_points", reference_points),
    ]:
        if array.ndim != 2 or array.shape[1] != 2:
            raise ValueError(f"{name} mora imati oblik (N, 2)")

        if len(array) == 0:
            raise ValueError(f"{name} ne sme biti prazan")

        if not np.all(np.isfinite(array)):
            raise ValueError(f"{name} sadrzi neispravne koordinate")

    deviations = []

    for point in reference_points:
        distances = np.linalg.norm(path - point, axis=1)
        deviations.append(float(np.min(distances)))

    deviations = np.asarray(deviations)

    return {
        "deviations": deviations,
        "max_deviation": float(np.max(deviations)),
        "rmse": float(np.sqrt(np.mean(deviations**2))),
    }


def validate_reference_range(
    path,
    satellite_points,
    start_index,
    end_index,
):
    """Proverava odstupanja za izabrani opseg GPX tacaka."""

    satellite_points = np.asarray(
        satellite_points,
        dtype=float
    )

    if satellite_points.ndim != 2 or satellite_points.shape[1] != 2:
        raise ValueError("Ocekuju se GPX tacke oblika (N, 2)")

    if not (0 <= start_index <= end_index < len(satellite_points)):
        raise ValueError("Neispravan opseg GPX tacaka")

    reference = satellite_points[start_index:end_index + 1]

    return point_deviations(path, reference)


from curve_builder import (
    cubic_bezier_path,
    cubic_bezier_tangents,
    minimum_bezier_radius,
)


def validate_bezier(p0, p1, p2, p3, samples=1001):
    """Kompletna geometrijska analiza kubne Bezierove krive."""

    path = cubic_bezier_path(
        p0, p1, p2, p3,
        samples=samples,
    )

    geometry = validate_curve(path)
    tangents = cubic_bezier_tangents(p0, p1, p2, p3)
    radius = minimum_bezier_radius(p0, p1, p2, p3)

    return {
        "length": geometry["length"],
        "minimum_radius": radius["minimum_radius"],
        "radius_parameter": radius["parameter"],
        "entry_angle": tangents["entry_angle"],
        "exit_angle": tangents["exit_angle"],
        "point_count": geometry["point_count"],
    }


