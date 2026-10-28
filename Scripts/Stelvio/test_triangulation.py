import math
from triangulation import triangulate_polygon
from hairpin_geometry import signed_polygon_area, projection_t, distance_to_segment, inner_offset, line_intersection, inner_intersection
from hairpin_geometry import point_strictly_inside_triangle, segments_properly_cross


def triangle_area(a, b, c):
    return (
        (b[0] - a[0]) * (c[1] - a[1])
        - (b[1] - a[1]) * (c[0] - a[0])
    ) / 2.0


def check_polygon(poly, expected_area):
    triangles = triangulate_polygon(poly)

    assert triangles is not None
    assert len(triangles) == len(poly) - 2

    areas = [
        triangle_area(poly[i], poly[j], poly[k])
        for i, j, k in triangles
    ]

    assert all(area > 0 for area in areas)
    assert abs(sum(areas) - expected_area) < 1e-9


def test_square():
    poly = [(0, 0), (6, 0), (6, 6), (0, 6)]
    check_polygon(poly, 36.0)


def test_concave_pentagon():
    poly = [(0, 0), (6, 0), (6, 6), (3, 3), (0, 6)]
    check_polygon(poly, 27.0)


def test_concave_octagon():
    poly = [
        (0, 0), (8, 0), (8, 8), (6, 8),
        (6, 3), (4, 3), (4, 8), (0, 8)
    ]
    check_polygon(poly, 54.0)



def test_polygon_orientation():
    poly = [
        (0, 0),
        (6, 0),
        (6, 6),
        (0, 6),
    ]

    assert signed_polygon_area(poly) == 36.0
    assert signed_polygon_area(poly[::-1]) == -36.0



def test_projection_t():
    a = (0.0, 0.0)
    b = (10.0, 0.0)

    assert projection_t((5.0, 3.0), a, b) == 0.5
    assert projection_t((-2.0, 0.0), a, b) == -0.2
    assert projection_t((12.0, 0.0), a, b) == 1.2

    # Segment nulte duzine
    assert projection_t((5.0, 3.0), a, a) == 0.0


def test_distance_to_segment():
    a = (0.0, 0.0)
    b = (10.0, 0.0)

    # Projekcija unutar duzi
    assert distance_to_segment((5.0, 3.0), a, b) == 3.0

    # Projekcija pre tacke A
    assert distance_to_segment((-3.0, 4.0), a, b) == 5.0

    # Projekcija posle tacke B
    assert distance_to_segment((13.0, 4.0), a, b) == 5.0

    # Segment nulte duzine
    assert distance_to_segment((3.0, 4.0), a, a) == 5.0


def test_inner_offset():
    a = (0.0, 0.0)
    b = (10.0, 0.0)

    left = inner_offset(a, b, 1)
    right = inner_offset(a, b, -1)

    assert left == ((0.0, 3.0), (10.0, 3.0))
    assert right == ((0.0, -3.0), (10.0, -3.0))

    # Provera ukupne sirine puta
    assert left[0][1] - right[0][1] == 6.0


def test_line_intersection():
    # Dve prave koje se seku
    p = line_intersection(
        (0.0, 0.0), (10.0, 10.0),
        (0.0, 10.0), (10.0, 0.0)
    )

    assert p == (5.0, 5.0)

    # Paralelne prave
    q = line_intersection(
        (0.0, 0.0), (10.0, 0.0),
        (0.0, 3.0), (10.0, 3.0)
    )

    assert q is None



def test_inner_intersection():
    # Prave koje se seku
    g = {
        "points": (
            (0, 0),
            (10, 0),
            (10, 10),
            (10, 20),
        ),
        "direction": "LEFT",
    }

    p = inner_intersection(g)

    assert p is not None
    assert abs(p[0] - 7.0) < 1e-9
    assert abs(p[1] - 3.0) < 1e-9

    # Paralelne prave
    g["points"] = (
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    )

    assert inner_intersection(g) is None


from hairpin_geometry import make_outer_arc


def test_outer_arc_left():
    arc = make_outer_arc(
        (0, 0), (3, 0), (0, 3), 1
    )

    assert len(arc) == 19
    assert arc[0] == (3.0, 0.0)
    assert abs(arc[-1][0]) < 1e-9
    assert abs(arc[-1][1] - 3.0) < 1e-9

    assert all(
        abs(math.hypot(x, y) - 3.0) < 1e-9
        for x, y in arc
    )


