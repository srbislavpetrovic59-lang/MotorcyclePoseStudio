import numpy as np
from arc_length_path import ArcLengthPath

from curve_validator import validate_curve
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


def generate_stelvio_road():
    original = np.asarray(
        load_stelvio_points(GPX_PATH),
        dtype=float,
    )

    centerline = build_stelvio_centerline(original)

    dense = densify_centerline(
        centerline,
        max_step=5.0,
    )

    return dense


def motorcycle_pose_at(path, distance_m):
    """
    Vraca polozaj i pravac motocikla
    u Unreal koordinatama.
    """
    distance_cm = distance_m * 100.0

    position = path.point_at(distance_cm)
    heading = path.heading_at(distance_cm)

    return {
        "x_cm": float(position[0]),
        "y_cm": float(position[1]),
        "heading_deg": float(heading),
    }


def generate_motorcycle_poses(road, step_m=5.0):
    if step_m <= 0:
        raise ValueError("Korak mora biti pozitivan")

    path = ArcLengthPath(road * 100.0)

    total_m = path.length / 100.0

    distances = np.arange(
        0.0,
        total_m,
        step_m,
    )

    distances = np.append(distances, total_m)

    poses = []

    for distance in distances:
        pose = motorcycle_pose_at(path, distance)

        poses.append([
            distance,
            pose["x_cm"],
            pose["y_cm"],
            pose["heading_deg"],
        ])

    return np.asarray(poses)


if __name__ == "__main__":
    road = generate_stelvio_road()
    geometry = validate_curve(road)
    
    print("Stelvio road generator")
    print(f"Broj tacaka: {len(road)}")
    print(f"Prva tacka: {road[0]}")
    print(f"Poslednja tacka: {road[-1]}")
    print("\nGeometrijska validacija:")
    print(f"Duzina trase: {geometry['length']:.3f} m")
    print(f"Minimalni radijus: {geometry['minimum_radius']:.3f} m")
    print(f"Pocetni ugao: {geometry['entry_angle']:.3f} deg")
    print(f"Zavrsni ugao: {geometry['exit_angle']:.3f} deg")
    print("Validacija: OK")
    from pathlib import Path

    output_file = (
        Path(__file__).parent
        / "stelvio_centerline.csv"
    )

    np.savetxt(
        output_file,
        road,
        delimiter=",",
        header="X_m,Y_m",
        comments="",
        fmt="%.9f",
    )

    print(f"\nCSV sacuvan: {output_file}")
    
    unreal_file = (
        Path(__file__).parent
        / "stelvio_centerline_ue.csv"
    )

    unreal_points = road * 100.0

    np.savetxt(
        unreal_file,
        unreal_points,
        delimiter=",",
        header="X_cm,Y_cm",
        comments="",
        fmt="%.6f",
    )

    print(f"Unreal CSV sacuvan: {unreal_file}")

    poses = generate_motorcycle_poses(road)

    poses_file = (
        Path(__file__).parent
        / "stelvio_motorcycle_poses_ue.csv"
    )

    np.savetxt(
        poses_file,
        poses,
        delimiter=",",
        header="distance_m,x_cm,y_cm,heading_deg",
        comments="",
        fmt="%.9f",
    )

    print(f"\nPolozaji motocikla: {len(poses)}")
    print(f"CSV sacuvan: {poses_file}")