import math


def signed_polygon_area(poly):
    area = 0.0
    n = len(poly)

    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]

        area += x1 * y2 - x2 * y1

    return area / 2.0


def projection_t(p, a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]

    length_sq = dx * dx + dy * dy

    if length_sq == 0:
        return 0.0

    return (
        (p[0] - a[0]) * dx
        + (p[1] - a[1]) * dy
    ) / length_sq


def distance_to_segment(p, a, b):
    t = projection_t(p, a, b)

    # Ogranicavamo projekciju na duz AB.
    t = max(0.0, min(1.0, t))

    closest_x = a[0] + t * (b[0] - a[0])
    closest_y = a[1] + t * (b[1] - a[1])

    return math.hypot(
        p[0] - closest_x,
        p[1] - closest_y
    )


def inner_offset(a, b, side, distance=3.0):
    dx = b[0] - a[0]
    dy = b[1] - a[1]

    length = math.hypot(dx, dy)

    if length == 0:
        raise ValueError("Segment nulte duzine")

    # Jedinicna normala ulevo
    nx = -dy / length
    ny = dx / length

    offset_x = side * distance * nx
    offset_y = side * distance * ny

    return (
        (a[0] + offset_x, a[1] + offset_y),
        (b[0] + offset_x, b[1] + offset_y),
    )


def line_intersection(a, b, c, d):
    x1, y1 = a
    x2, y2 = b
    x3, y3 = c
    x4, y4 = d

    denominator = (
        (x1 - x2) * (y3 - y4)
        - (y1 - y2) * (x3 - x4)
    )

    if abs(denominator) < 1e-12:
        return None

    det1 = x1 * y2 - y1 * x2
    det2 = x3 * y4 - y3 * x4

    x = (
        det1 * (x3 - x4)
        - (x1 - x2) * det2
    ) / denominator

    y = (
        det1 * (y3 - y4)
        - (y1 - y2) * det2
    ) / denominator

    return (x, y)


def inner_intersection(g, distance=3.0):
    p0, p1, p2, p3 = g["points"]

    side = 1 if g["direction"] == "LEFT" else -1

    # Unutrasnja ivica prvog segmenta
    a, b = inner_offset(p0, p1, side, distance)

    # Unutrasnja ivica poslednjeg segmenta
    c, d = inner_offset(p2, p3, side, distance)

    return line_intersection(a, b, c, d)


def make_outer_arc(center, start, end, side, radius=3.0):
    a1 = math.atan2(
        start[1] - center[1],
        start[0] - center[0]
    )
    a2 = math.atan2(
        end[1] - center[1],
        end[0] - center[0]
    )

    sweep = math.atan2(
        math.sin(a2 - a1),
        math.cos(a2 - a1)
    )

    if side * sweep < 0:
        sweep += side * 2 * math.pi

    steps = max(
        1,
        math.ceil(abs(math.degrees(sweep)) / 5.0)
    )

    return [
        (
            center[0] + radius * math.cos(a1 + sweep * k / steps),
            center[1] + radius * math.sin(a1 + sweep * k / steps)
        )
        for k in range(steps + 1)
    ]



def point_on_segment(p, a, b, eps=1e-9):
    cross = (
        (b[0] - a[0]) * (p[1] - a[1])
        - (b[1] - a[1]) * (p[0] - a[0])
    )

    if abs(cross) > eps:
        return False

    return (
        min(a[0], b[0]) - eps <= p[0] <= max(a[0], b[0]) + eps
        and
        min(a[1], b[1]) - eps <= p[1] <= max(a[1], b[1]) + eps
    )

def segments_cross(a, b, c, d, eps=1e-9):
    def orientation(p, q, r):
        return (
            (q[0] - p[0]) * (r[1] - p[1])
            - (q[1] - p[1]) * (r[0] - p[0])
        )

    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)

    # Pravi presek dve duži
    if (
        ((o1 > eps and o2 < -eps) or
         (o1 < -eps and o2 > eps))
        and
        ((o3 > eps and o4 < -eps) or
         (o3 < -eps and o4 > eps))
    ):
        return True

    # Dodirivanje i kolinearne duži
    return (
        (abs(o1) <= eps and point_on_segment(c, a, b))
        or (abs(o2) <= eps and point_on_segment(d, a, b))
        or (abs(o3) <= eps and point_on_segment(a, c, d))
        or (abs(o4) <= eps and point_on_segment(b, c, d))
    )


