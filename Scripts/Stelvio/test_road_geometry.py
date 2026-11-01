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

def test_stelvio_csv_matches_generated_road():
    from generate_stelvio_road import generate_stelvio_road
    from pathlib import Path

    filename = (
        Path(__file__).parent
        / "stelvio_centerline.csv"
    )

    exported = np.loadtxt(
        filename,
        delimiter=",",
        skiprows=1,
    )

    generated = generate_stelvio_road()

    assert exported.shape == generated.shape

    assert np.allclose(
        exported,
        generated,
        atol=1e-8,
        rtol=0,
    )

def test_stelvio_unreal_csv_conversion():
    from pathlib import Path

    folder = Path(__file__).parent

    meters = np.loadtxt(
        folder / "stelvio_centerline.csv",
        delimiter=",",
        skiprows=1,
    )

    centimeters = np.loadtxt(
        folder / "stelvio_centerline_ue.csv",
        delimiter=",",
        skiprows=1,
    )

    assert meters.shape == centimeters.shape
    assert len(meters) == 46249

    assert np.allclose(
        centimeters,
        meters * 100.0,
        atol=1e-5,
        rtol=0,
    )


def test_stelvio_arc_length_position():
    from arc_length_path import ArcLengthPath
    from generate_stelvio_road import generate_stelvio_road

    road = generate_stelvio_road()
    path = ArcLengthPath(road)

    # Ukupna duzina trase.
    assert np.isclose(
        path.length,
        24533.282208852,
        atol=1e-5,
    )

    # Pocetak i kraj trase.
    assert np.allclose(path.point_at(0), road[0])
    assert np.allclose(
        path.point_at(path.length),
        road[-1],
    )

    # Polozaj motocikla na 12.500 m.
    position = path.point_at(12500.0)
    heading = path.heading_at(12500.0)

    assert position.shape == (2,)
    assert np.all(np.isfinite(position))
    assert np.isfinite(heading)

    print()
    print(f"Polozaj na 12500 m: {position}")
    print(f"Pravac motocikla: {heading:.6f} deg")


def test_stelvio_arc_length_unreal_units():
    from arc_length_path import ArcLengthPath
    from generate_stelvio_road import generate_stelvio_road

    road_m = generate_stelvio_road()
    road_cm = road_m * 100.0

    path_m = ArcLengthPath(road_m)
    path_cm = ArcLengthPath(road_cm)

    distance_m = 12500.0

    position_m = path_m.point_at(distance_m)
    position_cm = path_cm.point_at(distance_m * 100.0)

    heading_m = path_m.heading_at(distance_m)
    heading_cm = path_cm.heading_at(distance_m * 100.0)

    assert np.allclose(
        position_cm,
        position_m * 100.0,
        atol=1e-5,
        rtol=0,
    )

    assert np.isclose(
        heading_cm,
        heading_m,
        atol=1e-5,
    )

    print()
    print(f"UE pozicija: {position_cm}")
    print(f"UE pravac: {heading_cm:.6f} deg")

def test_motorcycle_pose_at():
    from arc_length_path import ArcLengthPath

    from generate_stelvio_road import (
        generate_stelvio_road,
        motorcycle_pose_at,
    )

    road = generate_stelvio_road()
    path = ArcLengthPath(road * 100.0)

    pose = motorcycle_pose_at(path, 12500.0)

    assert set(pose) == {
        "x_cm",
        "y_cm",
        "heading_deg",
    }

    assert np.isclose(
        pose["x_cm"],
        -657565.28516364,
        atol=1e-4,
    )

    assert np.isclose(
        pose["y_cm"],
        -851719.67546342,
        atol=1e-4,
    )

    assert np.isclose(
        pose["heading_deg"],
        -50.073837,
        atol=1e-5,
    )

    # Rastojanje van trase mora biti odbijeno.
    import pytest

    with pytest.raises(ValueError):
        motorcycle_pose_at(path, -1.0)

    with pytest.raises(ValueError):
        motorcycle_pose_at(
            path,
            path.length / 100.0 + 1.0,
        )

def test_generate_motorcycle_poses():
    import pytest

    from generate_stelvio_road import (
        generate_stelvio_road,
        generate_motorcycle_poses,
    )

    road = generate_stelvio_road()
    poses = generate_motorcycle_poses(road)

    # Svaki zapis: distance_m, x_cm, y_cm, heading_deg
    assert poses.shape == (4908, 4)

    # Prvi polozaj.
    assert np.isclose(poses[0, 0], 0.0)
    assert np.allclose(poses[0, 1:3], road[0] * 100.0)

    # Poslednji polozaj.
    assert np.allclose(
        poses[-1, 1:3],
        road[-1] * 100.0,
        atol=1e-5,
    )

    # Rastojanja moraju strogo rasti.
    steps = np.diff(poses[:, 0])

    assert np.all(steps > 0)
    assert np.all(steps <= 5.000001)

    # Sve vrednosti moraju biti konacne.
    assert np.all(np.isfinite(poses))

    # Neispravan korak mora biti odbijen.
    with pytest.raises(ValueError):
        generate_motorcycle_poses(road, step_m=0)


def test_motorcycle_poses_csv_export():
    from pathlib import Path

    from generate_stelvio_road import (
        generate_stelvio_road,
        generate_motorcycle_poses,
    )

    filename = (
        Path(__file__).parent
        / "stelvio_motorcycle_poses_ue.csv"
    )

    exported = np.loadtxt(
        filename,
        delimiter=",",
        skiprows=1,
    )

    expected = generate_motorcycle_poses(
        generate_stelvio_road()
    )

    assert exported.shape == (4908, 4)

    assert np.allclose(
        exported,
        expected,
        atol=1e-8,
        rtol=0,
    )

    assert np.isclose(
        exported[0, 0],
        0.0,
    )

    assert np.isclose(
        exported[-1, 0],
        24533.282208852,
        atol=1e-5,
    )

 