import numpy as np

from stelvio_transitions import load_stelvio_points
from road_geometry import (
    build_stelvio_centerline,
    densify_centerline,
)


GPX_PATH = (
    r"C:\Vezbe\MotorcyclePoseSim"
    r"\stelvio_terrain\data"
    r"\salita-al-passo-dello-stelvio-da-prato.gpx"
)


def test_stelvio_reconstructed_centerline():
    original = np.asarray(load_stelvio_points(GPX_PATH))

    centerline = build_stelvio_centerline(original)

    assert len(original) == 522
    assert len(centerline) == 41633
    assert np.all(np.isfinite(centerline))

    distances = np.linalg.norm(
        np.diff(centerline, axis=0),
        axis=1,
    )

    assert np.all(distances > 0)

    dense = densify_centerline(
        centerline,
        max_step=5.0,
    )

    dense_distances = np.linalg.norm(
        np.diff(dense, axis=0),
        axis=1,
    )

    assert len(dense) == 46249
    assert np.max(dense_distances) <= 5.000001

    assert np.isclose(
        np.sum(distances),
        np.sum(dense_distances),
        atol=1e-5,
    )


def test_p411_bezier_to_reconstructed_continuity():
    from road_geometry import sample_p411_transition
    from stelvio_transitions import (
        P411_BEZIER_POINTS,
        load_p411_p415_spline,
        load_p411_p415_reconstructed_path,
    )

    bezier = sample_p411_transition(1000)
    reconstructed = load_p411_p415_reconstructed_path()

    # C0: zajednicka tacka
    position_error = np.linalg.norm(
        bezier[-1] - reconstructed[0]
    )

    assert position_error < 1e-8

    # G1: pravac tangente
    p2 = np.asarray(P411_BEZIER_POINTS[2])
    p3 = np.asarray(P411_BEZIER_POINTS[3])

    tangent_bezier = 3.0 * (p3 - p2)

    spline = load_p411_p415_spline()
    u0 = spline.t[spline.k]

    tangent_spline = np.asarray(
        spline.derivative(1)(u0)
    )

    def unit(v):
        return v / np.linalg.norm(v)

    assert np.allclose(
        unit(tangent_bezier),
        unit(tangent_spline),
        atol=1e-9,
    )


def test_p411_reconstructed_curvature_continuity():
    from stelvio_transitions import (
        load_p411_p415_spline,
    )

    from pathlib import Path

    filename = (
        Path(__file__).parent
        / "stelvio_hairpin_411_415_reconstructed.npz"
    )

    with np.load(filename) as data:
        points = data["points"].copy()
        kappa = data["kappa"].copy()
        join_index = int(data["join_index"])
        up = float(data["join_parameter"])

    spline = load_p411_p415_spline()

    v = np.asarray(spline.derivative(1)(up))
    a = np.asarray(spline.derivative(2)(up))

    original_kappa = (
        v[0] * a[1] - v[1] * a[0]
    ) / np.linalg.norm(v)**3

    # G2: zakrivljenost na unutrasnjem spoju.
    assert abs(
        kappa[join_index] - original_kappa
    ) < 1e-8

    # Zavrsna zakrivljenost mora biti nula.
    assert abs(kappa[-1]) < 1e-10

    # Minimalni radijus cele rekonstruisane krive.
    rmin = 1.0 / np.max(np.abs(kappa))

    assert rmin >= 4.5 - 1e-8

    # Nema prekida putanje.
    distances = np.linalg.norm(
        np.diff(points, axis=0),
        axis=1,
    )
    assert np.all(distances > 0)


def test_p411_reconstructed_exit_to_gpx():
    from pathlib import Path

    from stelvio_transitions import load_stelvio_points

    original = np.asarray(load_stelvio_points(GPX_PATH))

    filename = (
        Path(__file__).parent
        / "stelvio_transition_411_415.npz"
    )

    with np.load(filename) as data:
        points = data["points"].copy()
        theta = data["theta"].copy()
        kappa = data["kappa"].copy()

    p414 = original[414]
    p415 = original[415]

    segment = p415 - p414
    length = np.linalg.norm(segment)
    direction = segment / length

    end = points[-1]
    relative = end - p414

    along = np.dot(relative, direction)
    lateral = np.linalg.det(
        np.stack([direction, relative])
    )

    # Zavrsna tangenta iz sacuvanog ugla.
    exit_direction = np.array([
        np.cos(theta[-1]),
        np.sin(theta[-1]),
    ])

    print()
    print(f"Projekcija: {along / length:.9f}")
    print(f"Bocno odstupanje: {lateral:+.12f} m")
    print(
        "Greska tangente:",
        np.linalg.norm(exit_direction - direction),
    )
    print(f"Zavrsna kappa: {kappa[-1]:+.12f}")

    # Kraj mora biti unutar GPX segmenta.
    assert 0 < along < length

    # Kraj mora lezati na GPX pravcu.
    assert abs(lateral) < 1e-6

    # Zavrsna tangenta mora pratiti GPX pravac.
    assert np.allclose(
        exit_direction,
        direction,
        atol=1e-6,
        rtol=0,
    )

    # Izlazimo na pravac sa nultom zakrivljenoscu.
    assert abs(kappa[-1]) < 1e-10

 