def test_outer_arc_right():
    arc = make_outer_arc(
        (0, 0), (3, 0), (0, -3), -1
    )

    assert len(arc) == 19
    assert abs(arc[-1][0]) < 1e-9
    assert abs(arc[-1][1] + 3.0) < 1e-9

    angles = [math.atan2(y, x) for x, y in arc]

    assert all(
        angles[i + 1] < angles[i]
        for i in range(len(angles) - 1)
    )

def test_outer_arc_long_left():
    arc = make_outer_arc(
        (0, 0),
        (3, 0),
        (0, -3),
        1
    )

    assert len(arc) == 55

    assert abs(arc[0][0] - 3.0) < 1e-9
    assert abs(arc[-1][0]) < 1e-9
    assert abs(arc[-1][1] + 3.0) < 1e-9

    assert all(
        abs(math.hypot(x, y) - 3.0) < 1e-9
        for x, y in arc
    )


def test_outer_arc_long_right():
    arc = make_outer_arc(
        (0, 0),
        (3, 0),
        (0, 3),
        -1
    )

    assert len(arc) == 55

    assert abs(arc[0][0] - 3.0) < 1e-9
    assert abs(arc[-1][0]) < 1e-9
    assert abs(arc[-1][1] - 3.0) < 1e-9

    assert all(
        abs(math.hypot(x, y) - 3.0) < 1e-9
        for x, y in arc
    )


from hairpin_geometry import point_on_segment


def test_point_on_segment():
    a = (0.0, 0.0)
    b = (10.0, 0.0)

    # Tačka na duži
    assert point_on_segment((5.0, 0.0), a, b)

    # Krajnje tačke pripadaju duži
    assert point_on_segment(a, a, b)
    assert point_on_segment(b, a, b)

    # Tačka na produžetku prave
    assert not point_on_segment((15.0, 0.0), a, b)

    # Tačka izvan prave
    assert not point_on_segment((5.0, 2.0), a, b)


from hairpin_geometry import segments_cross


def test_segments_cross():
    # Dve duži koje se ukrštaju
    assert segments_cross(
        (0, 0), (10, 10),
        (0, 10), (10, 0)
    )

    # Paralelne, razdvojene duži
    assert not segments_cross(
        (0, 0), (10, 0),
        (0, 5), (10, 5)
    )

    # Dodirivanje u krajnjoj tački
    assert segments_cross(
        (0, 0), (10, 0),
        (10, 0), (10, 10)
    )

    # Kolinearne duži koje se preklapaju
    assert segments_cross(
        (0, 0), (10, 0),
        (5, 0), (15, 0)
    )

    # Kolinearne, ali razdvojene duži
    assert not segments_cross(
        (0, 0), (10, 0),
        (15, 0), (20, 0)
    )


from hairpin_geometry import polygon_self_intersects


def test_polygon_self_intersects():
    # Pravilan kvadrat — nema samopresecanja
    square = [
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    ]

    assert not polygon_self_intersects(square)

    # Leptir-masna — ivice se ukrstaju
    bowtie = [
        (0, 0),
        (10, 10),
        (0, 10),
        (10, 0),
    ]

    assert polygon_self_intersects(bowtie)

    # Konkavan, ali ispravan poligon
    concave = [
        (0, 0),
        (10, 0),
        (5, 4),
        (10, 10),
        (0, 10),
    ]

    assert not polygon_self_intersects(concave)

from hairpin_geometry import triangle_area


def test_triangle_area():
    # Pravougli trougao: 6 x 4 / 2 = 12
    a = (0, 0)
    b = (6, 0)
    c = (0, 4)

    assert abs(triangle_area(a, b, c) - 12.0) < 1e-9

    # Obrnut redosled temena
    assert abs(triangle_area(a, c, b) - 12.0) < 1e-9

    # Kolinearne tačke: površina je nula
    assert triangle_area(
        (0, 0), (5, 0), (10, 0)
    ) == 0.0


from hairpin_geometry import triangulation_area_ok


def test_triangulation_area_ok():
    # Kvadrat površine 100 m²
    poly = [
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    ]

    # Ispravna triangulacija: 50 + 50 = 100 m²
    triangles = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    assert triangulation_area_ok(poly, triangles)

    # Nedostaje jedan trougao: samo 50 m²
    incomplete = [
        (0, 1, 2),
    ]

    assert not triangulation_area_ok(poly, incomplete)


def test_real_triangulation_area():
    poly = [
        (0, 0),
        (10, 0),
        (10, 10),
        (5, 5),
        (0, 10),
    ]

    triangles = triangulate_polygon(poly)

    assert len(triangles) == len(poly) - 2
    assert triangulation_area_ok(poly, triangles)