def polygon_self_intersects(poly):
    n = len(poly)

    if n < 3:
        return False

    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]

        for j in range(i + 1, n):
            # Preskačemo susedne ivice
            if j == i + 1:
                continue

            # Prva i poslednja ivica su susedne
            if i == 0 and j == n - 1:
                continue

            c = poly[j]
            d = poly[(j + 1) % n]

            if segments_cross(a, b, c, d):
                return True

    return False


def triangle_area(a, b, c):
    return abs(
        (b[0] - a[0]) * (c[1] - a[1])
        - (b[1] - a[1]) * (c[0] - a[0])
    ) / 2.0



def triangulation_area_ok(poly, triangles, tolerance=1e-6):
    polygon_area = abs(signed_polygon_area(poly))

    triangles_area = sum(
        triangle_area(
            poly[i],
            poly[j],
            poly[k]
        )
        for i, j, k in triangles
    )

    return abs(polygon_area - triangles_area) <= tolerance


def triangle_indices_valid(poly, triangles):
    n = len(poly)

    return all(
        len(triangle) == 3
        and all(
            isinstance(index, int)
            and 0 <= index < n
            for index in triangle
        )
        and len(set(triangle)) == 3
        for triangle in triangles
    )


def triangles_non_degenerate(poly, triangles, eps=1e-9):
    return all(
        triangle_area(
            poly[i],
            poly[j],
            poly[k]
        ) > eps
        for i, j, k in triangles
    )


def validate_triangulation(poly, triangles):
    if len(poly) < 3:
        return False

    if polygon_self_intersects(poly):
        return False

    if len(triangles) != len(poly) - 2:
        return False

    if not triangle_indices_valid(poly, triangles):
        return False

    if not triangles_non_degenerate(poly, triangles):
        return False

    if not triangulation_area_ok(poly, triangles):
        return False

    if triangulation_has_overlaps(poly, triangles):
        return False

    return True


def orientation(a, b, c):
    return (
        (b[0] - a[0]) * (c[1] - a[1])
        - (b[1] - a[1]) * (c[0] - a[0])
    )


def point_strictly_inside_triangle(p, a, b, c, eps=1e-9):
    o1 = orientation(a, b, p)
    o2 = orientation(b, c, p)
    o3 = orientation(c, a, p)

    return (
        (o1 > eps and o2 > eps and o3 > eps)
        or
        (o1 < -eps and o2 < -eps and o3 < -eps)
    )


def segments_properly_cross(a, b, c, d, eps=1e-9):
    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)

    return (
        (
            (o1 > eps and o2 < -eps)
            or (o1 < -eps and o2 > eps)
        )
        and
        (
            (o3 > eps and o4 < -eps)
            or (o3 < -eps and o4 > eps)
        )
    )


def triangles_overlap(t1, t2):
    a, b, c = t1
    d, e, f = t2

    edges1 = [(a, b), (b, c), (c, a)]
    edges2 = [(d, e), (e, f), (f, d)]

    # Pravi preseci ivica
    for p, q in edges1:
        for r, s in edges2:
            if segments_properly_cross(p, q, r, s):
                return True

    # Teme strogo unutar drugog trougla
    for p in t1:
        if point_strictly_inside_triangle(p, d, e, f):
            return True

    for p in t2:
        if point_strictly_inside_triangle(p, a, b, c):
            return True

        # Provera tezista oba trougla
    centroid1 = (
        (a[0] + b[0] + c[0]) / 3.0,
        (a[1] + b[1] + c[1]) / 3.0,
    )

    centroid2 = (
        (d[0] + e[0] + f[0]) / 3.0,
        (d[1] + e[1] + f[1]) / 3.0,
    )

    if point_strictly_inside_triangle(
        centroid1, d, e, f
    ):
        return True

    if point_strictly_inside_triangle(
        centroid2, a, b, c
    ):
        return True
    
    return False

def triangulation_has_overlaps(poly, triangles):
    n = len(triangles)

    for i in range(n):
        t1 = tuple(poly[k] for k in triangles[i])

        for j in range(i + 1, n):
            t2 = tuple(poly[k] for k in triangles[j])

            if triangles_overlap(t1, t2):
                return True

    return False


def normalize_polygon_ccw(poly):
    result = list(poly)

    if signed_polygon_area(result) < 0:
        result.reverse()

    return result

