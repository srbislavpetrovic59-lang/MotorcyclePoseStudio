from triangulation import triangulate_polygon

from hairpin_geometry import (
    normalize_polygon_ccw,
    validate_triangulation,
)


def build_validated_polygon(points):
    poly = normalize_polygon_ccw(points)

    triangles = triangulate_polygon(poly)

    if not validate_triangulation(poly, triangles):
        raise ValueError("Neispravna triangulacija poligona")

    return poly, triangles