from hairpin_geometry import triangle_indices_valid


def test_triangle_indices_valid():
    poly = [
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    ]

    # Ispravni trouglovi
    valid = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    assert triangle_indices_valid(poly, valid)

    # Indeks izvan opsega
    assert not triangle_indices_valid(
        poly, [(0, 1, 4)]
    )

    # Ponovljeno teme
    assert not triangle_indices_valid(
        poly, [(0, 1, 1)]
    )

    # Nedostaje treći indeks
    assert not triangle_indices_valid(
        poly, [(0, 1)]
    )

    # Negativan indeks
    assert not triangle_indices_valid(
        poly, [(-1, 1, 2)]
    )


from hairpin_geometry import triangles_non_degenerate


def test_triangles_non_degenerate():
    poly = [
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
        (5, 0),
    ]

    # Ispravan trougao
    assert triangles_non_degenerate(
        poly, [(0, 1, 2)]
    )

    # Tri razlicita, ali kolinearna temena
    assert not triangles_non_degenerate(
        poly, [(0, 4, 1)]
    )

    # Mesavina ispravnog i degenerisanog trougla
    assert not triangles_non_degenerate(
        poly, [(0, 1, 2), (0, 4, 1)]
    )


from hairpin_geometry import validate_triangulation


def test_validate_triangulation():
    poly = [
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    ]

    # Ispravna triangulacija
    valid = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    assert validate_triangulation(poly, valid)

    # Nedostaje trougao
    assert not validate_triangulation(
        poly, [(0, 1, 2)]
    )

    # Neispravan indeks
    assert not validate_triangulation(
        poly, [(0, 1, 4), (0, 2, 3)]
    )

    # Degenerisan trougao
    assert not validate_triangulation(
        poly, [(0, 1, 1), (0, 2, 3)]
    )

    # Samopresecajuci poligon
    bowtie = [
        (0, 0),
        (10, 10),
        (0, 10),
        (10, 0),
    ]

    assert not validate_triangulation(
        bowtie, [(0, 1, 2), (0, 2, 3)]
    )


from hairpin_geometry import orientation


def test_orientation():
    a = (0, 0)
    b = (10, 0)

    # Tacka levo od pravca A -> B
    assert orientation(a, b, (5, 5)) > 0

    # Tacka desno od pravca A -> B
    assert orientation(a, b, (5, -5)) < 0

    # Kolinearne tacke
    assert orientation(a, b, (5, 0)) == 0

    # Obrnuti smer menja znak
    assert orientation(b, a, (5, 5)) < 0





def test_point_strictly_inside_triangle():
    a = (0, 0)
    b = (10, 0)
    c = (0, 10)

    # Tacka strogo unutar trougla
    assert point_strictly_inside_triangle(
        (2, 2), a, b, c
    )

    # Tacka na ivici
    assert not point_strictly_inside_triangle(
        (5, 0), a, b, c
    )

    # Tacka izvan trougla
    assert not point_strictly_inside_triangle(
        (8, 8), a, b, c
    )

    # Obrnut redosled temena
    assert point_strictly_inside_triangle(
        (2, 2), a, c, b
    )

    # Tacka u temenu
    assert not point_strictly_inside_triangle(
        a, a, b, c
    )



def test_segments_properly_cross():
    # Pravi presek u unutrasnjosti obe duzi
    assert segments_properly_cross(
        (0, 0), (10, 10),
        (0, 10), (10, 0)
    )

    # Paralelne duzi
    assert not segments_properly_cross(
        (0, 0), (10, 0),
        (0, 5), (10, 5)
    )

    # Dodirivanje u zajednickom temenu
    assert not segments_properly_cross(
        (0, 0), (10, 0),
        (10, 0), (10, 10)
    )

    # Kolinearno preklapanje
    assert not segments_properly_cross(
        (0, 0), (10, 0),
        (5, 0), (15, 0)
    )

    # Presek u temenu samo jedne duzi
    assert not segments_properly_cross(
        (0, 0), (10, 0),
        (5, 0), (5, 10)
    )


from hairpin_geometry import triangles_overlap


def test_triangles_overlap():
    # Dva potpuno odvojena trougla
    t1 = [(0, 0), (4, 0), (0, 4)]
    t2 = [(10, 0), (14, 0), (10, 4)]

    assert not triangles_overlap(t1, t2)

    # Dva trougla koja se preklapaju
    t3 = [(0, 0), (6, 0), (0, 6)]
    t4 = [(2, 2), (8, 2), (2, 8)]

    assert triangles_overlap(t3, t4)

    # Susedni trouglovi sa zajednickom ivicom
    t5 = [(0, 0), (4, 0), (4, 4)]
    t6 = [(0, 0), (4, 4), (0, 4)]

    assert not triangles_overlap(t5, t6)



