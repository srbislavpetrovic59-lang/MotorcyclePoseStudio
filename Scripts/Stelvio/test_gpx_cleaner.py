from gpx_cleaner import remove_immediate_backtracks


def test_remove_immediate_backtracks():
    points = [
        (0, 0),
        (1, 0),
        (0, 0),  # Povratak A -> B -> A
        (2, 0),
        (2, 0),  # Uzastopni duplikat
        (3, 0),
    ]

    original = points.copy()

    cleaned = remove_immediate_backtracks(points)

    assert cleaned == [
        (0, 0),
        (2, 0),
        (3, 0),
    ]

    # Originalna lista mora ostati nepromenjena.
    assert points == original


import xml.etree.ElementTree as ET
from pathlib import Path

from pyproj import Geod


def test_stelvio_gpx_cleaning_regression():
    gpx_path = Path(
        r"C:\Vezbe\MotorcyclePoseSim\stelvio_terrain"
        r"\data\salita-al-passo-dello-stelvio-da-prato.gpx"
    )

    root = ET.parse(gpx_path).getroot()

    points = [
        (float(e.attrib["lon"]), float(e.attrib["lat"]))
        for e in root.iter()
        if e.tag.split("}")[-1] == "trkpt"
    ]

    cleaned = remove_immediate_backtracks(points)

    assert len(points) == 534
    assert len(cleaned) == 522

    geod = Geod(ellps="WGS84")

    length = sum(
        geod.inv(*a, *b)[2]
        for a, b in zip(cleaned, cleaned[1:])
    )

    assert abs(length - 24539.781) < 0.01


from stelvio_hairpins import STELVIO_HAIRPINS


def test_stelvio_hairpin_indices_fit_cleaned_route():
    cleaned_point_count = 522

    assert len(STELVIO_HAIRPINS) == 8

    for i, j, direction in STELVIO_HAIRPINS:
        assert 0 <= i < j < cleaned_point_count
        assert j == i + 1
        assert direction in ("LEFT", "RIGHT")


def test_stelvio_hairpins_have_sharp_turns():
    gpx_path = Path(
        r"C:\Vezbe\MotorcyclePoseSim\stelvio_terrain"
        r"\data\salita-al-passo-dello-stelvio-da-prato.gpx"
    )

    root = ET.parse(gpx_path).getroot()

    points = [
        (float(e.attrib["lon"]), float(e.attrib["lat"]))
        for e in root.iter()
        if e.tag.split("}")[-1] == "trkpt"
    ]

    cleaned = remove_immediate_backtracks(points)
    geod = Geod(ellps="WGS84")

    for i, j, direction in STELVIO_HAIRPINS:
        az_before, _, _ = geod.inv(
            *cleaned[i - 2],
            *cleaned[i - 1]
        )

        az_after, _, _ = geod.inv(
            *cleaned[j + 1],
            *cleaned[j + 2]
        )

        change = (
            az_after - az_before + 180
        ) % 360 - 180

        assert abs(change) >= 130, (
            f"P{i}-P{j}: "
            f"skretanje samo {change:.1f} stepeni"
        )