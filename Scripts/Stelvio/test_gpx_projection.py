import pytest

from gpx_projection import project_route_to_meters


def test_projection_preserves_origin_and_distance():
    points = [
        (10.59129, 46.61702),
        (10.59092, 46.61683),
    ]

    projected = project_route_to_meters(points)

    assert len(projected) == 2

    # Prva tacka je koordinatni pocetak.
    assert projected[0][0] == pytest.approx(0.0)
    assert projected[0][1] == pytest.approx(0.0)

    # Druga tacka mora biti razlicita od prve.
    assert projected[1] != projected[0]


import math

from pyproj import Geod


def test_projection_distance_matches_geodesic():
    points = [
        (10.59129, 46.61702),
        (10.59092, 46.61683),
    ]

    projected = project_route_to_meters(points)

    dx = projected[1][0] - projected[0][0]
    dy = projected[1][1] - projected[0][1]

    projected_distance = math.hypot(dx, dy)

    geod = Geod(ellps="WGS84")

    _, _, geodesic_distance = geod.inv(
        points[0][0],
        points[0][1],
        points[1][0],
        points[1][1],
    )

    assert projected_distance == pytest.approx(
        geodesic_distance,
        abs=0.1,
    )