def test_triangles_overlap_identical():
    t1 = [
        (0, 0),
        (10, 0),
        (0, 10),
    ]

    t2 = [
        (0, 0),
        (10, 0),
        (0, 10),
    ]

    assert triangles_overlap(t1, t2)


def test_triangles_overlap_collinear():
    t1 = [
        (0, 0),
        (10, 0),
        (0, 10),
    ]

    t2 = [
        (0, 0),
        (10, 0),
        (10, 10),
    ]

    # Trouglovi dele osnovicu, ali su im
    # unutrasnjosti na istoj strani te osnovice.
    assert triangles_overlap(t1, t2)


from hairpin_geometry import triangulation_has_overlaps


def test_triangulation_has_overlaps():
    poly = [
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    ]

    # Ispravna triangulacija kvadrata
    valid = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    assert not triangulation_has_overlaps(poly, valid)

    # Dva identicna trougla
    overlapping = [
        (0, 1, 2),
        (0, 1, 2),
    ]

    assert triangulation_has_overlaps(poly, overlapping)

    # Samo jedan trougao
    assert not triangulation_has_overlaps(
        poly, [(0, 1, 2)]
    )


def test_validate_triangulation_rejects_overlaps():
    poly = [
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    ]

    # Dva identicna trougla
    overlapping = [
        (0, 1, 2),
        (0, 1, 2),
    ]

    assert not validate_triangulation(poly, overlapping)

    # Ispravna triangulacija istog kvadrata
    valid = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    assert validate_triangulation(poly, valid)


def test_triangles_touch_at_vertex():
    t1 = [
        (0, 0),
        (4, 0),
        (0, 4),
    ]

    t2 = [
        (0, 0),
        (-4, 0),
        (0, -4),
    ]

    # Zajednicko teme nije preklapanje
    assert not triangles_overlap(t1, t2)


def test_triangles_shared_edge_same_side():
    t1 = [
        (0, 0),
        (10, 0),
        (0, 10),
    ]

    t2 = [
        (0, 0),
        (10, 0),
        (0, 5),
    ]

    # Zajednicka osnovica, ali oba trougla
    # zauzimaju istu stranu osnovice.
    # Drugi trougao lezi unutar prvog.
    assert triangles_overlap(t1, t2)


def test_triangles_partial_shared_edge_opposite_sides():
    t1 = [
        (0, 0),
        (10, 0),
        (0, 10),
    ]

    t2 = [
        (3, 0),
        (7, 0),
        (5, -5),
    ]

    # Deo osnovice je zajednicki,
    # ali su unutrasnjosti sa suprotnih strana.
    assert not triangles_overlap(t1, t2)


def test_triangles_fully_contained():
    outer = [
        (0, 0),
        (12, 0),
        (0, 12),
    ]

    inner = [
        (2, 2),
        (5, 2),
        (2, 5),
    ]

    # Manji trougao je potpuno unutar veceg
    assert triangles_overlap(outer, inner)

    # Provera mora raditi i obrnutim redosledom
    assert triangles_overlap(inner, outer)


def test_triangles_cross_without_contained_vertices():
    t1 = [
        (-5, -1),
        (5, -1),
        (0, 5),
    ]

    t2 = [
        (-5, 3),
        (5, 3),
        (0, -3),
    ]

    # Unutrasnjosti se preklapaju,
    # a ivice se pravilno ukrstaju.
    assert triangles_overlap(t1, t2)
    assert triangles_overlap(t2, t1)

def test_triangles_overlap_reversed_winding():
    t1 = [
        (0, 0),
        (10, 0),
        (0, 10),
    ]

    t2 = [
        (2, 2),
        (8, 2),
        (2, 8),
    ]

    # Normalan redosled temena
    assert triangles_overlap(t1, t2)

    # Obrnut redosled temena
    assert triangles_overlap(t1[::-1], t2)
    assert triangles_overlap(t1, t2[::-1])
    assert triangles_overlap(t1[::-1], t2[::-1])

    # Obrnut redosled argumenata
    assert triangles_overlap(t2, t1)

