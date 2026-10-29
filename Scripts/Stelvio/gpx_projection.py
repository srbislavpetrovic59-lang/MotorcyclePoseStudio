from pyproj import Transformer


_transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32632",
    always_xy=True,
)


def project_route_to_meters(points):
    """
    Pretvara (lon, lat) koordinate u lokalne
    ravanske (x, y) koordinate u metrima.

    Prva tacka postaje (0, 0).
    Redosled tacaka ostaje nepromenjen.
    """
    if not points:
        return []

    origin_lon, origin_lat = points[0]

    origin_x, origin_y = _transformer.transform(
        origin_lon, origin_lat
    )

    result = []

    for lon, lat in points:
        x, y = _transformer.transform(lon, lat)

        result.append((
            x - origin_x,
            y - origin_y,
        ))

    return result