import xml.etree.ElementTree as ET
from gpx_cleaner import remove_immediate_backtracks
from gpx_projection import project_route_to_meters

STELVIO_TRANSITION_RADIUS = 4.5
STELVIO_ROAD_WIDTH = 6.0
P411_TRANSITION_LENGTH = 20.009743
P411_START_HANDLE = 10.0
P411_END_HANDLE = 2.290115
P411_HAIRPIN = (411, 412)

def transition_control_p1(p0, direction):
    return (
        p0[0] + P411_START_HANDLE * direction[0],
        p0[1] + P411_START_HANDLE * direction[1],
    )

def transition_control_p2(p3, direction):
    return (
        p3[0] - P411_END_HANDLE * direction[0],
        p3[1] - P411_END_HANDLE * direction[1],
    )

def cubic_bezier_point(p0, p1, p2, p3, t):
    u = 1.0 - t
    return (
        u**3 * p0[0] + 3*u*u*t * p1[0] + 3*u*t*t * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3*u*u*t * p1[1] + 3*u*t*t * p2[1] + t**3 * p3[1],
    )



def load_stelvio_points(gpx_path):
    root = ET.parse(gpx_path).getroot()
    ns = {"g": "http://www.topografix.com/GPX/1/1"}

    points = [
        (float(p.get("lon")), float(p.get("lat")))
        for p in root.findall(".//g:trkpt", ns)
    ]

    return project_route_to_meters(
        remove_immediate_backtracks(points)
    )

P411_BEZIER_POINTS = (
    (-8909.79348080414, -9489.717730867722),
    (-8901.04282401414, -9484.877688957722),
    (-8893.950893073472, -9481.723749339319),
    (-8892.121748501859, -9480.345759192965),
)

def load_p488_p493_spline():
    from pathlib import Path
    import numpy as np
    from scipy.interpolate import CubicSpline

    filename = (
        Path(__file__).parent
        / "stelvio_hairpin_488_493.npz"
    )

    with np.load(filename) as data:
        s = data["s40"]
        points = data["points40"].copy()
        shifts = data["x_smooth"].reshape(5, 2)
        entry = data["entry"]
        exit_direction = data["new_exit"]
        origin = data["origin"]

    points[1:6] += shifts

    # Vracamo lokalne koordinate u sistem Stelvija
    points += origin

    return CubicSpline(
        s,
        points,
        axis=0,
        bc_type=(
            (1, entry),
            (1, exit_direction)
        )
    )

def load_s282_s285_path():
    from pathlib import Path
    import numpy as np

    filename = (
        Path(__file__).parent
        / "stelvio_hairpin_282_285.npz"
    )

    with np.load(filename) as data:
        points = data["path"].copy()

    return points