def test_triangles_shared_edge_reversed_winding():
    t1 = [
        (0, 0),
        (10, 0),
        (10, 10),
    ]

    t2 = [
        (0, 0),
        (10, 10),
        (0, 10),
    ]

    # Trouglovi dele ivicu, ali se ne preklapaju.
    assert not triangles_overlap(t1, t2)

    # Obrnuta orijentacija oba trougla.
    assert not triangles_overlap(t1[::-1], t2[::-1])

    # Obrnuta orijentacija samo jednog trougla.
    assert not triangles_overlap(t1[::-1], t2)
    assert not triangles_overlap(t1, t2[::-1])


def test_triangles_overlap_rotated_vertices():
    t1 = [
        (0, 0),
        (10, 0),
        (0, 10),
    ]

    # Isti trougao, ali drugo pocetno teme
    t2 = [
        (10, 0),
        (0, 10),
        (0, 0),
    ]

    assert triangles_overlap(t1, t2)
    assert triangles_overlap(t2, t1)

    # Isti trougao, obrnuta orijentacija
    assert triangles_overlap(t1, t2[::-1])


def test_validate_concave_triangulation():
    # Konkavan poligon u obliku slova L
    poly = [
        (0, 0),
        (10, 0),
        (10, 4),
        (4, 4),
        (4, 10),
        (0, 10),
    ]

    triangles = triangulate_polygon(poly)

    assert len(triangles) == len(poly) - 2
    assert validate_triangulation(poly, triangles)


def test_validate_concave_triangulation_clockwise():
    poly = [
        (0, 10),
        (4, 10),
        (4, 4),
        (10, 4),
        (10, 0),
        (0, 0),
    ]

    # Poligon ima CW orijentaciju
    assert signed_polygon_area(poly) < 0

    # Normalizacija u CCW pre triangulacije
    poly.reverse()

    assert signed_polygon_area(poly) > 0

    triangles = triangulate_polygon(poly)

    assert len(triangles) == len(poly) - 2
    assert validate_triangulation(poly, triangles)


from hairpin_geometry import normalize_polygon_ccw


def test_normalize_polygon_ccw():
    ccw = [
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    ]

    cw = list(reversed(ccw))
    original_cw = cw.copy()

    # CW poligon postaje CCW
    normalized = normalize_polygon_ccw(cw)

    assert signed_polygon_area(normalized) > 0
    assert normalized == ccw

    # Originalni poligon ostaje nepromenjen
    assert cw == original_cw

    # Vec ispravan CCW poligon ostaje isti
    assert normalize_polygon_ccw(ccw) == ccw

    # Rezultat je nova lista
    assert normalize_polygon_ccw(ccw) is not ccw


from hairpin_builder import build_validated_polygon


def test_build_validated_polygon():
    # Kvadrat sa CW orijentacijom
    points = [
        (0, 0),
        (0, 10),
        (10, 10),
        (10, 0),
    ]

    original = points.copy()

    poly, triangles = build_validated_polygon(points)

    # Izlazni poligon mora biti CCW
    assert signed_polygon_area(poly) > 0

    # Kvadrat mora imati dva trougla
    assert len(triangles) == 2

    # Triangulacija mora biti ispravna
    assert validate_triangulation(poly, triangles)

    # Ulazne koordinate ostaju nepromenjene
    assert points == original


def test_build_validated_concave_polygon():
    # Konkavni poligon u obliku slova L
    points = [
        (0, 0),
        (10, 0),
        (10, 4),
        (4, 4),
        (4, 10),
        (0, 10),
    ]

    original = points.copy()

    poly, triangles = build_validated_polygon(points)

    # Orijentacija mora biti CCW
    assert signed_polygon_area(poly) > 0

    # Sest temena daju cetiri trougla
    assert len(triangles) == 4

    # Kompletna geometrijska validacija
    assert validate_triangulation(poly, triangles)

    # Originalne koordinate ostaju netaknute
    assert points == original


from stelvio_hairpins import STELVIO_HAIRPINS


def test_stelvio_hairpin_registry():
    expected = [
        (187, 188, "LEFT"),
        (216, 217, "LEFT"),
        (246, 247, "RIGHT"),
        (252, 253, "RIGHT"),
        (411, 412, "LEFT"),
        (423, 424, "RIGHT"),
        (489, 490, "LEFT"),
        (503, 504, "RIGHT"),
    ]

    assert STELVIO_HAIRPINS == expected
    assert len(STELVIO_HAIRPINS) == 8

    # Svaki par mora imati uzastopne indekse
    assert all(
        j == i + 1
        for i, j, direction in STELVIO_HAIRPINS
    )

    # Indeksi pripadaju ociscenoj trasi od 522 tacke
    assert all(
        0 <= i < j < 522
        for i, j, direction in STELVIO_HAIRPINS
    )



