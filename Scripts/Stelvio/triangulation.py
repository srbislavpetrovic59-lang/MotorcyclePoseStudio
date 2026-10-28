def point_in_triangle(p, a, b, c):
    def cross(u, v, w):
        return (
            (v[0] - u[0]) * (w[1] - u[1])
            - (v[1] - u[1]) * (w[0] - u[0])
        )

    d1 = cross(a, b, p)
    d2 = cross(b, c, p)
    d3 = cross(c, a, p)

    eps = 1e-9

    return (
        d1 >= -eps
        and d2 >= -eps
        and d3 >= -eps
    )


def find_ear(poly, indices):
    n = len(indices)

    for k in range(n):
        ia = indices[(k - 1) % n]
        ib = indices[k]
        ic = indices[(k + 1) % n]

        a, b, c = poly[ia], poly[ib], poly[ic]

        cross = (
            (b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0])
        )

        if cross <= 1e-9:
            continue

        if any(
            point_in_triangle(poly[idx], a, b, c)
            for idx in indices
            if idx not in (ia, ib, ic)
        ):
            continue

        return k, (ia, ib, ic)

    return None


def triangulate_polygon(poly):
    remaining = list(range(len(poly)))
    result = []

    while len(remaining) > 3:
        ear = find_ear(poly, remaining)

        if ear is None:
            return None

        k, triangle = ear
        result.append(triangle)
        remaining.pop(k)

    result.append(tuple(remaining))
    return result