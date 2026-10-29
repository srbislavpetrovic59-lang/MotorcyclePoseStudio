
@'
import math
import xml.etree.ElementTree as ET
from hairpin_geometry import polygon_self_intersects
from hairpin_builder import build_validated_polygon
from hairpin_geometry import segments_properly_cross
from gpx_cleaner import remove_immediate_backtracks
from gpx_projection import project_route_to_meters
from stelvio_hairpins import STELVIO_HAIRPINS
from hairpin_geometry import inner_intersection, line_intersection
from hairpin_geometry import triangles_overlap


path = r"C:\Vezbe\MotorcyclePoseSim\stelvio_terrain\data\salita-al-passo-dello-stelvio-da-prato.gpx"

root = ET.parse(path).getroot()
ns = {"g": "http://www.topografix.com/GPX/1/1"}

points = [
    (float(p.get("lon")), float(p.get("lat")))
    for p in root.findall(".//g:trkpt", ns)
]
def segment_angle(a, b):
    return math.degrees(math.atan2(
        b[1] - a[1],
        b[0] - a[0]
    ))


def angle_change(a1, a2):
    return (a2 - a1 + 180) % 360 - 180
xy = project_route_to_meters(
    remove_immediate_backtracks(points)
)
angles = []
from hairpin_geometry import distance_to_segment

a = xy[186]
b = xy[187]

c = xy[188]
d = xy[189]

distances = [
    distance_to_segment(a, c, d),
    distance_to_segment(b, c, d),
    distance_to_segment(c, a, b),
    distance_to_segment(d, a, b),
]

print(
    f"Razmak krakova P185-P186 / P189-P190: "
    f"{min(distances):.2f} m"
)

pairs = [
    ("P186-P188", xy[186], xy[188]),
    ("P187-P188", xy[187], xy[188]),
    ("P187-P189", xy[187], xy[189]),
]

for name, a, b in pairs:
    print(f"{name}: {math.dist(a, b):.2f} m")

from hairpin_geometry import projection_t

a = xy[186]
b = xy[187]

c = xy[188]
d = xy[189]

t1 = projection_t(b, c, d)
t2 = projection_t(c, a, b)

print(f"P187 na izlaznom segmentu: t={t1:.3f}")
print(f"P188 na ulaznom segmentu: t={t2:.3f}")
xy = project_route_to_meters(
    remove_immediate_backtracks(points)
)

for i, j, direction in STELVIO_HAIRPINS:
    g = {
        "points": [xy[i-1], xy[i], xy[j], xy[j+1]],
        "direction": direction,
    }

    center = inner_intersection(g)
    if i == 187 and center is not None:
        print("P187 udaljenost od centra:",
              f"{math.dist(xy[187], center):.2f} m")

        print("P188 udaljenost od centra:",
              f"{math.dist(xy[188], center):.2f} m")
        a1 = math.atan2(
        xy[187][1] - center[1],
        xy[187][0] - center[0]
        )

        a2 = math.atan2(
            xy[188][1] - center[1],
            xy[188][0] - center[0]
        )

        sweep = (math.degrees(a2 - a1) + 180) % 360 - 180

        print(f"P187-P188 ugao oko centra: {sweep:+.2f}")
        radius = (
            math.dist(xy[187], center)
            + math.dist(xy[188], center)
        ) / 2

        arc_length = radius * math.radians(abs(sweep))
        chord_length = math.dist(xy[187], xy[188])

        print(f"Prosecan poluprecnik: {radius:.3f} m")
        print(f"Duzina kruznog luka: {arc_length:.3f} m")
        print(f"GPX segment: {chord_length:.3f} m")
        tangent_start = math.degrees(a1) + 90
        tangent_end = math.degrees(a2) + 90

        entry_angle = segment_angle(xy[186], xy[187])
        exit_angle = segment_angle(xy[188], xy[189])

        print(
            "Odstupanje ulazne tangente:",
            f"{angle_change(entry_angle, tangent_start):+.2f}"
        )

        print(
            "Odstupanje izlazne tangente:",
            f"{angle_change(tangent_end, exit_angle):+.2f}"
        )
        def cross_side(a, b, p):
            return (
                (b[0] - a[0]) * (p[1] - a[1])
                - (b[1] - a[1]) * (p[0] - a[0])
            )

        print(
            "Centar prema ulaznom kraku:",
            f"{cross_side(xy[186], xy[187], center):+.3f}"
        )

        print(
            "Centar prema izlaznom kraku:",
            f"{cross_side(xy[188], xy[189], center):+.3f}"
        )
        def foot_on_line(p, a, b):
            t = projection_t(p, a, b)
            return (
                a[0] + t * (b[0] - a[0]),
                a[1] + t * (b[1] - a[1])
            )

        tangent_in = foot_on_line(
            center, xy[186], xy[187]
        )

        tangent_out = foot_on_line(
            center, xy[188], xy[189]
        )

        print(
            "Ulazna tacka tangencije, t:",
            f"{projection_t(center, xy[186], xy[187]):.3f}"
        )

        print(
            "Izlazna tacka tangencije, t:",
            f"{projection_t(center, xy[188], xy[189]):.3f}"
        )
        angle_in = math.atan2(
            tangent_in[1] - center[1],
            tangent_in[0] - center[0]
        )

        angle_out = math.atan2(
            tangent_out[1] - center[1],
            tangent_out[0] - center[0]
        )

        sweep_left = (
            math.degrees(angle_out - angle_in) % 360
        )

        print(f"Ugao tangencijalnog LEFT luka: {sweep_left:.2f}")
        tangent_angle_in = math.degrees(angle_in) + 90
        tangent_angle_out = math.degrees(angle_out) + 90

        road_angle_in = segment_angle(xy[186], xy[187])
        road_angle_out = segment_angle(xy[188], xy[189])

        print(
            "Ulaz, razlika smerova:",
            f"{angle_change(road_angle_in, tangent_angle_in):+.2f}"
        )

        print(
            "Izlaz, razlika smerova:",
            f"{angle_change(tangent_angle_out, road_angle_out):+.2f}"
        )
        from hairpin_geometry import make_outer_arc

        arc = make_outer_arc(
            center,
            tangent_in,
            tangent_out,
            side=1,
            radius=3.0
        )

        print(f"Broj tacaka luka: {len(arc)}")
        print(f"Pocetak luka - greska: {math.dist(arc[0], tangent_in):.6f} m")
        print(f"Kraj luka - greska: {math.dist(arc[-1], tangent_out):.6f} m")
        def min_distance_to_arc(point, arc):
            return min(
                distance_to_segment(point, arc[k], arc[k + 1])
                for k in range(len(arc) - 1)
            )

        print(
            "P187 do luka:",
            f"{min_distance_to_arc(xy[187], arc):.3f} m"
        )

        print(
            "P188 do luka:",
            f"{min_distance_to_arc(xy[188], arc):.3f} m"
        )
        for idx in (187, 188):
            radial_distance = math.dist(xy[idx], center)
            difference = radial_distance - 3.0

            print(
                f"P{idx}: odstupanje od kruznice = "
                f"{difference:+.3f} m"
            )
        midpoint = (
            (xy[187][0] + xy[188][0]) / 2,
            (xy[187][1] + xy[188][1]) / 2
        )

        print(
            "Centar do sredine GPX segmenta:",
            f"{math.dist(center, midpoint):.3f} m"
        )

        print(
            "Centar do GPX segmenta:",
            f"{distance_to_segment(center, xy[187], xy[188]):.3f} m"
        )
        print(
            "Sredina GPX segmenta do luka:",
            f"{min_distance_to_arc(midpoint, arc):.3f} m"
        )
        arc_midpoint = arc[len(arc) // 2]

        cross = (
            (xy[188][0] - xy[187][0])
            * (arc_midpoint[1] - xy[187][1])
            -
            (xy[188][1] - xy[187][1])
            * (arc_midpoint[0] - xy[187][0])
        )

        print(f"Polozaj sredine luka: {cross:+.3f}")
        print(
            "Centar prema P187-P188:",
            f"{cross_side(xy[187], xy[188], center):+.3f}"
        )
        road_width = 6.0
        half_width = road_width / 2

        centerline_radius = 3.0
        inner_radius = centerline_radius - half_width
        outer_radius = centerline_radius + half_width

        print(f"Unutrasnji poluprecnik: {inner_radius:.3f} m")
        print(f"Spoljasnji poluprecnik: {outer_radius:.3f} m")
        segments = [
            (186, 187),
            (187, 188),
            (188, 189),
        ]

        for a, b in segments:
            distance = distance_to_segment(
                center, xy[a], xy[b]
            )
            print(
                f"Centar do P{a}-P{b}: "
                f"{distance:.3f} m"
            )
        penetration = 3.0 - distance_to_segment(
            center,
            xy[187],
            xy[188]
        )
        print(
            f"Ulazak GPX segmenta u kruznicu: "
            f"{penetration:.3f} m"
        )
        print(
            "Razmak tacaka tangencije:",
            f"{math.dist(tangent_in, tangent_out):.3f} m"
        )
        print(
            "Ulazna tangencija do P187:",
            f"{math.dist(tangent_in, xy[187]):.3f} m"
        )

        print(
            "Izlazna tangencija do P188:",
            f"{math.dist(tangent_out, xy[188]):.3f} m"
        )
        new_radius = 6.0
        old_radius = 3.0

        angle_rad = math.radians(124.58)

        old_tangent_distance = old_radius * math.tan(angle_rad / 2)
        new_tangent_distance = new_radius * math.tan(angle_rad / 2)

        print(f"Stara tangentna duzina: {old_tangent_distance:.3f} m")
        print(f"Nova tangentna duzina: {new_tangent_distance:.3f} m")
        print(f"Potrebno pomeranje: {new_tangent_distance - old_tangent_distance:.3f} m")
        center6 = inner_intersection(g, distance=6.0)

        if center6 is not None:
            t_in6 = projection_t(
                center6, xy[186], xy[187]
            )

            t_out6 = projection_t(
                center6, xy[188], xy[189]
            )

            print(f"R=6 m, ulazna tangencija: t={t_in6:.3f}")
            print(f"R=6 m, izlazna tangencija: t={t_out6:.3f}")
        if center6 is not None:
            tangent_in6 = foot_on_line(
                center6, xy[186], xy[187]
            )

            tangent_out6 = foot_on_line(
                center6, xy[188], xy[189]
            )

            arc6 = make_outer_arc(
                center6,
                tangent_in6,
                tangent_out6,
                side=1,
                radius=6.0
            )
            print(
                "R=3, sredina GPX do luka:",
                f"{min_distance_to_arc(midpoint, arc):.3f} m"
            )

            print(
                "R=6, sredina GPX do luka:",
                f"{min_distance_to_arc(midpoint, arc6):.3f} m"
            )
            print(
                "R=6, P187 do luka:",
                f"{min_distance_to_arc(xy[187], arc6):.3f} m"
            )

            print(
                "R=6, P188 do luka:",
                f"{min_distance_to_arc(xy[188], arc6):.3f} m"
            )
        center45 = inner_intersection(g, distance=4.5)

        if center45 is not None:
            tin45 = foot_on_line(
                center45, xy[186], xy[187]
            )

            tout45 = foot_on_line(
                center45, xy[188], xy[189]
            )

            arc45 = make_outer_arc(
                center45, tin45, tout45,
                side=1, radius=4.5
            )

            for name, point in [
                ("P187", xy[187]),
                ("Sredina", midpoint),
                ("P188", xy[188])
            ]:
                print(
                    f"R=4.5, {name}: "
                    f"{min_distance_to_arc(point, arc45):.3f} m"
                )    
        road_half_width = 3.0

        for radius in (3.0, 4.5, 6.0):
            inner_radius = radius - road_half_width
            outer_radius = radius + road_half_width

            print(
                f"R={radius:.1f} m: "
                f"unutrasnja={inner_radius:.1f} m, "
                f"spoljasnja={outer_radius:.1f} m"
            )
        if center45 is not None:
            t_in45 = projection_t(
                center45, xy[186], xy[187]
            )

            t_out45 = projection_t(
                center45, xy[188], xy[189]
            )

            print(f"R=4.5, ulazna tangencija: t={t_in45:.3f}")
            print(f"R=4.5, izlazna tangencija: t={t_out45:.3f}")
        radial_errors = [
            abs(math.dist(p, center45) - 4.5)
            for p in arc45
        ]

        print(
            f"R=4.5, broj tacaka: {len(arc45)}"
        )

        print(
            f"R=4.5, maksimalna radijalna greska: "
            f"{max(radial_errors):.9f} m"
        )
        inner45 = []
        outer45 = []

        for p in arc45:
            dx = p[0] - center45[0]
            dy = p[1] - center45[1]

            inner45.append((
                center45[0] + dx / 4.5 * 1.5,
                center45[1] + dy / 4.5 * 1.5
            ))

            outer45.append((
                center45[0] + dx / 4.5 * 7.5,
                center45[1] + dy / 4.5 * 7.5
            ))

        widths = [
            math.dist(a, b)
            for a, b in zip(inner45, outer45)
        ]

        print(f"Minimalna sirina: {min(widths):.6f} m")
        print(f"Maksimalna sirina: {max(widths):.6f} m")
        road_polygon45 = outer45 + list(reversed(inner45))

        print(
            f"Broj tacaka poligona: {len(road_polygon45)}"
        )

        print(
            "Samopresecanje:",
            polygon_self_intersects(road_polygon45)
        )
        from hairpin_geometry import signed_polygon_area

        theoretical_area = (
            math.radians(124.58) / 2
            * (7.5**2 - 1.5**2)
        )

        polygon_area = abs(
            signed_polygon_area(road_polygon45)
        )

        print(f"Teorijska povrsina: {theoretical_area:.3f} m2")
        print(f"Povrsina poligona: {polygon_area:.3f} m2")
        print(f"Razlika: {theoretical_area - polygon_area:.3f} m2")
        poly45, triangles45 = build_validated_polygon(
            road_polygon45
        )

        print(f"Broj temena: {len(poly45)}")
        print(f"Broj trouglova: {len(triangles45)}")
        print("Triangulacija: VALIDNA")
        triangle_areas = [
            signed_polygon_area([
                poly45[a],
                poly45[b],
                poly45[c]
            ])
            for a, b, c in triangles45
        ]

        print(
            "Najmanja potpisana povrsina trougla:",
            f"{min(triangle_areas):.6f} m2"
        )

        print(
            "Najveca potpisana povrsina trougla:",
            f"{max(triangle_areas):.6f} m2"
        )
        total_triangle_area = sum(triangle_areas)
        polygon_area45 = abs(signed_polygon_area(poly45))

        print(f"Zbir povrsina trouglova: {total_triangle_area:.6f} m2")
        print(f"Povrsina poligona: {polygon_area45:.6f} m2")
        print(
            f"Razlika: "
            f"{abs(total_triangle_area - polygon_area45):.9f} m2"
        )
        print(
            "Sirina ulaznog spoja:",
            f"{math.dist(inner45[0], outer45[0]):.6f} m"
        )

        print(
            "Sirina izlaznog spoja:",
            f"{math.dist(inner45[-1], outer45[-1]):.6f} m"
        )
        tangent_in45 = foot_on_line(
            center45,
            xy[186],
            xy[187]
        )
        mid_in = (
            (inner45[0][0] + outer45[0][0]) / 2,
            (inner45[0][1] + outer45[0][1]) / 2
        )

        print(
            "Osa do sredine ulaznog spoja:",
            f"{math.dist(tangent_in45, mid_in):.9f} m"
        )
        tangent_out45 = foot_on_line(
            center45,
            xy[188],
            xy[189]
        )

        mid_out = (
            (inner45[-1][0] + outer45[-1][0]) / 2,
            (inner45[-1][1] + outer45[-1][1]) / 2
        )

        print(
            "Osa do sredine izlaznog spoja:",
            f"{math.dist(tangent_out45, mid_out):.9f} m"
        )
        road_dx = xy[187][0] - xy[186][0]
        road_dy = xy[187][1] - xy[186][1]

        width_dx = outer45[0][0] - inner45[0][0]
        width_dy = outer45[0][1] - inner45[0][1]

        dot = road_dx * width_dx + road_dy * width_dy

        print(
            "Ulazni spoj - skalarni proizvod:",
            f"{dot:.9f}"
        )
        road_dx = xy[189][0] - xy[188][0]
        road_dy = xy[189][1] - xy[188][1]

        width_dx = outer45[-1][0] - inner45[-1][0]
        width_dy = outer45[-1][1] - inner45[-1][1]

        dot_out = road_dx * width_dx + road_dy * width_dy

        print(
            "Izlazni spoj - skalarni proizvod:",
            f"{dot_out:.9f}"
        )
        dx = xy[187][0] - xy[186][0]
        dy = xy[187][1] - xy[186][1]

        length = math.hypot(dx, dy)

        straight_inner_in = (
            tangent_in45[0] - 3.0 * dy / length,
            tangent_in45[1] + 3.0 * dx / length
        )

        gap_inner_in = math.dist(
            straight_inner_in,
            inner45[0]
        )

        print(
            "Ulaz - spoj unutrasnje ivice:",
            f"{gap_inner_in:.9f} m"
        )
        straight_outer_in = (
            tangent_in45[0] + 3.0 * dy / length,
            tangent_in45[1] - 3.0 * dx / length
        )

        gap_outer_in = math.dist(
            straight_outer_in,
            outer45[0]
        )

        print(
            "Ulaz - spoj spoljasnje ivice:",
            f"{gap_outer_in:.9f} m"
        )
        dx_out = xy[189][0] - xy[188][0]
        dy_out = xy[189][1] - xy[188][1]

        length_out = math.hypot(dx_out, dy_out)

        straight_inner_out = (
            tangent_out45[0] - 3.0 * dy_out / length_out,
            tangent_out45[1] + 3.0 * dx_out / length_out
        )

        gap_inner_out = math.dist(
            straight_inner_out,
            inner45[-1]
        )

        print(
            "Izlaz - spoj unutrasnje ivice:",
            f"{gap_inner_out:.9f} m"
        )
        straight_outer_out = (
            tangent_out45[0] + 3.0 * dy_out / length_out,
            tangent_out45[1] - 3.0 * dx_out / length_out
        )

        gap_outer_out = math.dist(
            straight_outer_out,
            outer45[-1]
        )

        print(
            "Izlaz - spoj spoljasnje ivice:",
            f"{gap_outer_out:.9f} m"
        )
        straight_angle = math.atan2(
            xy[187][1] - xy[186][1],
            xy[187][0] - xy[186][0]
        )

        arc_angle = math.atan2(
            inner45[1][1] - inner45[0][1],
            inner45[1][0] - inner45[0][0]
        )

        angle_diff = math.degrees(
            math.atan2(
                math.sin(arc_angle - straight_angle),
                math.cos(arc_angle - straight_angle)
            )
        )

        print(
            "Ulaz - ugao prelaza unutrasnje ivice:",
            f"{angle_diff:.6f} stepeni"
        )
        outer_arc_angle = math.atan2(
            outer45[1][1] - outer45[0][1],
            outer45[1][0] - outer45[0][0]
        )

        outer_angle_diff = math.degrees(
            math.atan2(
                math.sin(outer_arc_angle - straight_angle),
                math.cos(outer_arc_angle - straight_angle)
            )
        )

        print(
            "Ulaz - ugao prelaza spoljasnje ivice:",
            f"{outer_angle_diff:.6f} stepeni"
        )
        exit_straight_angle = math.atan2(
            xy[189][1] - xy[188][1],
            xy[189][0] - xy[188][0]
        )

        exit_arc_angle = math.atan2(
            inner45[-1][1] - inner45[-2][1],
            inner45[-1][0] - inner45[-2][0]
        )

        exit_angle_diff = math.degrees(
            math.atan2(
                math.sin(exit_straight_angle - exit_arc_angle),
                math.cos(exit_straight_angle - exit_arc_angle)
            )
        )

        print(
            "Izlaz - ugao prelaza unutrasnje ivice:",
            f"{exit_angle_diff:.6f} stepeni"
        )
        exit_outer_arc_angle = math.atan2(
            outer45[-1][1] - outer45[-2][1],
            outer45[-1][0] - outer45[-2][0]
        )

        exit_outer_angle_diff = math.degrees(
            math.atan2(
                math.sin(exit_straight_angle - exit_outer_arc_angle),
                math.cos(exit_straight_angle - exit_outer_arc_angle)
            )
        )

        print(
            "Izlaz - ugao prelaza spoljasnje ivice:",
            f"{exit_outer_angle_diff:.6f} stepeni"
        )
        approach_length = math.dist(
            xy[186],
            tangent_in45
        )

        print(
            "Duzina pravolinijskog prilaza:",
            f"{approach_length:.6f} m"
        )

        print(
            "Duzina segmenta P186-P187:",
            f"{math.dist(xy[186], xy[187]):.6f} m"
        )
        exit_length = math.dist(
            tangent_out45,
            xy[189]
        )

        full_exit_length = math.dist(
            xy[188],
            xy[189]
        )

        print(
            "Duzina pravolinijskog izlaza:",
            f"{exit_length:.6f} m"
        )

        print(
            "Duzina segmenta P188-P189:",
            f"{full_exit_length:.6f} m"
        )

        print(
            "Preostalo od P188 do tangencije:",
            f"{full_exit_length - exit_length:.6f} m"
        )
        t_entry = projection_t(
            tangent_in45,
            xy[186],
            xy[187]
        )

        t_exit = projection_t(
            tangent_out45,
            xy[188],
            xy[189]
        )

        print(f"Ulaz - parametar tangencije: {t_entry:.6f}")
        print(f"Izlaz - parametar tangencije: {t_exit:.6f}")

        print(
            "Obe tangencije unutar segmenata:",
            0.0 <= t_entry <= 1.0
            and 0.0 <= t_exit <= 1.0
        )
        straight_inner_start = (
            xy[186][0] - 3.0 * dy / length,
            xy[186][1] + 3.0 * dx / length
        )

        straight_outer_start = (
            xy[186][0] + 3.0 * dy / length,
            xy[186][1] - 3.0 * dx / length
        )

        approach_polygon = [
            straight_inner_start,
            straight_inner_in,
            straight_outer_in,
            straight_outer_start
        ]

        print(
            "Prilaz - samopresecanje:",
            polygon_self_intersects(approach_polygon)
        )

        print(
            "Prilaz - povrsina:",
            f"{abs(signed_polygon_area(approach_polygon)):.6f} m2"
        )
        straight_inner_end = (
            xy[189][0] - 3.0 * dy_out / length_out,
            xy[189][1] + 3.0 * dx_out / length_out
        )

        straight_outer_end = (
            xy[189][0] + 3.0 * dy_out / length_out,
            xy[189][1] - 3.0 * dx_out / length_out
        )

        exit_polygon = [
            straight_inner_out,
            straight_inner_end,
            straight_outer_end,
            straight_outer_out
        ]

        print(
            "Izlaz - samopresecanje:",
            polygon_self_intersects(exit_polygon)
        )

        print(
            "Izlaz - povrsina:",
            f"{abs(signed_polygon_area(exit_polygon)):.6f} m2"
        )
        crossings = 0

        for a in range(len(approach_polygon)):
            p1 = approach_polygon[a]
            p2 = approach_polygon[(a + 1) % len(approach_polygon)]

            for b in range(len(road_polygon45)):
                q1 = road_polygon45[b]
                q2 = road_polygon45[(b + 1) % len(road_polygon45)]

                if segments_properly_cross(p1, p2, q1, q2):
                    crossings += 1

        print(
            "Prilaz i kruzni deo - nepravilna ukrstanja:",
            crossings
        )
        approach_triangles = [
            [approach_polygon[0], approach_polygon[1], approach_polygon[2]],
            [approach_polygon[0], approach_polygon[2], approach_polygon[3]]
        ]

        overlap_count = 0

        for approach_tri in approach_triangles:
            for tri in triangles45:
                arc_tri = [poly45[k] for k in tri]

                if triangles_overlap(approach_tri, arc_tri):
                    overlap_count += 1

        print(
            "Prilaz i kruzni deo - preklapanja trouglova:",
            overlap_count
        )
        exit_triangles = [
            [exit_polygon[0], exit_polygon[1], exit_polygon[2]],
            [exit_polygon[0], exit_polygon[2], exit_polygon[3]]
        ]

        exit_overlap_count = 0

        for exit_tri in exit_triangles:
            for tri in triangles45:
                arc_tri = [poly45[k] for k in tri]

                if triangles_overlap(exit_tri, arc_tri):
                    exit_overlap_count += 1

        print(
            "Izlaz i kruzni deo - preklapanja trouglova:",
            exit_overlap_count
        )
        full_road_polygon = (
            [straight_inner_start]
            + inner45
            + [straight_inner_end, straight_outer_end]
            + list(reversed(outer45))
            + [straight_outer_start]
        )

        print(
            "Ukupan broj temena:",
            len(full_road_polygon)
        )

        print(
            "Kompletan kolovoz - samopresecanje:",
            polygon_self_intersects(full_road_polygon)
        )

        print(
            "Kompletan kolovoz - povrsina:",
            f"{abs(signed_polygon_area(full_road_polygon)):.6f} m2"
        )
        try:
            full_poly, full_triangles = build_validated_polygon(
                full_road_polygon
            )

            print("Kompletan kolovoz - triangulacija: VALIDNA")
            print("Broj temena:", len(full_poly))
            print("Broj trouglova:", len(full_triangles))

        except ValueError as e:
            print("Kompletan kolovoz - triangulacija: NEVALIDNA")
            print("Razlog:", e)
        full_triangle_area = sum(
            abs(signed_polygon_area([
                full_poly[a],
                full_poly[b],
                full_poly[c]
            ]))
            for a, b, c in full_triangles
        )

        full_polygon_area = abs(
            signed_polygon_area(full_poly)
        )

        print(
            "Povrsina 54 trougla:",
            f"{full_triangle_area:.6f} m2"
        )

        print(
            "Povrsina kompletnog poligona:",
            f"{full_polygon_area:.6f} m2"
        )

        print(
            "Razlika povrsina:",
            f"{abs(full_triangle_area - full_polygon_area):.9f} m2"
        )













for n in range(185, 190):
    a = xy[n]
    b = xy[n + 1]

    angle = math.degrees(math.atan2(
        b[1] - a[1],
        b[0] - a[0]
    ))

    angles.append(angle)

total_turn = 0.0

for a1, a2 in zip(angles, angles[1:]):
    delta = (a2 - a1 + 180) % 360 - 180
    total_turn += delta
print("\nUKUPNO SKRETANJE SERPENTINA")

for i, j, direction in STELVIO_HAIRPINS:
    angles = []

    for n in range(i - 2, j + 2):
        a = xy[n]
        b = xy[n + 1]

        angle = math.degrees(math.atan2(
            b[1] - a[1],
            b[0] - a[0]
        ))

        angles.append(angle)

    total_turn = 0.0

    for a1, a2 in zip(angles, angles[1:]):
        delta = (a2 - a1 + 180) % 360 - 180
        total_turn += delta

    print(
        f"P{i}-P{j}: {direction}, "
        f"ukupno={total_turn:+.2f}"
    )
print("\nCENTRI SERPENTINA - R = 4.5 m")

for i, j, direction in STELVIO_HAIRPINS:
    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=4.5
    )

    print(
        f"P{i}-{j} ({direction}):",
        "OK" if center is not None else "NEMA CENTRA"
    )
print("\nTANGENCIJE SERPENTINA - R = 4.5 m")

for i, j, direction in STELVIO_HAIRPINS:
    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=4.5
    )

    if center is None:
        print(f"P{i}-{j}: NEMA CENTRA")
        continue

    t_in = projection_t(
        center,
        xy[i - 1],
        xy[i]
    )

    t_out = projection_t(
        center,
        xy[j],
        xy[j + 1]
    )

    valid = (
        0.0 <= t_in <= 1.0
        and 0.0 <= t_out <= 1.0
    )

    print(
        f"P{i}-{j}: "
        f"ulaz={t_in:.3f}, "
        f"izlaz={t_out:.3f}, "
        f"{'OK' if valid else 'PROBLEM'}"
    )
    print("\nPROBLEMATICNE SERPENTINE - R = 3.0 m")

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=3.0
    )

    if center is None:
        print(f"P{i}-{j}: NEMA CENTRA")
        continue

    t_in = projection_t(
        center,
        xy[i - 1],
        xy[i]
    )

    t_out = projection_t(
        center,
        xy[j],
        xy[j + 1]
    )

    print(
        f"P{i}-{j}: "
        f"ulaz={t_in:.3f}, "
        f"izlaz={t_out:.3f}"
    )
print("\nISPITIVANJE POLUPRECNIKA")

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    print(f"\nSerpentina P{i}-{j}")

    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    for radius in (3.1, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5):
        center = inner_intersection(
            geometry,
            distance=radius
        )

        if center is None:
            print(f"R={radius:.2f}: NEMA CENTRA")
            continue

        t_in = projection_t(
            center, xy[i - 1], xy[i]
        )

        t_out = projection_t(
            center, xy[j], xy[j + 1]
        )

        valid = (
            0 <= t_in <= 1
            and 0 <= t_out <= 1
        )

        print(
            f"R={radius:.2f}: "
            f"ulaz={t_in:.3f}, "
            f"izlaz={t_out:.3f}, "
            f"{'OK' if valid else 'PROBLEM'}"
        )
print("\nGRANICNI POLUPRECNICI")

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    low = 3.5
    high = 3.75

    for _ in range(40):
        radius = (low + high) / 2

        center = inner_intersection(
            geometry,
            distance=radius
        )

        t_in = projection_t(
            center,
            xy[i - 1],
            xy[i]
        )

        if t_in >= 0:
            low = radius
        else:
            high = radius

    print(
        f"P{i}-{j}: "
        f"R_max={low:.6f} m, "
        f"R_unutrasnji={low - 3.0:.6f} m"
    )

print("\nP187-P188: lokalni uglovi")

for n in range(184, 191):
    a = xy[n]
    b = xy[n + 1]

    angle = math.degrees(math.atan2(
        b[1] - a[1],
        b[0] - a[0]
    ))

    print(f"P{n}-P{n+1}: {angle:.2f}")

distance = math.dist(xy[185], xy[190])

print(
    f"P185-P190: {distance:.2f} m"
)



entry = segment_angle(xy[186], xy[187])
middle = segment_angle(xy[187], xy[188])
exit_angle = segment_angle(xy[188], xy[189])

print(f"Ulaz -> sredina: {angle_change(entry, middle):+.2f}")
print(f"Sredina -> izlaz: {angle_change(middle, exit_angle):+.2f}")
print("\nNEDOSTAJUCA DUZINA PRILAZA - R = 4.5 m")

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=4.5
    )

    t_in = projection_t(
        center,
        xy[i - 1],
        xy[i]
    )

    segment_length = math.dist(
        xy[i - 1],
        xy[i]
    )

    missing_length = max(
        0.0,
        -t_in * segment_length
    )

    print(
        f"P{i}-{j}: "
        f"segment={segment_length:.3f} m, "
        f"nedostaje={missing_length:.3f} m"
    )
print("\nPROMENA PRAVCA PRE PRILAZA")

for i in (411, 489):
    a = xy[i - 2]
    b = xy[i - 1]
    c = xy[i]

    angle_previous = math.atan2(
        b[1] - a[1],
        b[0] - a[0]
    )

    angle_approach = math.atan2(
        c[1] - b[1],
        c[0] - b[0]
    )

    angle_diff = math.degrees(
        math.atan2(
            math.sin(angle_approach - angle_previous),
            math.cos(angle_approach - angle_previous)
        )
    )

    previous_length = math.dist(a, b)

    print(
        f"P{i}-{i+1}: "
        f"prethodni_segment={previous_length:.3f} m, "
        f"promena_pravca={angle_diff:+.3f} stepeni"
    )
print("\nODSTUPANJE TANGENCIJE OD GPX TRASE")

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=4.5
    )

    a = xy[i - 1]
    b = xy[i]

    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dx, dy)

    # Projekcija centra na beskonačni prilazni pravac
    t = projection_t(center, a, b)

    tangent = (
        a[0] + t * dx,
        a[1] + t * dy
    )

    previous_a = xy[i - 2]
    previous_b = xy[i - 1]

    deviation = distance_to_segment(
        tangent,
        previous_a,
        previous_b
    )

    print(
        f"P{i}-{j}: "
        f"odstupanje={deviation:.3f} m"
    )
print("\nPOLOZAJ TANGENCIJE PREMA PRETHODNOM SEGMENTU")

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=4.5
    )

    a = xy[i - 1]
    b = xy[i]

    t = projection_t(center, a, b)

    tangent = (
        a[0] + t * (b[0] - a[0]),
        a[1] + t * (b[1] - a[1])
    )

    t_previous = projection_t(
        tangent,
        xy[i - 2],
        xy[i - 1]
    )

    print(
        f"P{i}-{j}: "
        f"t_prethodni={t_previous:.6f}, "
        f"unutar={0 <= t_previous <= 1}"
    )
print("\nPOLOZAJ PROJEKCIJE TANGENCIJE")

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=4.5
    )

    a = xy[i - 1]
    b = xy[i]

    t = projection_t(center, a, b)

    tangent = (
        a[0] + t * (b[0] - a[0]),
        a[1] + t * (b[1] - a[1])
    )

    previous_a = xy[i - 2]
    previous_b = xy[i - 1]

    t_previous = projection_t(
        tangent,
        previous_a,
        previous_b
    )

    previous_length = math.dist(
        previous_a,
        previous_b
    )

    distance_before_end = (
        1.0 - t_previous
    ) * previous_length

    print(
        f"P{i}-{j}: "
        f"projekcija_pre_P{i-1}="
        f"{distance_before_end:.3f} m"
    )
print("\nPOTPISANO ODSTUPANJE TANGENCIJE")

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=4.5
    )

    a = xy[i - 1]
    b = xy[i]

    t = projection_t(center, a, b)

    tangent = (
        a[0] + t * (b[0] - a[0]),
        a[1] + t * (b[1] - a[1])
    )

    p = xy[i - 2]
    q = xy[i - 1]

    dx = q[0] - p[0]
    dy = q[1] - p[1]

    signed_offset = (
        dx * (tangent[1] - p[1])
        - dy * (tangent[0] - p[0])
    ) / math.hypot(dx, dy)

    print(
        f"P{i}-{j}: "
        f"odstupanje={signed_offset:+.3f} m, "
        f"strana={'LEVO' if signed_offset > 0 else 'DESNO'}"
    )
print("\nRASPOLOZIVA DUZINA PRE TANGENCIJE")

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    geometry = {
        "points": [
            xy[i - 1],
            xy[i],
            xy[j],
            xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=4.5
    )

    a = xy[i - 1]
    b = xy[i]

    t = projection_t(center, a, b)

    tangent = (
        a[0] + t * (b[0] - a[0]),
        a[1] + t * (b[1] - a[1])
    )

    previous_a = xy[i - 2]
    previous_b = xy[i - 1]

    t_previous = projection_t(
        tangent,
        previous_a,
        previous_b
    )

    previous_length = math.dist(
        previous_a,
        previous_b
    )

    available_length = t_previous * previous_length

    print(
        f"P{i}-{j}: "
        f"raspolozivo={available_length:.3f} m"
    )
print("\nPOCETAK PRELAZA - 20 m PRE TANGENCIJE")

transition_length = 20.0

for i, j, direction in STELVIO_HAIRPINS:
    if i not in (411, 489):
        continue

    geometry = {
        "points": [
            xy[i - 1], xy[i],
            xy[j], xy[j + 1]
        ],
        "direction": direction
    }

    center = inner_intersection(
        geometry,
        distance=4.5
    )

    a = xy[i - 1]
    b = xy[i]

    t = projection_t(center, a, b)

    tangent = (
        a[0] + t * (b[0] - a[0]),
        a[1] + t * (b[1] - a[1])
    )

    p = xy[i - 2]
    q = xy[i - 1]

    previous_length = math.dist(p, q)

    t_previous = projection_t(tangent, p, q)

    t_start = t_previous - transition_length / previous_length

    start_inside = 0.0 <= t_start <= 1.0

    print(
        f"P{i}-{j}: "
        f"t_start={t_start:.6f}, "
        f"unutar={start_inside}"
    )
print("\nUGAO IZMEDJU TANGENTI PRELAZA")

for i in (411, 489):
    p = xy[i - 2]
    q = xy[i - 1]
    r = xy[i]

    angle_start = math.atan2(
        q[1] - p[1],
        q[0] - p[0]
    )

    angle_end = math.atan2(
        r[1] - q[1],
        r[0] - q[0]
    )

    delta = math.degrees(
        math.atan2(
            math.sin(angle_end - angle_start),
            math.cos(angle_end - angle_start)
        )
    )

    print(
        f"P{i}-{i+1}: "
        f"promena_tangente={delta:+.6f} stepeni"
    )
i, j, direction = 411, 412, "LEFT"

geometry = {
    "points": [xy[i-1], xy[i], xy[j], xy[j+1]],
    "direction": direction
}

center = inner_intersection(geometry, distance=4.5)

a = xy[i-1]
b = xy[i]

t = projection_t(center, a, b)

P3 = (
    a[0] + t * (b[0] - a[0]),
    a[1] + t * (b[1] - a[1])
)

p = xy[i-2]
q = xy[i-1]

length = math.dist(p, q)
ux = (q[0] - p[0]) / length
uy = (q[1] - p[1]) / length

t_previous = projection_t(P3, p, q)

P0 = (
    p[0] + (t_previous * length - 20.0) * ux,
    p[1] + (t_previous * length - 20.0) * uy
)

end_length = math.dist(a, b)
vx = (b[0] - a[0]) / end_length
vy = (b[1] - a[1]) / end_length

# Probna duzina kontrolnih rucica
handle = math.dist(P0, P3) / 3.0

P1 = (
    P0[0] + handle * ux,
    P0[1] + handle * uy
)

P2 = (
    P3[0] - handle * vx,
    P3[1] - handle * vy
)

print("P411-412 - duzina tetive:", f"{math.dist(P0, P3):.6f} m")
print("P411-412 - duzina rucice:", f"{handle:.6f} m")
print("P411-412 - kontrolne tacke:", P0, P1, P2, P3)
# Prvi izvod Bezierove krive u P3
d1x = 3.0 * (P3[0] - P2[0])
d1y = 3.0 * (P3[1] - P2[1])

# Drugi izvod u P3
d2x = 6.0 * (P3[0] - 2.0 * P2[0] + P1[0])
d2y = 6.0 * (P3[1] - 2.0 * P2[1] + P1[1])

# Potpisana zakrivljenost
kappa_bezier = (
    (d1x * d2y - d1y * d2x)
    / (d1x * d1x + d1y * d1y) ** 1.5
)

kappa_circle = 1.0 / 4.5

print(
    "Bezier - zakrivljenost na izlazu:",
    f"{kappa_bezier:.6f} 1/m"
)

print(
    "Kruznica - zakrivljenost:",
    f"{kappa_circle:.6f} 1/m"
)

print(
    "Razlika zakrivljenosti:",
    f"{abs(kappa_bezier - kappa_circle):.6f} 1/m"
)
# Jedinicna normala na zavrsnu tangentu
nx = -vy
ny = vx

# Trenutni vektor P1 - P2
wx = P1[0] - P2[0]
wy = P1[1] - P2[1]

current_normal = wx * nx + wy * ny

# Potrebna normalna komponenta za kappa = 1/R
target_normal = (
    kappa_circle * 1.5 * handle * handle
)

correction = target_normal - current_normal

print(
    "Trenutna normalna komponenta:",
    f"{current_normal:.6f} m"
)

print(
    "Potrebna normalna komponenta:",
    f"{target_normal:.6f} m"
)

print(
    "Potrebna korekcija P1:",
    f"{correction:.6f} m"
)
# P0, P1, P3, vx, vy i kappa_circle vec postoje.

# Normalna komponenta vektora P1 - P3
normal_component = (
    (P1[0] - P3[0]) * (-vy)
    + (P1[1] - P3[1]) * vx
)

print(
    "Normalna komponenta P1-P3:",
    f"{normal_component:.6f} m"
)

if normal_component > 0:
    required_handle = math.sqrt(
        2.0 * normal_component
        / (3.0 * kappa_circle)
    )

    print(
        "Potrebna zavrsna rucica:",
        f"{required_handle:.6f} m"
    )
else:
    print(
        "Sa postojecim P1 nije moguce dobiti "
        "pozitivnu ciljnu zakrivljenost."
    )
P2_new = (
    P3[0] - required_handle * vx,
    P3[1] - required_handle * vy
)

# Prvi izvod na kraju nove Bezierove krive
d1x_new = 3.0 * (P3[0] - P2_new[0])
d1y_new = 3.0 * (P3[1] - P2_new[1])

# Drugi izvod na kraju
d2x_new = 6.0 * (
    P3[0] - 2.0 * P2_new[0] + P1[0]
)
d2y_new = 6.0 * (
    P3[1] - 2.0 * P2_new[1] + P1[1]
)

kappa_new = (
    (d1x_new * d2y_new - d1y_new * d2x_new)
    / (d1x_new**2 + d1y_new**2)**1.5
)

print(
    "Nova zakrivljenost Bezier:",
    f"{kappa_new:.9f} 1/m"
)

print(
    "Zakrivljenost kruznice:",
    f"{kappa_circle:.9f} 1/m"
)

print(
    "Razlika:",
    f"{abs(kappa_new - kappa_circle):.9f} 1/m"
)
print("\nZAKRIVLJENOST DUZ BEZIEROVE KRIVE")

for step in range(11):
    t = step / 10.0
    u = 1.0 - t

    # Prvi izvod
    dx = 3 * (
        u*u * (P1[0] - P0[0])
        + 2*u*t * (P2_new[0] - P1[0])
        + t*t * (P3[0] - P2_new[0])
    )

    dy = 3 * (
        u*u * (P1[1] - P0[1])
        + 2*u*t * (P2_new[1] - P1[1])
        + t*t * (P3[1] - P2_new[1])
    )

    # Drugi izvod
    ddx = 6 * (
        u * (P2_new[0] - 2*P1[0] + P0[0])
        + t * (P3[0] - 2*P2_new[0] + P1[0])
    )

    ddy = 6 * (
        u * (P2_new[1] - 2*P1[1] + P0[1])
        + t * (P3[1] - 2*P2_new[1] + P1[1])
    )

    speed = math.hypot(dx, dy)

    kappa = (
        (dx * ddy - dy * ddx) / speed**3
        if speed > 1e-12 else float("nan")
    )

    print(f"t={t:.1f}  kappa={kappa:+.6f} 1/m")
def bezier_point(t):
    u = 1.0 - t
    return (
        u**3 * P0[0]
        + 3*u*u*t * P1[0]
        + 3*u*t*t * P2_new[0]
        + t**3 * P3[0],

        u**3 * P0[1]
        + 3*u*u*t * P1[1]
        + 3*u*t*t * P2_new[1]
        + t**3 * P3[1]
    )


length_bezier = 0.0
previous = bezier_point(0.0)

for step in range(1, 1001):
    t = step / 1000.0
    current = bezier_point(t)

    length_bezier += math.dist(previous, current)
    previous = current

print(
    "Stvarna duzina Bezierove krive:",
    f"{length_bezier:.6f} m"
)

print(
    "Odnos duzine krive i tetive:",
    f"{length_bezier / math.dist(P0, P3):.6f}"
)
max_kappa = 0.0
max_t = None
signed_kappa_at_max = None

max_deviation = 0.0
max_deviation_t = None
signed_deviation = 0.0

for step in range(1001):
    t = step / 1000.0

    point = bezier_point(t)

    # Potpisano bocno odstupanje od pravca P409-P410
    deviation = (
        ux * (point[1] - p[1])
        - uy * (point[0] - p[0])
    )

    if abs(deviation) > max_deviation:
        max_deviation = abs(deviation)
        max_deviation_t = t
        signed_deviation = deviation

print(
    "Najvece bocno odstupanje:",
    f"{max_deviation:.6f} m"
)

print(
    "Pozicija maksimuma:",
    f"t={max_deviation_t:.3f}"
)

print(
    "Smer odstupanja:",
    "LEVO" if signed_deviation > 0 else "DESNO"
)
# Pocetna zakrivljenost Bezierove krive

d1x = 3 * (P1[0] - P0[0])
d1y = 3 * (P1[1] - P0[1])

d2x = 6 * (P2_new[0] - 2*P1[0] + P0[0])
d2y = 6 * (P2_new[1] - 2*P1[1] + P0[1])

kappa_start = (
    (d1x*d2y - d1y*d2x)
    / math.hypot(d1x, d1y)**3
)

radius_start = (
    1.0 / abs(kappa_start)
    if abs(kappa_start) > 1e-12
    else float("inf")
)

print("Pocetna zakrivljenost:", f"{kappa_start:+.9f} 1/m")
print("Pocetni lokalni radijus:", f"{radius_start:.6f} m")
print("Zakrivljenost pravca:", "0.000000000 1/m")
# Presek pocetne i zavrsne tangente

intersection = line_intersection(
    P0,
    (P0[0] + ux, P0[1] + uy),
    P3,
    (P3[0] + vx, P3[1] + vy)
)

print("\nPRESEK TANGENTI")

if intersection is None:
    print("Tangente su paralelne.")
else:
    print(
        "Udaljenost preseka od P0:",
        f"{math.dist(P0, intersection):.6f} m"
    )

    print(
        "Udaljenost preseka od P3:",
        f"{math.dist(P3, intersection):.6f} m"
    )

    forward_start = (
        (intersection[0] - P0[0]) * ux
        + (intersection[1] - P0[1]) * uy
    )

    backward_end = (
        (P3[0] - intersection[0]) * vx
        + (P3[1] - intersection[1]) * vy
    )

    print("Pocetna rucica napred:", f"{forward_start:.6f} m")
    print("Zavrsna rucica napred:", f"{backward_end:.6f} m")
if intersection is not None:
    dx = intersection[0] - P3[0]
    dy = intersection[1] - P3[1]

    longitudinal = dx * vx + dy * vy
    lateral = -dx * vy + dy * vx

    print("\nPOLOZAJ PRESEKA U ODNOSU NA P3")
    print(f"Uzduzno: {longitudinal:+.6f} m")
    print(f"Poprecno: {lateral:+.6f} m")
# Bezierova kriva petog stepena - pocetak

Q0 = P0

Q1 = (
    Q0[0] + handle * ux,
    Q0[1] + handle * uy
)

Q2 = (
    Q0[0] + 2.0 * handle * ux,
    Q0[1] + 2.0 * handle * uy
)

# Provera kolinearnosti
cross = (
    (Q1[0] - Q0[0]) * (Q2[1] - Q1[1])
    - (Q1[1] - Q0[1]) * (Q2[0] - Q1[0])
)

print("\nBEZIER PETOG STEPENA - POCETAK")
print(f"Q0-Q1: {math.dist(Q0, Q1):.6f} m")

print(f"Q1-Q2: {math.dist(Q1, Q2):.6f} m")
print("KOLINEARNOST:", cross)
# Bezier petog stepena - zavrsne tacke

Q5 = P3

Q4 = (
    Q5[0] - required_handle * vx,
    Q5[1] - required_handle * vy
)

# Provera smera zavrsne tangente
tx = Q5[0] - Q4[0]
ty = Q5[1] - Q4[1]

dot = tx * vx + ty * vy
cross_end = tx * vy - ty * vx

print("\nBEZIER PETOG STEPENA - KRAJ")
print(f"Q4-Q5: {math.dist(Q4, Q5):.6f} m")
print(f"Skalarni proizvod: {dot:.9f}")
print(f"Vektorski proizvod: {cross_end:.9f}")
# Potrebna normalna komponenta za R = 4.5 m
L = math.dist(Q4, Q5)

target_normal = (5.0 / 4.0) * kappa_circle * L**2

# Leva normala zavrsne tangente
nx = -vy
ny = vx

# Q3 postavljamo jednu duzinu rucice iza Q4,
# uz potreban bocni pomeraj.
Q3 = (
    Q4[0] - L * vx + target_normal * nx,
    Q4[1] - L * vy + target_normal * ny
)

actual_normal = (
    (Q3[0] - Q4[0]) * nx
    + (Q3[1] - Q4[1]) * ny
)

print("\nBEZIER PETOG STEPENA - Q3")
print(f"Duzina zavrsne rucice: {L:.6f} m")
print(f"Potrebna normalna komponenta: {target_normal:.6f} m")
print(f"Stvarna normalna komponenta: {actual_normal:.6f} m")
def curvature_from_derivatives(dx, dy, ddx, ddy):
    speed = math.hypot(dx, dy)
    return (dx * ddy - dy * ddx) / speed**3


# Pocetak krive, t = 0
dx0 = 5 * (Q1[0] - Q0[0])
dy0 = 5 * (Q1[1] - Q0[1])

ddx0 = 20 * (Q2[0] - 2*Q1[0] + Q0[0])
ddy0 = 20 * (Q2[1] - 2*Q1[1] + Q0[1])

k0 = curvature_from_derivatives(dx0, dy0, ddx0, ddy0)


# Kraj krive, t = 1
dx5 = 5 * (Q5[0] - Q4[0])
dy5 = 5 * (Q5[1] - Q4[1])

ddx5 = 20 * (Q5[0] - 2*Q4[0] + Q3[0])
ddy5 = 20 * (Q5[1] - 2*Q4[1] + Q3[1])

k5 = curvature_from_derivatives(dx5, dy5, ddx5, ddy5)

print("\nBEZIER 5 - PROVERA ZAKRIVLJENOSTI")
print(f"Pocetna zakrivljenost: {k0:+.9f} 1/m")
print(f"Zavrsna zakrivljenost: {k5:+.9f} 1/m")
print(f"Razlika od kruznice: {abs(k5 - kappa_circle):.9f} 1/m")
Q = [Q0, Q1, Q2, Q3, Q4, Q5]

print("\nBEZIER 5 - ZAKRIVLJENOST DUZ KRIVE")

for step in range(11):
    t = step / 10.0
    u = 1.0 - t

    # Prvi izvod: Bezier stepena 4
    dx = 0.0
    dy = 0.0

    for i in range(5):
        c = 5 * math.comb(4, i) * u**(4-i) * t**i
        dx += c * (Q[i+1][0] - Q[i][0])
        dy += c * (Q[i+1][1] - Q[i][1])

    # Drugi izvod: Bezier stepena 3
    ddx = 0.0
    ddy = 0.0

    for i in range(4):
        c = 20 * math.comb(3, i) * u**(3-i) * t**i

        ddx += c * (
            Q[i+2][0] - 2*Q[i+1][0] + Q[i][0]
        )

        ddy += c * (
            Q[i+2][1] - 2*Q[i+1][1] + Q[i][1]
        )

    speed = math.hypot(dx, dy)

    kappa = (
        (dx*ddy - dy*ddx) / speed**3
        if speed > 1e-12
        else float("nan")
    )

    print(f"t={t:.1f}  kappa={kappa:+.6f} 1/m")
max_abs_kappa = 0.0
max_t = None
max_signed_kappa = None

for step in range(1001):
    t = step / 1000.0
    u = 1.0 - t

    dx = dy = 0.0
    ddx = ddy = 0.0

    for i in range(5):
        c = 5 * math.comb(4, i) * u**(4-i) * t**i
        dx += c * (Q[i+1][0] - Q[i][0])
        dy += c * (Q[i+1][1] - Q[i][1])

    for i in range(4):
        c = 20 * math.comb(3, i) * u**(3-i) * t**i
        ddx += c * (Q[i+2][0] - 2*Q[i+1][0] + Q[i][0])
        ddy += c * (Q[i+2][1] - 2*Q[i+1][1] + Q[i][1])

    speed = math.hypot(dx, dy)

    if speed < 1e-12:
        continue

    kappa = (dx * ddy - dy * ddx) / speed**3

    if abs(kappa) > max_abs_kappa:
        max_abs_kappa = abs(kappa)
        max_signed_kappa = kappa
        max_t = t

print("\nBEZIER 5 - MAKSIMALNA ZAKRIVLJENOST")
print(f"Najveca apsolutna zakrivljenost: {max_abs_kappa:.9f} 1/m")
print(f"Pozicija maksimuma: t={max_t:.3f}")
print(f"Potpisana zakrivljenost: {max_signed_kappa:+.9f} 1/m")
print(f"Najmanji lokalni radijus: {1/max_abs_kappa:.6f} m")
def bezier5_point(t):
    u = 1.0 - t

    x = 0.0
    y = 0.0

    for i in range(6):
        c = math.comb(5, i) * u**(5-i) * t**i
        x += c * Q[i][0]
        y += c * Q[i][1]

    return x, y


max_deviation = 0.0
max_t = 0.0
signed_deviation = 0.0

for step in range(1001):
    t = step / 1000.0
    point = bezier5_point(t)

    deviation = (
        ux * (point[1] - p[1])
        - uy * (point[0] - p[0])
    )

    if abs(deviation) > max_deviation:
        max_deviation = abs(deviation)
        max_t = t
        signed_deviation = deviation

print("\nBEZIER 5 - BOCNO ODSTUPANJE")
print(f"Najvece odstupanje: {max_deviation:.6f} m")
print(f"Pozicija maksimuma: t={max_t:.3f}")
print(
    "Smer:",
    "LEVO" if signed_deviation > 0 else "DESNO"
)
length_bezier5 = 0.0
previous = bezier5_point(0.0)

for step in range(1, 1001):
    t = step / 1000.0
    current = bezier5_point(t)

    length_bezier5 += math.dist(previous, current)
    previous = current

chord_length = math.dist(Q0, Q5)

print("\nBEZIER 5 - DUZINA")
print(f"Duzina krive: {length_bezier5:.6f} m")
print(f"Duzina tetive: {chord_length:.6f} m")
print(f"Razlika: {length_bezier5 - chord_length:.6f} m")
print(f"Odnos: {length_bezier5 / chord_length:.6f}")
# Lokalna GPX polilinija oko serpentine P411-P412
gpx_segments = [
    (xy[409], xy[410]),
    (xy[410], xy[411]),
    (xy[411], xy[412]),
]

max_distance = 0.0
max_distance_t = 0.0

for step in range(1001):
    t = step / 1000.0
    point = bezier5_point(t)

    distance = min(
        distance_to_segment(point, a, b)
        for a, b in gpx_segments
    )

    if distance > max_distance:
        max_distance = distance
        max_distance_t = t

print("\nBEZIER 5 - ODSTUPANJE OD GPX")
print(f"Najvece odstupanje: {max_distance:.6f} m")
print(f"Pozicija maksimuma: t={max_distance_t:.3f}")
min_forward = float("inf")
min_forward_t = None

for step in range(1001):
    t = step / 1000.0
    u = 1.0 - t

    dx = 0.0
    dy = 0.0

    for i in range(5):
        c = 5 * math.comb(4, i) * u**(4-i) * t**i

        dx += c * (Q[i+1][0] - Q[i][0])
        dy += c * (Q[i+1][1] - Q[i][1])

    forward = dx * ux + dy * uy

    if forward < min_forward:
        min_forward = forward
        min_forward_t = t

print("\nBEZIER 5 - KRETANJE UNAPRED")
print(f"Najmanja uzduzna komponenta: {min_forward:.6f} m")
print(f"Pozicija minimuma: t={min_forward_t:.3f}")
print(
    "Rezultat:",
    "NAPRED" if min_forward > 0 else "PROBLEM - POVRATAK"
)
angles = []

for step in range(1001):
    t = step / 1000.0
    u = 1.0 - t

    dx = dy = 0.0

    for i in range(5):
        c = 5 * math.comb(4, i) * u**(4-i) * t**i
        dx += c * (Q[i+1][0] - Q[i][0])
        dy += c * (Q[i+1][1] - Q[i][1])

    angles.append(math.atan2(dy, dx))

total_turn = 0.0

for a, b in zip(angles, angles[1:]):
    delta = math.atan2(
        math.sin(b-a),
        math.cos(b-a)
    )
    total_turn += abs(delta)

net_turn = math.atan2(
    math.sin(angles[-1] - angles[0]),
    math.cos(angles[-1] - angles[0])
)

print("\nBEZIER 5 - PROMENA PRAVCA")
print(f"Ukupno skretanje: {math.degrees(total_turn):.6f} stepeni")
print(f"Neto promena pravca: {math.degrees(net_turn):+.6f} stepeni")
print(f"Visak skretanja: {math.degrees(total_turn-abs(net_turn)):.6f} stepeni")
chord_angle = math.atan2(
    P3[1] - P0[1],
    P3[0] - P0[0]
)

start_angle = math.atan2(uy, ux)
end_angle = math.atan2(vy, vx)

def angle_difference(a, b):
    return math.degrees(
        math.atan2(math.sin(a-b), math.cos(a-b))
    )

print("\nGEOMETRIJA PRELAZA P411-P412")

print(
    "Ugao tetive prema pocetnoj tangenti:",
    f"{angle_difference(chord_angle, start_angle):+.6f} stepeni"
)

print(
    "Zavrsna tangenta prema pocetnoj:",
    f"{angle_difference(end_angle, start_angle):+.6f} stepeni"
)
# Probna kubna Bezierova kriva
# Pocetna rucica = 10 m

trial_handle = 10.0

P1_trial = (
    P0[0] + trial_handle * ux,
    P0[1] + trial_handle * uy
)

# Normalna komponenta za zavrsnu zakrivljenost
normal_trial = (
    (P1_trial[0] - P3[0]) * (-vy)
    + (P1_trial[1] - P3[1]) * vx
)

print("\nKUBNA BEZIER - NOVA POCETNA RUCICA")
print(f"Pocetna rucica: {trial_handle:.6f} m")
print(f"Normalna komponenta: {normal_trial:.6f} m")

if normal_trial > 0:
    end_handle_trial = math.sqrt(
        2.0 * normal_trial / (3.0 * kappa_circle)
    )
    print(f"Potrebna zavrsna rucica: {end_handle_trial:.6f} m")
else:
    print("Nema pozitivnog resenja za zavrsnu rucicu.")
P2_trial = (
    P3[0] - end_handle_trial * vx,
    P3[1] - end_handle_trial * vy
)

angles_trial = []

for step in range(1001):
    t = step / 1000.0
    u = 1.0 - t

    dx = 3.0 * (
        u*u * (P1_trial[0] - P0[0])
        + 2*u*t * (P2_trial[0] - P1_trial[0])
        + t*t * (P3[0] - P2_trial[0])
    )

    dy = 3.0 * (
        u*u * (P1_trial[1] - P0[1])
        + 2*u*t * (P2_trial[1] - P1_trial[1])
        + t*t * (P3[1] - P2_trial[1])
    )

    angles_trial.append(math.atan2(dy, dx))

total_trial = 0.0

for a, b in zip(angles_trial, angles_trial[1:]):
    delta = math.atan2(
        math.sin(b-a),
        math.cos(b-a)
    )
    total_trial += abs(delta)

net_trial = math.atan2(
    math.sin(angles_trial[-1] - angles_trial[0]),
    math.cos(angles_trial[-1] - angles_trial[0])
)

print("\nKUBNA BEZIER - NOVO SKRETANJE")
print(f"Ukupno skretanje: {math.degrees(total_trial):.6f} stepeni")
print(f"Neto skretanje: {math.degrees(net_trial):+.6f} stepeni")
print(
    f"Visak skretanja: "
    f"{math.degrees(total_trial - abs(net_trial)):.6f} stepeni"
)
max_kappa_trial = 0.0
max_t_trial = None
signed_kappa_trial = None

for step in range(1001):
    t = step / 1000.0
    u = 1.0 - t

    dx = 3 * (
        u*u * (P1_trial[0] - P0[0])
        + 2*u*t * (P2_trial[0] - P1_trial[0])
        + t*t * (P3[0] - P2_trial[0])
    )

    dy = 3 * (
        u*u * (P1_trial[1] - P0[1])
        + 2*u*t * (P2_trial[1] - P1_trial[1])
        + t*t * (P3[1] - P2_trial[1])
    )

    ddx = 6 * (
        u * (P2_trial[0] - 2*P1_trial[0] + P0[0])
        + t * (P3[0] - 2*P2_trial[0] + P1_trial[0])
    )

    ddy = 6 * (
        u * (P2_trial[1] - 2*P1_trial[1] + P0[1])
        + t * (P3[1] - 2*P2_trial[1] + P1_trial[1])
    )

    speed = math.hypot(dx, dy)

    if speed < 1e-12:
        continue

    kappa = (dx * ddy - dy * ddx) / speed**3

    if abs(kappa) > max_kappa_trial:
        max_kappa_trial = abs(kappa)
        max_t_trial = t
        signed_kappa_trial = kappa

print("\nNOVA KUBNA KRIVA - ZAKRIVLJENOST")
print(f"Najveca zakrivljenost: {max_kappa_trial:.9f} 1/m")
print(f"Pozicija maksimuma: t={max_t_trial:.3f}")
print(f"Potpisana zakrivljenost: {signed_kappa_trial:+.9f} 1/m")
print(f"Najmanji radijus: {1/max_kappa_trial:.6f} m")
# Pocetna zakrivljenost nove kubne krive

dx0 = 3 * (P1_trial[0] - P0[0])
dy0 = 3 * (P1_trial[1] - P0[1])

ddx0 = 6 * (
    P2_trial[0] - 2*P1_trial[0] + P0[0]
)

ddy0 = 6 * (
    P2_trial[1] - 2*P1_trial[1] + P0[1]
)

kappa_start_trial = (
    (dx0 * ddy0 - dy0 * ddx0)
    / math.hypot(dx0, dy0)**3
)

radius_start_trial = (
    1.0 / abs(kappa_start_trial)
    if abs(kappa_start_trial) > 1e-12
    else float("inf")
)

print("\nNOVA KUBNA KRIVA - POCETAK")
print(f"Pocetna zakrivljenost: {kappa_start_trial:+.9f} 1/m")
print(f"Pocetni lokalni radijus: {radius_start_trial:.6f} m")
print(f"Razlika od pravca: {abs(kappa_start_trial):.9f} 1/m")
def bezier_trial_point(t):
    u = 1.0 - t

    return (
        u**3 * P0[0]
        + 3*u*u*t * P1_trial[0]
        + 3*u*t*t * P2_trial[0]
        + t**3 * P3[0],

        u**3 * P0[1]
        + 3*u*u*t * P1_trial[1]
        + 3*u*t*t * P2_trial[1]
        + t**3 * P3[1]
    )


max_distance_trial = 0.0
max_distance_t = 0.0

for step in range(1001):
    t = step / 1000.0
    point = bezier_trial_point(t)

    distance = min(
        distance_to_segment(point, a, b)
        for a, b in gpx_segments
    )

    if distance > max_distance_trial:
        max_distance_trial = distance
        max_distance_t = t

print("\nNOVA KUBNA KRIVA - ODSTUPANJE OD GPX")
print(f"Najvece odstupanje: {max_distance_trial:.6f} m")
print(f"Pozicija maksimuma: t={max_distance_t:.3f}")
print(f"Razlika prema Bezier 5: {max_distance_trial - 0.402845:+.6f} m")
min_forward = float("inf")
min_forward_t = None

for step in range(1001):
    t = step / 1000.0
    u = 1.0 - t

    dx = 3 * (
        u*u * (P1_trial[0] - P0[0])
        + 2*u*t * (P2_trial[0] - P1_trial[0])
        + t*t * (P3[0] - P2_trial[0])
    )

    dy = 3 * (
        u*u * (P1_trial[1] - P0[1])
        + 2*u*t * (P2_trial[1] - P1_trial[1])
        + t*t * (P3[1] - P2_trial[1])
    )

    forward = dx * ux + dy * uy

    if forward < min_forward:
        min_forward = forward
        min_forward_t = t

print("\nNOVA KUBNA KRIVA - KRETANJE UNAPRED")
print(f"Najmanja projekcija tangente: {min_forward:+.6f}")
print(f"Pozicija minimuma: t={min_forward_t:.3f}")
print(
    "Kretanje unapred:",
    "DA" if min_forward > 0 else "NE"
)
# Kubna Bezierova kriva:
# Broj promena znaka zakrivljenosti

sign_changes = 0
previous_sign = 0
change_positions = []

for step in range(1001):
    t = step / 1000.0
    u = 1.0 - t

    dx = 3 * (
        u*u * (P1_trial[0] - P0[0])
        + 2*u*t * (P2_trial[0] - P1_trial[0])
        + t*t * (P3[0] - P2_trial[0])
    )

    dy = 3 * (
        u*u * (P1_trial[1] - P0[1])
        + 2*u*t * (P2_trial[1] - P1_trial[1])
        + t*t * (P3[1] - P2_trial[1])
    )

    ddx = 6 * (
        u * (P2_trial[0] - 2*P1_trial[0] + P0[0])
        + t * (P3[0] - 2*P2_trial[0] + P1_trial[0])
    )

    ddy = 6 * (
        u * (P2_trial[1] - 2*P1_trial[1] + P0[1])
        + t * (P3[1] - 2*P2_trial[1] + P1_trial[1])
    )

    cross = dx * ddy - dy * ddx

    sign = 1 if cross > 1e-10 else -1 if cross < -1e-10 else 0

    if sign != 0:
        if previous_sign != 0 and sign != previous_sign:
            sign_changes += 1
            change_positions.append(t)

        previous_sign = sign

print("\nKUBNA BEZIER - PROMENE ZAKRIVLJENOSTI")
print(f"Broj promena znaka: {sign_changes}")
print(f"Pozicije promena: {change_positions}")
print(
    "Jednostavan S-prelaz:",
    "DA" if sign_changes == 1 else "NE"
)
# Duzina nove kubne Bezierove krive

previous_point = bezier_trial_point(0.0)
curve_length = 0.0

for step in range(1, 1001):
    t = step / 1000.0
    current_point = bezier_trial_point(t)

    curve_length += math.dist(
        previous_point,
        current_point
    )

    previous_point = current_point

chord_length = math.dist(P0, P3)

print("\nNOVA KUBNA KRIVA - DUZINA")
print(f"Duzina krive: {curve_length:.6f} m")
print(f"Duzina tetive: {chord_length:.6f} m")
print(f"Razlika: {curve_length - chord_length:.6f} m")
#'@ | python -
def make_cubic_bezier(
    start,
    end,
    start_direction,
    end_direction,
    start_handle,
    radius=4.5
):
    """
    Konstruise kubnu Bezierovu krivu sa zadatom
    zavrsnom zakrivljenoscu 1/radius.
    """

    x0, y0 = start
    x3, y3 = end
    ux, uy = start_direction
    vx, vy = end_direction

    p1 = (
        x0 + start_handle * ux,
        y0 + start_handle * uy
    )

    normal = (
        (p1[0] - x3) * (-vy)
        + (p1[1] - y3) * vx
    )

    if normal <= 0:
        raise ValueError(
            "Nije moguce dobiti trazenu "
            "zavrsnu zakrivljenost."
        )

    end_handle = math.sqrt(
        2.0 * normal * radius / 3.0
    )

    p2 = (
        x3 - end_handle * vx,
        y3 - end_handle * vy
    )

    return start, p1, p2, end
control_points = make_cubic_bezier(
    start=P0,
    end=P3,
    start_direction=(ux, uy),
    end_direction=(vx, vy),
    start_handle=10.0,
    radius=4.5
)

expected_points = (
    P0,
    P1_trial,
    P2_trial,
    P3
)

max_error = max(
    math.dist(actual, expected)
    for actual, expected in zip(
        control_points,
        expected_points
    )
)

print("\nREGRESIONI TEST P411-P412")
print(f"Najveca razlika: {max_error:.12f} m")
print("TEST:", "OK" if max_error < 1e-9 else "GRESKA")
'@ | python -





















@'
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize, least_squares
from stelvio_transitions import load_stelvio_points

path = r"C:\Vezbe\MotorcyclePoseSim\stelvio_terrain\data\salita-al-passo-dello-stelvio-da-prato.gpx"
p = load_stelvio_points(path)

original = np.array(p[488:494], dtype=float)
origin = original[0].copy()
local = original - origin

lengths = np.linalg.norm(np.diff(local, axis=0), axis=1)
s = np.r_[0.0, np.cumsum(lengths)]

def unit(a,b):
    d = np.asarray(b,dtype=float)-np.asarray(a,dtype=float)
    return d/np.linalg.norm(d)

entry = unit(p[487],p[488])
exit = unit(p[492],p[493])

limit = 1.0/4.55
sample = np.linspace(s[0],s[-1],1201)

def geometry(x,positions):
    pts = local.copy()
    pts[1:5] += x.reshape(4,2)

    curve = CubicSpline(
        s,pts,axis=0,
        bc_type=((1,entry),(1,exit))
    )

    d1 = curve(positions,1)
    d2 = curve(positions,2)

    speed = np.linalg.norm(d1,axis=1)

    cross = d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0]
    k = cross/np.maximum(speed,1e-9)**3

    return k,speed

def soft_residual(x):
    k,speed = geometry(x,sample)

    return np.r_[
        x/2.0,
        70*np.maximum(np.abs(k)-limit,0),
        20*np.maximum(0.4-speed,0)
    ]

initial = least_squares(
    soft_residual,np.zeros(8),
    max_nfev=200
).x

def objective(x):
    return np.sum(x*x)

def constraints(x):
    k,speed = geometry(x,sample)

    return np.r_[
        limit-k,
        limit+k,
        speed-0.4
    ]

result = minimize(
    objective,
    initial,
    method="SLSQP",
    constraints=[{
        "type":"ineq",
        "fun":constraints
    }],
    options={
        "maxiter":500,
        "ftol":1e-10,
        "disp":False
    }
)

dense = np.linspace(s[0],s[-1],12001)
k,speed = geometry(result.x,dense)

rmin = 1.0/np.max(np.abs(k))
shifts = np.linalg.norm(result.x.reshape(4,2),axis=1)

print("SLSQP uspesan:",result.success)
print("Poruka:",result.message)
print("Iteracije:",result.nit)
print("Minimalni radijus:",round(rmin,6),"m")
print("Najveci pomeraj:",round(shifts.max(),6),"m")
print("Minimalna brzina:",round(speed.min(),6))
print("Uzoraka ispod R4.5:",
      np.count_nonzero(np.abs(k)>limit+1e-9))
print("Zadovoljava R4.5:",rmin>=4.5-1e-6)

print()
for j in range(4):
    print(f"P{489+j}: pomeraj = {shifts[j]:.6f} m")
from scipy.spatial import cKDTree

# Rekonstruišemo optimizovanu krivu.
optimized = local.copy()
optimized[1:5] += result.x.reshape(4, 2)

curve = CubicSpline(
    s, optimized, axis=0,
    bc_type=((1, entry), (1, exit))
)

# Gusto uzorkovana optimizovana trasa.
positions = np.linspace(s[0], s[-1], 12001)
path_points = curve(positions)

# Rastojanje svake tacke krive do najblizeg
# segmenta originalne GPX polilinije.
best = np.full(len(path_points), np.inf)

for j in range(len(local)-1):
    A = local[j]
    B = local[j+1]
    AB = B-A

    t = np.clip(
        ((path_points-A) @ AB) / (AB @ AB),
        0.0, 1.0
    )

    projection = A + t[:, None]*AB
    distance = np.linalg.norm(
        path_points-projection, axis=1
    )

    best = np.minimum(best, distance)

# Proveravamo i suprotan smer:
# GPX polilinija -> optimizovana kriva.
gpx_samples = []

for j in range(len(local)-1):
    A = local[j]
    B = local[j+1]
    count = max(2, int(np.ceil(np.linalg.norm(B-A)/0.05))+1)

    t = np.linspace(0, 1, count)
    gpx_samples.append(A+t[:, None]*(B-A))

gpx_samples = np.vstack(gpx_samples)

tree = cKDTree(path_points)
reverse_distances, _ = tree.query(gpx_samples)

imax = int(np.argmax(best))
segment = np.searchsorted(
    s, positions[imax], side="right"
)-1
segment = min(max(segment, 0), len(s)-2)

print()
print("ODSTUPANJE OD GPX TRASE")
print("-----------------------")
print("Maks. kriva -> GPX:",
      round(best.max(), 6), "m")
print("Srednje kriva -> GPX:",
      round(best.mean(), 6), "m")
print("Maks. GPX -> kriva:",
      round(reverse_distances.max(), 6), "m")
print("Priblizno obostrano maks.:",
      round(max(best.max(), reverse_distances.max()), 6), "m")
print("Najvece odstupanje krive na:",
      f"P{488+segment}-P{489+segment}")
# Originalni spline, bez pomeranja GPX tacaka.
original_curve = CubicSpline(
    s, local, axis=0,
    bc_type=((1, entry), (1, exit))
)

original_spline = original_curve(positions)

def distance_to_gpx(points):
    best_distance = np.full(len(points), np.inf)

    for j in range(len(local)-1):
        A = local[j]
        B = local[j+1]
        AB = B-A

        t = np.clip(
            ((points-A) @ AB)/(AB @ AB),
            0.0, 1.0
        )

        projection = A+t[:,None]*AB

        distance = np.linalg.norm(
            points-projection, axis=1
        )

        best_distance = np.minimum(
            best_distance, distance
        )

    return best_distance

baseline_error = distance_to_gpx(original_spline)

# Koliko je optimizacija promenila samu krivu?
curve_change = np.linalg.norm(
    path_points-original_spline,
    axis=1
)

i = int(np.argmax(best))

print()
print("POREDJENJE DVE KRIVE")
print("---------------------------")
print("Originalni spline - max. odstupanje:",
      round(baseline_error.max(),6),"m")
print("Optimizovani spline - max. odstupanje:",
      round(best.max(),6),"m")
print("Najveca promena izmedju spline krivih:",
      round(curve_change.max(),6),"m")

print()
print("NA MESTU NAJVECEG ODSTUPANJA")
print("Originalni spline od GPX:",
      round(baseline_error[i],6),"m")
print("Optimizovani spline od GPX:",
      round(best[i],6),"m")
print("Pomeraj optimizacijom:",
      round(curve_change[i],6),"m")
# NOVI CILJ: cela kriva sto blize GPX poliliniji.

fit_positions = np.linspace(s[0], s[-1], 301)

def fit_objective(x):
    pts = local.copy()
    pts[1:5] += x.reshape(4, 2)

    fitted = CubicSpline(
        s, pts, axis=0,
        bc_type=((1, entry), (1, exit))
    )(fit_positions)

    best2 = np.full(len(fitted), np.inf)

    for j in range(len(local)-1):
        A = local[j]
        B = local[j+1]
        AB = B-A

        t = np.clip(
            ((fitted-A) @ AB)/(AB @ AB),
            0.0, 1.0
        )

        projection = A+t[:, None]*AB

        d2 = np.sum(
            (fitted-projection)**2, axis=1
        )

        best2 = np.minimum(best2, d2)

    # Srednja greska + kazna za veca odstupanja
    # + blaga kazna za pomeranje GPX tacaka.
    return (
        np.mean(best2)
        + 0.4*np.sqrt(np.mean(best2**2))
        + 0.1*np.mean(x*x)
    )

# Polazimo od prethodnog optimizovanog resenja.
previous_x = result.x.copy()

new_result = minimize(
    fit_objective,
    previous_x,
    method="SLSQP",
    bounds=[(-3.0, 3.0)]*8,
    constraints=[{
        "type": "ineq",
        "fun": constraints
    }],
    options={
        "maxiter": 250,
        "ftol": 1e-9
    }
)

# Provera na gustoj mrezi.
new_points = local.copy()
new_points[1:5] += new_result.x.reshape(4, 2)

new_curve = CubicSpline(
    s, new_points, axis=0,
    bc_type=((1, entry), (1, exit))
)

new_path = new_curve(dense)
new_k, new_speed = geometry(new_result.x, dense)

new_error = distance_to_gpx(new_path)
new_shifts = np.linalg.norm(
    new_result.x.reshape(4, 2), axis=1
)

print()
print("OPTIMIZACIJA CELE TRASE")
print("-----------------------------")
print("SLSQP uspesan:", new_result.success)
print("Poruka:", new_result.message)
print("Rmin:", round(1/np.max(np.abs(new_k)), 6), "m")
print("Maks. odstupanje od GPX:",
      round(new_error.max(), 6), "m")
print("Srednje odstupanje:",
      round(new_error.mean(), 6), "m")
print("Najveci pomeraj GPX tacke:",
      round(new_shifts.max(), 6), "m")
print("Uzoraka ispod R4.5:",
      np.count_nonzero(
          np.abs(new_k) > 1/4.5
      ))
print()
print("ODSTUPANJE PO SEGMENTIMA")
print("-" * 61)
print("Segment       Original     Prva opt.     Nova opt.")

for j in range(len(s)-1):
    mask = (dense >= s[j]) & (dense <= s[j+1])

    e0 = baseline_error[mask].max()
    e1 = best[mask].max()
    e2 = new_error[mask].max()

    print(
        f"P{488+j}-P{489+j}    "
        f"{e0:9.3f} m   "
        f"{e1:9.3f} m   "
        f"{e2:9.3f} m"
    )

imax = int(np.argmax(new_error))

segment = np.searchsorted(
    s, dense[imax], side="right"
)-1
segment = min(max(segment, 0), len(s)-2)

print()
print("NAJGORE MESTO NOVE KRIVE")
print("Segment:", f"P{488+segment}-P{489+segment}")
print("Parametar s:", round(dense[imax], 6), "m")
print("Odstupanje:", round(new_error[imax], 6), "m")

print()
print("POMERAJI KONTROLNIH TACAKA")
for j, shift in enumerate(new_shifts):
    print(f"P{489+j}: {shift:.6f} m")

# DODATNA TACKA NA SEGMENTU P490-P491

mid_s = (s[2] + s[3]) / 2.0
mid_point = (local[2] + local[3]) / 2.0

# Umetanje pomocne tacke izmedju P490 i P491.
s6 = np.insert(s, 3, mid_s)
points6 = np.insert(local, 3, mid_point, axis=0)

curve6 = CubicSpline(
    s6,
    points6,
    axis=0,
    bc_type=((1, entry), (1, exit))
)

positions6 = np.linspace(s6[0], s6[-1], 12001)

path6 = curve6(positions6)

d1 = curve6(positions6, 1)
d2 = curve6(positions6, 2)

speed6 = np.linalg.norm(d1, axis=1)

cross6 = (
    d1[:, 0]*d2[:, 1]
    - d1[:, 1]*d2[:, 0]
)

k6 = cross6 / np.maximum(speed6, 1e-9)**3

error6 = distance_to_gpx(path6)

imax = int(np.argmax(error6))
j = np.searchsorted(
    s, positions6[imax], side="right"
)-1
j = min(max(j, 0), len(s)-2)

print()
print("SPLINE SA DODATNOM TACKOM")
print("-"*42)
print("Rmin:", round(1/np.max(np.abs(k6)), 6), "m")
print("Maks. odstupanje:",
      round(error6.max(), 6), "m")
print("Srednje odstupanje:",
      round(error6.mean(), 6), "m")
print("Najgori segment:",
      f"P{488+j}-P{489+j}")
print("Minimalna brzina:",
      round(speed6.min(), 6))
print("Zadovoljava R4.5:",
      1/np.max(np.abs(k6)) >= 4.5)
# ANALIZA ZAKRIVLJENOSTI PO GPX SEGMENTIMA

print()
print("RADIJUS PO SEGMENTIMA")
print("-" * 48)

for j in range(len(s)-1):
    mask = (
        (positions6 >= s[j]) &
        (positions6 <= s[j+1])
    )

    segment_k = np.abs(k6[mask])

    rmin_segment = 1.0 / segment_k.max()

    print(
        f"P{488+j}-P{489+j}: "
        f"Rmin = {rmin_segment:.6f} m"
    )

# Tacna lokacija najvece uzorkovane zakrivljenosti
i = int(np.argmax(np.abs(k6)))

j = np.searchsorted(
    s, positions6[i], side="right"
) - 1

j = min(max(j, 0), len(s)-2)

print()
print("KRITICNA TACKA")
print("-" * 48)
print("Segment:", f"P{488+j}-P{489+j}")
print("s:", round(positions6[i], 6), "m")
print("Rmin:", round(1/abs(k6[i]), 6), "m")
print("Zakrivljenost:", round(k6[i], 6), "1/m")
print("Odstupanje od GPX:",
      round(error6[i], 6), "m")

print()
print("BROJ UZORAKA SA R < 4.5 m PO SEGMENTIMA")

for j in range(len(s)-1):
    mask = (
        (positions6 >= s[j]) &
        (positions6 <= s[j+1])
    )

    count = np.count_nonzero(
        np.abs(k6[mask]) > 1/4.5
    )

    print(f"P{488+j}-P{489+j}: {count}")
# OPTIMIZACIJA SA POMOCNOM TACKOM

sample7 = np.linspace(s6[0], s6[-1], 801)
dense7 = np.linspace(s6[0], s6[-1], 12001)

limit7 = 1.0 / 4.55

def curve7(x):
    pts = points6.copy()
    pts[1:6] += x.reshape(5, 2)

    return CubicSpline(
        s6, pts, axis=0,
        bc_type=((1, entry), (1, exit))
    )

def geometry7(x, positions):
    curve = curve7(x)

    d1 = curve(positions, 1)
    d2 = curve(positions, 2)

    speed = np.linalg.norm(d1, axis=1)

    cross = (
        d1[:, 0]*d2[:, 1]
        - d1[:, 1]*d2[:, 0]
    )

    k = cross / np.maximum(speed, 1e-9)**3

    return k, speed

def residual7(x):
    k, speed = geometry7(x, sample7)

    return np.r_[
        x / 2.0,
        70.0*np.maximum(np.abs(k)-limit7, 0),
        20.0*np.maximum(0.4-speed, 0)
    ]

initial7 = least_squares(
    residual7,
    np.zeros(10),
    max_nfev=200
).x

def objective7(x):
    # Kazna za pomeranje originalnih GPX tacaka
    shifts = x.reshape(5, 2)

    original_penalty = np.sum(
        shifts[[0, 1, 3, 4]]**2
    )

    # Pomocna tacka sme malo slobodnije da se pomera
    auxiliary_penalty = np.sum(shifts[2]**2)

    fitted = curve7(x)(sample7)
    error = distance_to_gpx(fitted)

    return (
        original_penalty
        + 0.3*auxiliary_penalty
        + 2.0*np.mean(error**2)
    )

def constraints7(x):
    k, speed = geometry7(x, sample7)

    return np.r_[
        limit7-k,
        limit7+k,
        speed-0.4
    ]

result7 = minimize(
    objective7,
    initial7,
    method="SLSQP",
    bounds=[(-5.0, 5.0)]*10,
    constraints=[{
        "type": "ineq",
        "fun": constraints7
    }],
    options={
        "maxiter": 400,
        "ftol": 1e-9
    }
)

k7, speed7 = geometry7(result7.x, dense7)

path7 = curve7(result7.x)(dense7)
error7 = distance_to_gpx(path7)

shifts7 = np.linalg.norm(
    result7.x.reshape(5, 2),
    axis=1
)

print()
print("OPTIMIZACIJA SA POMOCNOM TACKOM")
print("-"*45)
print("SLSQP uspesan:", result7.success)
print("Poruka:", result7.message)
print("Iteracije:", result7.nit)
print("Rmin:", round(1/np.max(np.abs(k7)), 6), "m")
print("Maks. odstupanje:",
      round(error7.max(), 6), "m")
print("Srednje odstupanje:",
      round(error7.mean(), 6), "m")
print("Min. parametarska brzina:",
      round(speed7.min(), 6))
print("Uzoraka ispod R4.5:",
      np.count_nonzero(np.abs(k7)>1/4.5))

print()
print("POMERAJI TACAKA")
for name, shift in zip(
    ["P489", "P490", "Pomocna", "P491", "P492"],
    shifts7
):
    print(f"{name}: {shift:.6f} m")
print()
print("ANALIZA SEDAM KONTROLNIH TACAKA")
print("-" * 56)
print("Segment          Rmin (m)     Max. odstupanje (m)")

for j in range(len(s)-1):
    mask = (
        (dense7 >= s[j]) &
        (dense7 <= s[j+1])
    )

    r = 1.0 / np.max(np.abs(k7[mask]))
    e = np.max(error7[mask])

    print(
        f"P{488+j}-P{489+j}       "
        f"{r:10.4f}       {e:10.4f}"
    )

# Lokacija najveceg odstupanja
ie = int(np.argmax(error7))

# Lokacija najmanjeg radijusa
ik = int(np.argmax(np.abs(k7)))

def segment_name(position):
    j = np.searchsorted(s, position, side="right")-1
    j = min(max(j, 0), len(s)-2)
    return f"P{488+j}-P{489+j}"

print()
print("NAJVECE ODSTUPANJE")
print("Segment:", segment_name(dense7[ie]))
print("s:", round(dense7[ie], 6), "m")
print("Odstupanje:", round(error7[ie], 6), "m")
print("Radijus na tom mestu:",
      round(1/abs(k7[ie]), 6), "m")

print()
print("NAJMANJI RADIJUS")
print("Segment:", segment_name(dense7[ik]))
print("s:", round(dense7[ik], 6), "m")
print("Radijus:", round(1/abs(k7[ik]), 6), "m")
print("Odstupanje na tom mestu:",
      round(error7[ik], 6), "m")

print()
print("POMERAJ POMOCNE TACKE")
shift = result7.x.reshape(5, 2)[2]

print("dx:", round(shift[0], 6), "m")
print("dy:", round(shift[1], 6), "m")
# TEST: pomocna tacka na 40% segmenta P490-P491

fraction = 0.40

new_mid_s = s[2] + fraction * (s[3] - s[2])

new_mid_point = (
    local[2] + fraction * (local[3] - local[2])
)

s40 = np.insert(s, 3, new_mid_s)
points40 = np.insert(local, 3, new_mid_point, axis=0)

def curve40(x):
    pts = points40.copy()
    pts[1:6] += x.reshape(5, 2)

    return CubicSpline(
        s40, pts, axis=0,
        bc_type=((1, entry), (1, exit))
    )

def geometry40(x, positions):
    curve = curve40(x)

    d1 = curve(positions, 1)
    d2 = curve(positions, 2)

    speed = np.linalg.norm(d1, axis=1)

    cross = (
        d1[:, 0]*d2[:, 1]
        - d1[:, 1]*d2[:, 0]
    )

    k = cross / np.maximum(speed, 1e-9)**3

    return k, speed

# Pocetna geometrija iz prethodnog resenja.
x0 = result7.x.reshape(5, 2).copy()

# Pomocna tacka na novom parametru prati staru krivu.
old_curve = curve7(result7.x)
x0[2] = old_curve(new_mid_s) - new_mid_point

x0 = x0.ravel()

def objective40(x):
    shifts = x.reshape(5, 2)

    fitted = curve40(x)(sample7)
    error = distance_to_gpx(fitted)

    return (
        np.sum(shifts[[0, 1, 3, 4]]**2)
        + 0.3*np.sum(shifts[2]**2)
        + 2.0*np.mean(error**2)
    )

def constraints40(x):
    k, speed = geometry40(x, sample7)

    return np.r_[
        limit7-k,
        limit7+k,
        speed-0.4
    ]

result40 = minimize(
    objective40,
    x0,
    method="SLSQP",
    bounds=[(-6.0, 6.0)]*10,
    constraints=[{
        "type": "ineq",
        "fun": constraints40
    }],
    options={
        "maxiter": 400,
        "ftol": 1e-9
    }
)

k40, speed40 = geometry40(result40.x, dense7)
path40 = curve40(result40.x)(dense7)
error40 = distance_to_gpx(path40)

shifts40 = np.linalg.norm(
    result40.x.reshape(5, 2), axis=1
)

imax = int(np.argmax(error40))
j = np.searchsorted(
    s, dense7[imax], side="right"
)-1
j = min(max(j, 0), len(s)-2)

print()
print("POREDJENJE POLOZAJA POMOCNE TACKE")
print("-"*48)
print("                         50%          40%")
print(f"Rmin:                  {1/np.max(np.abs(k7)):9.4f}    {1/np.max(np.abs(k40)):9.4f}")
print(f"Maks. odstupanje:      {error7.max():9.4f}    {error40.max():9.4f}")
print(f"Srednje odstupanje:    {error7.mean():9.4f}    {error40.mean():9.4f}")
print(f"Max. pomeraj GPX:      {max(shifts7[0],shifts7[1],shifts7[3],shifts7[4]):9.4f}    {max(shifts40[0],shifts40[1],shifts40[3],shifts40[4]):9.4f}")

print()
print("SLSQP uspesan:", result40.success)
print("Poruka:", result40.message)
print("Minimalna brzina:", round(speed40.min(), 6))
print("Uzoraka ispod R4.5:",
      np.count_nonzero(np.abs(k40)>1/4.5))
print("Najgori segment:", f"P{488+j}-P{489+j}")
print("Pomeraj pomocne tacke:",
      round(shifts40[2], 6), "m")
# GEOMETRIJA NAJVECEG ODSTUPANJA - MODEL 40%

i = int(np.argmax(error40))
Q = path40[i]
position = dense7[i]

print()
print("GEOMETRIJA NAJVECEG ODSTUPANJA")
print("-" * 48)

print("Parametar s:", round(position, 6), "m")
print("Tacka krive X:", round(Q[0], 6))
print("Tacka krive Y:", round(Q[1], 6))

nearest = None

for j in range(len(local)-1):
    A = local[j]
    B = local[j+1]
    AB = B-A

    t = np.clip(
        np.dot(Q-A, AB) / np.dot(AB, AB),
        0.0, 1.0
    )

    foot = A + t*AB
    distance = np.linalg.norm(Q-foot)

    if nearest is None or distance < nearest[0]:
        signed_cross = (
            AB[0]*(Q-A)[1]
            - AB[1]*(Q-A)[0]
        )

        nearest = (
            distance, j, t,
            signed_cross, foot
        )

distance, j, t, side, foot = nearest

print()
print("NAJBLIZI GPX SEGMENT")
print("Segment:", f"P{488+j}-P{489+j}")
print("Projekcija t:", round(t, 6))
print("Udaljenost:", round(distance, 6), "m")
print("Strana:",
      "LEVO" if side > 0 else
      "DESNO" if side < 0 else
      "NA PRAVOJ")

print()
print("NAJBLIZA TACKA GPX POLILINIJE")
print("X:", round(foot[0], 6))
print("Y:", round(foot[1], 6))

# Ugao tangente spline krive i najblizeg GPX segmenta
tangent = curve40(result40.x)(position, 1)

gpx_direction = local[j+1]-local[j]

angle = np.degrees(np.arctan2(
    tangent[0]*gpx_direction[1]
    - tangent[1]*gpx_direction[0],
    np.dot(tangent, gpx_direction)
))

print()
print("RAZLIKA PRAVACA")
print("Ugao spline / GPX:",
      round(angle, 6), "stepeni")
# MINIMAKS ZA MODEL SA 7 TACAKA
# Originalne GPX tacke: max. pomeraj 2 m
# Pomocna tacka: max. pomeraj 5 m

fit40 = np.linspace(s40[0], s40[-1], 401)

def objective_minimax40(z):
    x = z[:10]
    E = z[10]

    shifts = x.reshape(5, 2)

    original_cost = np.sum(
        shifts[[0, 1, 3, 4]]**2
    )

    auxiliary_cost = np.sum(shifts[2]**2)

    error = distance_to_gpx(
        curve40(x)(fit40)
    )

    return (
        E
        + 0.05*original_cost
        + 0.01*auxiliary_cost
        + 0.1*np.mean(error**2)
    )

def constraints_minimax40(z):
    x = z[:10]
    E = z[10]

    shifts = x.reshape(5, 2)

    original_norms = np.linalg.norm(
        shifts[[0, 1, 3, 4]], axis=1
    )

    auxiliary_norm = np.linalg.norm(shifts[2])

    error = distance_to_gpx(
        curve40(x)(fit40)
    )

    return np.r_[
        constraints40(x),
        E-error,
        2.0-original_norms,
        5.0-auxiliary_norm
    ]

start_x = result40.x.copy()

start_E = distance_to_gpx(
    curve40(start_x)(fit40)
).max() + 0.01

z0 = np.r_[start_x, start_E]

result_mm40 = minimize(
    objective_minimax40,
    z0,
    method="SLSQP",
    bounds=[(-6.0, 6.0)]*10 + [(0.0, 20.0)],
    constraints=[{
        "type": "ineq",
        "fun": constraints_minimax40
    }],
    options={
        "maxiter": 400,
        "ftol": 1e-9,
        "disp": False
    }
)

x_mm = result_mm40.x[:10]

k_mm, speed_mm = geometry40(x_mm, dense7)

path_mm = curve40(x_mm)(dense7)
error_mm = distance_to_gpx(path_mm)

shifts_mm = np.linalg.norm(
    x_mm.reshape(5, 2), axis=1
)

print()
print("MINIMAKS SA OGRANICENJEM POMERAJA")
print("-"*49)

print("SLSQP uspesan:", result_mm40.success)
print("Poruka:", result_mm40.message)
print("Iteracije:", result_mm40.nit)

print("Rmin:",
      round(1/np.max(np.abs(k_mm)), 6), "m")

print("Maks. odstupanje:",
      round(error_mm.max(), 6), "m")

print("Srednje odstupanje:",
      round(error_mm.mean(), 6), "m")

print("Max. pomeraj originalnih:",
      round(max(shifts_mm[0], shifts_mm[1],
                shifts_mm[3], shifts_mm[4]), 6), "m")

print("Pomeraj pomocne:",
      round(shifts_mm[2], 6), "m")

print("Minimalna brzina:",
      round(speed_mm.min(), 6))

print("Uzoraka ispod R4.5:",
      np.count_nonzero(np.abs(k_mm)>1/4.5))

print("Zadata granica E:",
      round(result_mm40.x[10], 6), "m")

print("Najmanja vrednost ogranicenja:",
      round(np.min(
          constraints_minimax40(result_mm40.x)
      ), 9))
from scipy.optimize import brentq

C = curve40(x_mm)

def curvature_at(t):
    v = C(t, 1)
    a = C(t, 2)

    cross = v[0]*a[1] - v[1]*a[0]
    speed2 = np.dot(v, v)

    return cross / speed2**1.5

def curvature_stationary(t):
    v = C(t, 1)
    a = C(t, 2)
    jerk = C(t, 3)

    speed2 = np.dot(v, v)
    va = np.dot(v, a)

    cross = v[0]*a[1] - v[1]*a[0]
    cross_prime = v[0]*jerk[1] - v[1]*jerk[0]

    return cross_prime*speed2 - 3*cross*va

candidates = list(s40)

for j in range(len(s40)-1):
    a = s40[j]
    b = s40[j+1]

    samples = np.linspace(a, b, 1001)
    values = [
        curvature_stationary(t)
        for t in samples
    ]

    for i in range(len(samples)-1):
        f0 = values[i]
        f1 = values[i+1]

        if f0 == 0:
            candidates.append(samples[i])
        elif f0*f1 < 0:
            root = brentq(
                curvature_stationary,
                samples[i],
                samples[i+1]
            )
            candidates.append(root)

radii = []

for t in candidates:
    k = abs(curvature_at(t))

    if k > 1e-12:
        radii.append((1/k, t))

rmin_exact, tmin = min(radii)

print()
print("PROVERA EKSTREMA ZAKRIVLJENOSTI")
print("-"*46)
print("Broj kandidata:", len(candidates))
print("Najmanji pronadjeni radijus:",
      round(rmin_exact, 9), "m")
print("Parametar s:",
      round(tmin, 9), "m")
print("Rezerva iznad R4.5:",
      round(rmin_exact-4.5, 9), "m")
print("Zadovoljava R4.5:",
      rmin_exact >= 4.5)
print("Zadovoljava R4.55:",
      rmin_exact >= 4.55)
# PROVERA SAMOPRESEKA SPLINE KRIVE

test_s = np.linspace(s40[0], s40[-1], 2001)
test_path = curve40(x_mm)(test_s)

A = test_path[:-1]
B = test_path[1:]
D = B - A

def cross2(a, b):
    return a[..., 0]*b[..., 1] - a[..., 1]*b[..., 0]

intersections = []

for i in range(len(A)-2):
    # Preskacemo susedne segmente.
    j = np.arange(i+2, len(A))

    r = D[i]
    q = A[j] - A[i]
    v = D[j]

    denom = cross2(r, v)
    valid = np.abs(denom) > 1e-12

    if not np.any(valid):
        continue

    jj = j[valid]
    q = q[valid]
    v = v[valid]
    den = denom[valid]

    t = cross2(q, v) / den
    u = cross2(q, r) / den

    hit = (
        (t >= 0) & (t <= 1) &
        (u >= 0) & (u <= 1)
    )

    for index, tt in zip(jj[hit], t[hit]):
        point = A[i] + tt*r

        intersections.append(
            (i, int(index), point)
        )

print()
print("PROVERA SAMOPRESEKA")
print("-" * 42)

print("Broj segmenata:", len(A))
print("Broj pronadjenih preseka:",
      len(intersections))

for i, j, point in intersections[:5]:
    print(
        f"Presek {i}-{j}: "
        f"X={point[0]:.6f}, "
        f"Y={point[1]:.6f}"
    )

print(
    "Nema detektovanih samopreseka:",
    len(intersections) == 0
)
# MINIMALNO RASTOJANJE IZMEDJU UDALJENIH DELOVA KRIVE

points = test_path

# Stvarna duzina duz uzorkovane krive
steps = np.linalg.norm(
    np.diff(points, axis=0),
    axis=1
)

arc = np.r_[0.0, np.cumsum(steps)]

min_arc_separation = 15.0

best_distance = np.inf
best_i = None
best_j = None

pairs_under_5 = 0
pairs_under_8 = 0

# Racunanje u blokovima, bez velike matrice u memoriji
block_size = 200

for start in range(0, len(points), block_size):

    end = min(start + block_size, len(points))

    delta = (
        points[start:end, None, :]
        - points[None, :, :]
    )

    distances = np.linalg.norm(delta, axis=2)

    arc_difference = np.abs(
        arc[start:end, None]
        - arc[None, :]
    )

    valid = arc_difference >= min_arc_separation

    # Svaki par brojimo samo jednom
    indices_i = np.arange(start, end)[:, None]
    indices_j = np.arange(len(points))[None, :]

    valid &= indices_j > indices_i

    pairs_under_5 += np.count_nonzero(
        valid & (distances < 5.0)
    )

    pairs_under_8 += np.count_nonzero(
        valid & (distances < 8.0)
    )

    distances[~valid] = np.inf

    index = np.unravel_index(
        np.argmin(distances),
        distances.shape
    )

    d = distances[index]

    if d < best_distance:
        best_distance = d
        best_i = start + index[0]
        best_j = index[1]

print()
print("RASTOJANJE IZMEDJU KRAKOVA")
print("-" * 46)

print("Ukupna duzina krive:",
      round(arc[-1], 6), "m")

print("Iskljucena duzina duz putanje:",
      min_arc_separation, "m")

if best_i is not None:

    print("Najmanje rastojanje:",
          round(best_distance, 6), "m")

    print("Tacka A - s:",
          round(test_s[best_i], 6))

    print("Tacka B - s:",
          round(test_s[best_j], 6))

    print("Razmak duz krive:",
          round(arc[best_j]-arc[best_i], 6), "m")

else:
    print("Nema parova sa zadatim razmakom.")

print("Parova blizih od 5 m:", pairs_under_5)
print("Parova blizih od 8 m:", pairs_under_8)
# PROVERA ULAZA I IZLAZA IZ SERPENTINE

C = curve40(x_mm)

def angle_between(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    return np.degrees(np.arctan2(
        a[0]*b[1] - a[1]*b[0],
        np.dot(a, b)
    ))

# Pravci susednih GPX segmenata
before = unit(p[487], p[488])
after = unit(p[493], p[494])

# Tangente rekonstruisane krive
t_entry = C(s40[0], 1)
t_exit = C(s40[-1], 1)

# Zakrivljenost na spojevima
k_entry = curvature_at(s40[0])
k_exit = curvature_at(s40[-1])

print()
print("KONTINUITET NA SPOJEVIMA")
print("-" * 46)

print("ULAZ P488")
print("Razlika pravaca:",
      round(angle_between(before, t_entry), 6),
      "stepeni")
print("Zakrivljenost:",
      round(k_entry, 9), "1/m")
print("Radijus:",
      round(1/abs(k_entry), 6)
      if abs(k_entry) > 1e-12 else "beskonacan",
      "m")

print()
print("IZLAZ P493")
print("Razlika pravaca:",
      round(angle_between(t_exit, after), 6),
      "stepeni")
print("Zakrivljenost:",
      round(k_exit, 9), "1/m")
print("Radijus:",
      round(1/abs(k_exit), 6)
      if abs(k_exit) > 1e-12 else "beskonacan",
      "m")

print()
print("BRZINA PARAMETRIZACIJE NA SPOJEVIMA")
print("Ulaz:", round(np.linalg.norm(t_entry), 6))
print("Izlaz:", round(np.linalg.norm(t_exit), 6))
# TEST NOVE IZLAZNE TANGENTE
# Bez nove optimizacije i bez izmene datoteka

from scipy.interpolate import CubicSpline

# Postojece optimizovane kontrolne tacke
pts = points40.copy()
pts[1:6] += x_mm.reshape(5, 2)

# Pravac narednog GPX segmenta
new_exit = unit(p[493], p[494])

# Nova kriva sa ispravljenim izlaznim pravcem
C_new = CubicSpline(
    s40,
    pts,
    axis=0,
    bc_type=((1, entry), (1, new_exit))
)

# Gusta numericka provera
d1 = C_new(dense7, 1)
d2 = C_new(dense7, 2)

speed_new = np.linalg.norm(d1, axis=1)

cross_new = (
    d1[:, 0]*d2[:, 1]
    - d1[:, 1]*d2[:, 0]
)

k_new = cross_new / np.maximum(speed_new, 1e-9)**3

path_new = C_new(dense7)
error_new = distance_to_gpx(path_new)

# Tangenta na izlazu
t_exit_new = C_new(s40[-1], 1)

print()
print("TEST ISPRAVLJENE IZLAZNE TANGENTE")
print("-" * 48)

print("Razlika pravaca na izlazu:",
      round(angle_between(t_exit_new, new_exit), 6),
      "stepeni")

print("Minimalni radijus:",
      round(1/np.max(np.abs(k_new)), 6), "m")

print("Maksimalno odstupanje:",
      round(error_new.max(), 6), "m")

print("Srednje odstupanje:",
      round(error_new.mean(), 6), "m")

print("Minimalna parametarska brzina:",
      round(speed_new.min(), 6))

print("Uzoraka ispod R4.5:",
      np.count_nonzero(np.abs(k_new) > 1/4.5))

print()
print("POREDJENJE SA PRETHODNOM KRIVOM")
print("Stari Rmin:",
      round(1/np.max(np.abs(k_mm)), 6), "m")

print("Novi Rmin:",
      round(1/np.max(np.abs(k_new)), 6), "m")

print("Staro max. odstupanje:",
      round(error_mm.max(), 6), "m")

print("Novo max. odstupanje:",
      round(error_new.max(), 6), "m")
print()
print("UTICAJ NOVE IZLAZNE TANGENTE")
print("-" * 66)

print(
    "Segment        Stara sred.  Nova sred.  "
    "Stari max.  Novi max."
)

for j in range(len(s)-1):
    mask = (
        (dense7 >= s[j]) &
        (dense7 <= s[j+1])
    )

    old_mean = error_mm[mask].mean()
    new_mean = error_new[mask].mean()

    old_max = error_mm[mask].max()
    new_max = error_new[mask].max()

    print(
        f"P{488+j}-P{489+j}       "
        f"{old_mean:8.3f}    "
        f"{new_mean:8.3f}    "
        f"{old_max:8.3f}    "
        f"{new_max:8.3f}"
    )

# Zakrivljenost na izlazu
v = C_new(s40[-1], 1)
a = C_new(s40[-1], 2)

cross = v[0]*a[1] - v[1]*a[0]

k_exit_new = cross / np.linalg.norm(v)**3

print()
print("ZAKRIVLJENOST NA IZLAZU P493")
print("-" * 46)

print("Zakrivljenost:",
      round(k_exit_new, 9), "1/m")

if abs(k_exit_new) > 1e-12:
    print("Radijus:",
          round(1/abs(k_exit_new), 6), "m")
else:
    print("Radijus: beskonacan")

print()
print("NAJVECA PROMENA OBLIKA KRIVE")

change = np.linalg.norm(
    path_new - path_mm,
    axis=1
)

i = int(np.argmax(change))

print("Najveca promena:",
      round(change[i], 6), "m")

print("Na parametru s:",
      round(dense7[i], 6), "m")
# OPTIMIZACIJA SA ISPRAVNOM IZLAZNOM TANGENTOM

fit_fix = np.linspace(s40[0], s40[-1], 401)
sample_fix = np.linspace(s40[0], s40[-1], 1201)

# Dodatna rezerva iznad projektnog minimuma R4.5
limit_fix = 1.0 / 4.53

def curve_fix(x):
    pts = points40.copy()
    pts[1:6] += x.reshape(5, 2)

    return CubicSpline(
        s40, pts, axis=0,
        bc_type=((1, entry), (1, new_exit))
    )

def geometry_fix(x, positions):
    C = curve_fix(x)

    v = C(positions, 1)
    a = C(positions, 2)

    speed = np.linalg.norm(v, axis=1)

    cross = v[:, 0]*a[:, 1] - v[:, 1]*a[:, 0]

    k = cross / np.maximum(speed, 1e-9)**3

    return k, speed

def objective_fix(z):
    x = z[:10]
    E = z[10]

    shifts = x.reshape(5, 2)

    original_cost = np.sum(
        shifts[[0, 1, 3, 4]]**2
    )

    auxiliary_cost = np.sum(shifts[2]**2)

    error = distance_to_gpx(
        curve_fix(x)(fit_fix)
    )

    return (
        E
        + 0.05*original_cost
        + 0.01*auxiliary_cost
        + 0.1*np.mean(error**2)
    )

def constraints_fix(z):
    x = z[:10]
    E = z[10]

    k, speed = geometry_fix(x, sample_fix)

    shifts = x.reshape(5, 2)

    original_norms = np.linalg.norm(
        shifts[[0, 1, 3, 4]], axis=1
    )

    auxiliary_norm = np.linalg.norm(shifts[2])

    error = distance_to_gpx(
        curve_fix(x)(fit_fix)
    )

    return np.r_[
        limit_fix-k,
        limit_fix+k,
        speed-0.4,
        E-error,
        2.0-original_norms,
        5.0-auxiliary_norm
    ]

# Polazimo od prethodnog minimaks resenja
start_x = x_mm.copy()

start_E = distance_to_gpx(
    curve_fix(start_x)(fit_fix)
).max() + 0.01

z0 = np.r_[start_x, start_E]

result_fix = minimize(
    objective_fix,
    z0,
    method="SLSQP",
    bounds=[(-6.0, 6.0)]*10 + [(0.0, 20.0)],
    constraints=[{
        "type": "ineq",
        "fun": constraints_fix
    }],
    options={
        "maxiter": 400,
        "ftol": 1e-9,
        "disp": False
    }
)

x_fix = result_fix.x[:10]
C_fix = curve_fix(x_fix)

k_fix, speed_fix = geometry_fix(x_fix, dense7)

path_fix = C_fix(dense7)
error_fix = distance_to_gpx(path_fix)

shifts_fix = np.linalg.norm(
    x_fix.reshape(5, 2), axis=1
)

print()
print("OPTIMIZACIJA SA ISPRAVNIM IZLAZOM")
print("-"*49)

print("SLSQP uspesan:", result_fix.success)
print("Poruka:", result_fix.message)
print("Iteracije:", result_fix.nit)

print("Rmin:",
      round(1/np.max(np.abs(k_fix)), 6), "m")

print("Maks. odstupanje:",
      round(error_fix.max(), 6), "m")

print("Srednje odstupanje:",
      round(error_fix.mean(), 6), "m")

print("Max. pomeraj originalnih:",
      round(max(shifts_fix[[0, 1, 3, 4]]), 6), "m")

print("Pomeraj pomocne:",
      round(shifts_fix[2], 6), "m")

print("Minimalna brzina:",
      round(speed_fix.min(), 6))

print("Uzoraka ispod R4.5:",
      np.count_nonzero(np.abs(k_fix) > 1/4.5))

print("Razlika pravaca na izlazu:",
      round(
          angle_between(
              C_fix(s40[-1], 1),
              new_exit
          ), 6
      ), "stepeni")

print("Najmanje ogranicenje:",
      round(np.min(constraints_fix(result_fix.x)), 9))

print()
print("ODSTUPANJE NA IZLAZNOM SEGMENTU")

mask = (
    (dense7 >= s[4]) &
    (dense7 <= s[5])
)

print("Pre optimizacije:",
      round(error_new[mask].max(), 6), "m")

print("Posle optimizacije:",
      round(error_fix[mask].max(), 6), "m")
from numpy.polynomial import Polynomial

# EKSTREMI ZAKRIVLJENOSTI NOVE KRIVE

C = C_fix

curvature_candidates = []
speed_candidates = []

for j in range(len(s40)-1):
    h = s40[j+1] - s40[j]

    # Kubni polinomi x(t), y(t) za lokalni segment
    px = Polynomial(C.c[:, j, 0][::-1])
    py = Polynomial(C.c[:, j, 1][::-1])

    vx, vy = px.deriv(), py.deriv()
    ax, ay = vx.deriv(), vy.deriv()

    # Brojilac zakrivljenosti i kvadrat brzine
    N = vx*ay - vy*ax
    S = vx*vx + vy*vy

    # Stacionarne tacke zakrivljenosti:
    # 2*N'*S - 3*N*S' = 0
    F = 2*N.deriv()*S - 3*N*S.deriv()

    def real_roots(poly):
        roots = []
        for r in poly.roots():
            if abs(r.imag) < 1e-7:
                t = float(r.real)
                if 0 <= t <= h:
                    roots.append(t)
        return roots

    local_curvature = (
        [0.0, h] + real_roots(F)
    )

    local_speed = (
        [0.0, h] + real_roots(S.deriv())
    )

    for t in local_curvature:
        curvature_candidates.append(
            (s40[j]+t, j)
        )

    for t in local_speed:
        speed_candidates.append(
            (s40[j]+t, j)
        )

def curvature_fix(t):
    v = C(t, 1)
    a = C(t, 2)

    return (
        v[0]*a[1] - v[1]*a[0]
    ) / np.linalg.norm(v)**3

radii = [
    (1/abs(curvature_fix(t)), t, j)
    for t, j in curvature_candidates
    if abs(curvature_fix(t)) > 1e-12
]

rmin_exact, tmin, segment = min(radii)

min_speed = min(
    np.linalg.norm(C(t, 1))
    for t, j in speed_candidates
)

print()
print("PROVERA NOVE OPTIMIZOVANE KRIVE")
print("-" * 48)

print("Broj kandidata zakrivljenosti:",
      len(curvature_candidates))

print("Najmanji pronadjeni radijus:",
      round(rmin_exact, 9), "m")

print("Parametar s:",
      round(tmin, 9), "m")

print("Spline segment:", segment + 1)

print("Rezerva iznad R4.5:",
      round(rmin_exact - 4.5, 9), "m")

print("Najmanja parametarska brzina:",
      round(min_speed, 9))

print("Zadovoljava R4.5:",
      rmin_exact >= 4.5)
# ZAKRIVLJENOST NA SPOJEVIMA I U NJIHOVOJ BLIZINI

C = C_fix

def signed_curvature(t):
    v = C(t, 1)
    a = C(t, 2)

    cross = v[0]*a[1] - v[1]*a[0]

    return cross / np.linalg.norm(v)**3

def radius(k):
    if abs(k) < 1e-12:
        return float("inf")
    return 1.0 / abs(k)

print()
print("ZAKRIVLJENOST NA SPOJEVIMA")
print("-" * 52)

print("ULAZ P488")
print("Pomeraj s       Zakrivljenost       Radijus")

for delta in [0.0, 0.5, 1.0, 2.0]:
    t = s40[0] + delta
    k = signed_curvature(t)

    print(
        f"{delta:6.2f}          "
        f"{k:+.9f}         "
        f"{radius(k):9.4f} m"
    )

print()
print("IZLAZ P493")
print("Pomeraj s       Zakrivljenost       Radijus")

for delta in [2.0, 1.0, 0.5, 0.0]:
    t = s40[-1] - delta
    k = signed_curvature(t)

    print(
        f"{delta:6.2f}          "
        f"{k:+.9f}         "
        f"{radius(k):9.4f} m"
    )

k_start = signed_curvature(s40[0])
k_end = signed_curvature(s40[-1])

print()
print("SPOJ SA PRAVOLINIJSKIM GPX SEGMENTIMA")
print("-" * 52)

print("Ulaz - skok zakrivljenosti:",
      round(k_start, 9), "1/m")

print("Izlaz - skok zakrivljenosti:",
      round(-k_end, 9), "1/m")

print()
print("Zakrivljenost na ulazu:",
      round(k_start, 9), "1/m")

print("Zakrivljenost na izlazu:",
      round(k_end, 9), "1/m")
# GEOMETRIJA GPX TACAKA OKO SPOJEVA

def gpx_corner(i):
    A = np.asarray(p[i-1], dtype=float)
    B = np.asarray(p[i], dtype=float)
    C = np.asarray(p[i+1], dtype=float)

    u = B-A
    v = C-B
    w = C-A

    lu = np.linalg.norm(u)
    lv = np.linalg.norm(v)
    lw = np.linalg.norm(w)

    cross = u[0]*v[1] - u[1]*v[0]
    dot = np.dot(u, v)

    angle = np.degrees(np.arctan2(cross, dot))

    if min(lu, lv, lw) < 1e-9:
        return angle, float("inf"), 0.0

    k = 2.0*cross/(lu*lv*lw)

    radius = (
        1.0/abs(k)
        if abs(k) > 1e-12
        else float("inf")
    )

    return angle, radius, k


print()
print("GPX GEOMETRIJA OKO SERPENTINE")
print("-"*58)
print("Tacka    Ugao (stepeni)    Radijus (m)    k (1/m)")

for i in range(486, 496):
    angle, radius, k = gpx_corner(i)

    print(
        f"P{i:<5} "
        f"{angle:+12.4f}       "
        f"{radius:10.4f}    "
        f"{k:+.7f}"
    )
print()
print("RAZMACI GPX TACAKA OKO SERPENTINE")
print("-" * 48)

print("Segment          Duzina (m)")

for i in range(485, 496):
    A = np.asarray(p[i], dtype=float)
    B = np.asarray(p[i+1], dtype=float)

    d = np.linalg.norm(B-A)

    print(
        f"P{i}-P{i+1}       "
        f"{d:10.4f}"
    )

print()
print("UKUPNE DUZINE SUSJEDNIH ZONA")

def gpx_length(a, b):
    return sum(
        np.linalg.norm(
            np.asarray(p[i+1], dtype=float)
            - np.asarray(p[i], dtype=float)
        )
        for i in range(a, b)
    )

print(
    "Pre ulaza P485-P488:",
    round(gpx_length(485, 488), 4), "m"
)

print(
    "Nasa kriva P488-P493 (GPX polilinija):",
    round(gpx_length(488, 493), 4), "m"
)

print(
    "Posle izlaza P493-P496:",
    round(gpx_length(493, 496), 4), "m"
)
from scipy.integrate import cumulative_trapezoid

C = C_fix

# Gusta parametrizacija postojece krive
t_grid = np.linspace(s40[0], s40[-1], 20001)

velocity = C(t_grid, 1)
speed = np.linalg.norm(velocity, axis=1)

# Stvarna duzina luka od pocetka krive
arc = np.r_[
    0.0,
    cumulative_trapezoid(speed, t_grid)
]

total_length = arc[-1]

print()
print("PROMENA PRAVCA NA SPOJEVIMA")
print("-" * 56)
print("Ukupna duzina krive:",
      round(total_length, 6), "m")

print()
print("ULAZ P488")
print("Predjeni put (m)    Promena pravca (stepeni)")

for distance in [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]:
    t = np.interp(distance, arc, t_grid)

    tangent = C(t, 1)

    angle = angle_between(entry, tangent)

    print(
        f"{distance:8.2f}            "
        f"{angle:+12.6f}"
    )

print()
print("IZLAZ P493")
print("Do izlaza (m)       Preostala promena pravca")

for distance in [5.0, 3.0, 2.0, 1.0, 0.5, 0.0]:
    t = np.interp(
        total_length-distance,
        arc,
        t_grid
    )

    tangent = C(t, 1)

    angle = angle_between(tangent, new_exit)

    print(
        f"{distance:8.2f}            "
        f"{angle:+12.6f}"
    )
from scipy.integrate import cumulative_trapezoid

print()
print("PROBNI KLOTOIDNI PRELAZI")
print("-" * 65)

def trial_transition(point, tangent, k_joint, L, incoming):
    point = np.asarray(point, dtype=float)
    tangent = np.asarray(tangent, dtype=float)

    theta0 = np.arctan2(tangent[1], tangent[0])

    if incoming:
        # s = -L ... 0, zakrivljenost 0 ... k_joint
        ss = np.linspace(-L, 0.0, 2001)
        theta = theta0 + k_joint * (
            ss + ss**2 / (2*L)
        )
    else:
        # s = 0 ... L, zakrivljenost k_joint ... 0
        ss = np.linspace(0.0, L, 2001)
        theta = theta0 + k_joint * (
            ss - ss**2 / (2*L)
        )

    directions = np.column_stack((
        np.cos(theta), np.sin(theta)
    ))

    xy = cumulative_trapezoid(
        directions, ss, axis=0, initial=0.0
    )

    if incoming:
        xy = point + xy - xy[-1]
    else:
        xy = point + xy

    # Poprecno odstupanje od GPX pravca kroz spoj
    relative = xy - point

    lateral = np.abs(
        tangent[0]*relative[:, 1]
        - tangent[1]*relative[:, 0]
    )

    heading_change = np.degrees(
        theta[-1] - theta[0]
    )

    return lateral.max(), heading_change


k_in = signed_curvature(s40[0])
k_out = signed_curvature(s40[-1])

print("ULAZ P488")
print("Duzina    Max. bocno odstupanje    Promena pravca")

for L in [5.0, 10.0, 15.0]:
    offset, angle = trial_transition(
        p[488], entry, k_in, L, True
    )

    print(
        f"{L:5.1f} m       "
        f"{offset:9.4f} m          "
        f"{angle:+9.4f} deg"
    )

print()
print("IZLAZ P493")
print("Duzina    Max. bocno odstupanje    Promena pravca")

for L in [5.0, 10.0, 15.0]:
    offset, angle = trial_transition(
        p[493], new_exit, k_out, L, False
    )

    print(
        f"{L:5.1f} m       "
        f"{offset:9.4f} m          "
        f"{angle:+9.4f} deg"
    )
from scipy.integrate import cumulative_trapezoid

print()
print("KRAJEVI PROBNIH KLOTOIDA")
print("-" * 66)

def check_transition(point, tangent, k, L, incoming):
    point = np.asarray(point, dtype=float)
    tangent = np.asarray(tangent, dtype=float)

    theta0 = np.arctan2(tangent[1], tangent[0])

    if incoming:
        ss = np.linspace(-L, 0.0, 2001)
        theta = theta0 + k*(ss + ss**2/(2*L))
    else:
        ss = np.linspace(0.0, L, 2001)
        theta = theta0 + k*(ss - ss**2/(2*L))

    directions = np.column_stack((
        np.cos(theta),
        np.sin(theta)
    ))

    xy = cumulative_trapezoid(
        directions, ss,
        axis=0,
        initial=0.0
    )

    if incoming:
        xy = point + xy - xy[-1]
        outer = xy[0]
        outer_tangent = directions[0]
    else:
        xy = point + xy
        outer = xy[-1]
        outer_tangent = directions[-1]

    relative = outer - point

    # Projekcija na pravac susednog GPX segmenta
    longitudinal = np.dot(relative, tangent)

    lateral = (
        tangent[0]*relative[1]
        - tangent[1]*relative[0]
    )

    angle = angle_between(tangent, outer_tangent)

    return longitudinal, lateral, angle


for name, point, tangent, k, incoming in [
    ("ULAZ P488", p[488], entry, k_in, True),
    ("IZLAZ P493", p[493], new_exit, k_out, False)
]:
    print()
    print(name)
    print("L (m)   Uzduzno (m)   Bocno (m)   Ugao (deg)")

    for L in [5.0, 10.0, 15.0]:
        longitudinal, lateral, angle = check_transition(
            point, tangent, k, L, incoming
        )

        print(
            f"{L:5.1f}   "
            f"{longitudinal:+11.4f}   "
            f"{lateral:+9.4f}   "
            f"{angle:+10.4f}"
        )
print()
print("PROVERA SPOJEVA KLOTOIDA SA GPX TACKAMA")
print("-" * 62)

def check_outer_connection(point, tangent, k, L, incoming):
    point = np.asarray(point, dtype=float)
    tangent = np.asarray(tangent, dtype=float)

    theta0 = np.arctan2(tangent[1], tangent[0])

    if incoming:
        ss = np.linspace(-L, 0.0, 2001)
        theta = theta0 + k*(ss + ss**2/(2*L))
    else:
        ss = np.linspace(0.0, L, 2001)
        theta = theta0 + k*(ss - ss**2/(2*L))

    directions = np.column_stack((
        np.cos(theta),
        np.sin(theta)
    ))

    xy = cumulative_trapezoid(
        directions,
        ss,
        axis=0,
        initial=0.0
    )

    if incoming:
        xy = point + xy - xy[-1]

        outer = xy[0]
        outer_tangent = directions[0]

        connection = outer - np.asarray(p[487], dtype=float)

        mismatch = angle_between(
            connection,
            outer_tangent
        )
    else:
        xy = point + xy

        outer = xy[-1]
        outer_tangent = directions[-1]

        connection = np.asarray(p[494], dtype=float) - outer

        mismatch = angle_between(
            outer_tangent,
            connection
        )

    return (
        np.linalg.norm(connection),
        mismatch
    )


print("ULAZ: P487 -> pocetak klotoide")
print("L (m)   Duzina spojnice (m)   Prelom (deg)")

for L in [5.0, 10.0, 15.0]:
    distance, mismatch = check_outer_connection(
        p[488], entry, k_in, L, True
    )

    print(
        f"{L:5.1f}        "
        f"{distance:10.4f}         "
        f"{mismatch:+10.4f}"
    )

print()
print("IZLAZ: kraj klotoide -> P494")
print("L (m)   Duzina spojnice (m)   Prelom (deg)")

for L in [5.0, 10.0, 15.0]:
    distance, mismatch = check_outer_connection(
        p[493], new_exit, k_out, L, False
    )

    print(
        f"{L:5.1f}        "
        f"{distance:10.4f}         "
        f"{mismatch:+10.4f}"
    )
print()
print("SMEROVI OKO SPOJEVA SERPENTINE")
print("-" * 56)

reference = unit(p[487], p[488])

segments = [
    ("P486-P487", 486, 487),
    ("P487-P488", 487, 488),
    ("P488-P489", 488, 489),
    ("P492-P493", 492, 493),
    ("P493-P494", 493, 494),
    ("P494-P495", 494, 495),
]

print("Segment       Ugao prema P487-P488")

for name, a, b in segments:
    direction = unit(p[a], p[b])

    angle = angle_between(reference, direction)

    print(f"{name:12s} {angle:+12.6f} deg")

print()
print("TANGENTE REKONSTRUISANE KRIVE")

t_start = C_fix(s40[0], 1)
t_end = C_fix(s40[-1], 1)

print(
    "Ulaz:",
    round(angle_between(reference, t_start), 6),
    "deg"
)

print(
    "Izlaz:",
    round(angle_between(reference, t_end), 6),
    "deg"
)

print()
print("PROMENA PRAVCA SUSJEDNIH GPX SEGMENATA")

print(
    "Pre ulaza P487:",
    round(
        angle_between(
            unit(p[486], p[487]),
            unit(p[487], p[488])
        ), 6
    ),
    "deg"
)

print(
    "Posle izlaza P494:",
    round(
        angle_between(
            unit(p[493], p[494]),
            unit(p[494], p[495])
        ), 6
    ),
    "deg"
)
print()
print("UKUPNA PROMENA PRAVCA SERPENTINE")
print("-" * 56)

C = C_fix

tt = np.linspace(s40[0], s40[-1], 20001)

v = C(tt, 1)
a = C(tt, 2)

speed = np.linalg.norm(v, axis=1)

cross = v[:, 0]*a[:, 1] - v[:, 1]*a[:, 0]

k = cross / speed**3

# Kontinuirani ugao tangente, bez skoka na +/-180 stepeni
heading = np.unwrap(
    np.arctan2(v[:, 1], v[:, 0])
)

relative_heading = np.degrees(
    heading - heading[0]
)

# Promena ugla po malim intervalima
dtheta = np.diff(heading)

left_turn = np.degrees(
    np.sum(np.maximum(dtheta, 0.0))
)

right_turn = np.degrees(
    np.sum(np.minimum(dtheta, 0.0))
)

total_turn = np.degrees(
    heading[-1] - heading[0]
)

print("Ukupno skretanje ulevo:",
      round(left_turn, 6), "deg")

print("Ukupno skretanje udesno:",
      round(right_turn, 6), "deg")

print("Neto promena pravca:",
      round(total_turn, 6), "deg")

print("Najmanji relativni ugao:",
      round(relative_heading.min(), 6), "deg")

print("Najveci relativni ugao:",
      round(relative_heading.max(), 6), "deg")

print()
print("PROMENA PRAVCA PO SPLINE SEGMENTIMA")
print("-" * 56)

for j in range(len(s40)-1):

    h0 = np.interp(s40[j], tt, heading)
    h1 = np.interp(s40[j+1], tt, heading)

    change = np.degrees(h1-h0)

    print(
        f"Segment {j+1}: "
        f"{change:+10.6f} deg"
    )

print()
print("UZORCI NEGATIVNE ZAKRIVLJENOSTI")

negative = k < -1e-8

print("Broj:",
      np.count_nonzero(negative))

print("Procenat:",
      round(100*np.mean(negative), 4), "%")

print("Najnegativnija zakrivljenost:",
      round(k.min(), 9), "1/m")
from scipy.integrate import cumulative_trapezoid

print()
print("ANALIZA DESNIH KRIVINA")
print("-" * 60)

C = C_fix

tt = np.linspace(s40[0], s40[-1], 30001)

v = C(tt, 1)
a = C(tt, 2)

speed = np.linalg.norm(v, axis=1)

cross = v[:, 0]*a[:, 1] - v[:, 1]*a[:, 0]
k = cross / speed**3

arc = cumulative_trapezoid(
    speed, tt, initial=0.0
)

heading = np.unwrap(
    np.arctan2(v[:, 1], v[:, 0])
)

# Pronalazimo nule zakrivljenosti interpolacijom
# i formiramo intervale sa negativnim znakom.

zero_crossings = []

for i in range(len(tt)-1):
    if k[i] * k[i+1] < 0:
        fraction = -k[i] / (k[i+1]-k[i])

        root = tt[i] + fraction*(tt[i+1]-tt[i])
        zero_crossings.append(root)

boundaries = [
    tt[0],
    *zero_crossings,
    tt[-1]
]

def arc_at(t):
    return np.interp(t, tt, arc)

def heading_at(t):
    velocity = C(t, 1)
    raw = np.arctan2(velocity[1], velocity[0])

    # Biramo odgovarajucu granu kontinualnog ugla
    reference = np.interp(t, tt, heading)

    return raw + 2*np.pi*round(
        (reference-raw)/(2*np.pi)
    )

total_right_length = 0.0

print("Broj promena znaka zakrivljenosti:",
      len(zero_crossings))

print()

counter = 0

for start, end in zip(boundaries[:-1], boundaries[1:]):

    middle = (start+end)/2

    vel = C(middle, 1)
    acc = C(middle, 2)

    cross_mid = (
        vel[0]*acc[1] - vel[1]*acc[0]
    )

    if cross_mid >= 0:
        continue

    counter += 1

    length = arc_at(end) - arc_at(start)

    angle = np.degrees(
        heading_at(end)-heading_at(start)
    )

    mask = (tt >= start) & (tt <= end)
    k_min = k[mask].min()

    radius_min = 1.0/abs(k_min)

    total_right_length += length

    print(f"DESNA KRIVINA {counter}")
    print("Parametar s:",
          round(start, 4), "do",
          round(end, 4), "m")

    print("Duzina luka:",
          round(length, 4), "m")

    print("Promena pravca:",
          round(angle, 4), "deg")

    print("Najmanji radijus:",
          round(radius_min, 4), "m")

    print()

print("-" * 60)

print("Ukupna duzina desnih krivina:",
      round(total_right_length, 4), "m")

print("Procenat duzine putanje:",
      round(
          100*total_right_length/arc[-1], 4
      ), "%")
print()
print("POLOZAJ DESNE KRIVINE U ODNOSU NA GPX")
print("-" * 60)

C = C_fix

def nearest_gpx_segment(point):
    best_distance = float("inf")
    best_segment = None

    for j in range(len(local)-1):
        A = local[j]
        B = local[j+1]

        AB = B-A

        fraction = np.clip(
            np.dot(point-A, AB) / np.dot(AB, AB),
            0.0, 1.0
        )

        projection = A + fraction*AB

        distance = np.linalg.norm(point-projection)

        if distance < best_distance:
            best_distance = distance
            best_segment = j

    return best_segment, best_distance


# Koristimo dve ranije pronadjene nule zakrivljenosti
t_start = zero_crossings[0]
t_end = zero_crossings[1]

locations = [
    ("POCETAK", t_start),
    ("SREDINA", (t_start+t_end)/2),
    ("KRAJ", t_end)
]

for name, t in locations:
    point = C(t)

    segment, distance = nearest_gpx_segment(point)

    heading_deg = np.degrees(
        heading_at(t) - heading_at(s40[0])
    )

    print()
    print(name)

    print("Parametar s:",
          round(t, 6), "m")

    print("Predjeni put:",
          round(arc_at(t), 6), "m")

    print("Relativni pravac:",
          round(heading_deg, 6), "deg")

    print(
        "Najblizi GPX segment:",
        f"P{488+segment}-P{489+segment}"
    )

    print("Odstupanje:",
          round(distance, 6), "m")

print()
print("UKUPNA DESNA PROMENA PRAVCA")

print(
    round(
        np.degrees(
            heading_at(t_end)-heading_at(t_start)
        ), 6
    ),
    "deg"
)
print()
print("POREDJENJE PRAVACA SPLINE-A I GPX-A")
print("-" * 65)

reference = unit(p[487], p[488])

# Originalne GPX tacke i odgovarajuci
# parametri u prosirenom spline-u
knots = [
    (490, s40[2]),
    (491, s40[4]),
    (492, s40[5]),
    (493, s40[6])
]

print("Tacka    Spline (deg)    GPX pre (deg)    GPX posle (deg)")

for index, t in knots:
    spline_direction = C_fix(t, 1)

    previous_direction = unit(
        p[index-1], p[index]
    )

    next_direction = unit(
        p[index], p[index+1]
    )

    spline_angle = angle_between(
        reference, spline_direction
    )

    previous_angle = angle_between(
        reference, previous_direction
    )

    next_angle = angle_between(
        reference, next_direction
    )

    print(
        f"P{index}      "
        f"{spline_angle:+11.4f}     "
        f"{previous_angle:+11.4f}     "
        f"{next_angle:+11.4f}"
    )

print()
print("PROMENA PRAVCA GPX POLILINIJE")
print("-" * 48)

gpx_turn = 0.0

for index in [491, 492]:
    before = unit(p[index-1], p[index])
    after = unit(p[index], p[index+1])

    change = angle_between(before, after)
    gpx_turn += change

    print(
        f"P{index}: {change:+.6f} deg"
    )

print(
    "Ukupno GPX:",
    round(gpx_turn, 6), "deg"
)

print()
print("PROMENA PRAVCA SPLINE-A")

t490 = s40[2]
t493 = s40[6]

spline_turn = np.degrees(
    heading_at(t493) - heading_at(t490)
)

print(
    "P490 do P493:",
    round(spline_turn, 6), "deg"
)
print()
print("KONTROLA SMERA I POMERAJA TACKAKA")
print("-" * 65)

# GPX indeks -> indeks parametra u s40
knots = [
    (490, 2),
    (491, 4),
    (492, 5),
    (493, 6)
]

print("TACKA     Pomeraj (m)    Pravac (deg)    k (1/m)")

for gpx_index, knot_index in knots:
    t = s40[knot_index]

    point = C_fix(t) + origin
    original_point = np.asarray(
        p[gpx_index], dtype=float
    )

    displacement = np.linalg.norm(
        point - original_point
    )

    direction = np.degrees(
        heading_at(t) - heading_at(s40[0])
    )

    curvature = signed_curvature(t)

    print(
        f"P{gpx_index}      "
        f"{displacement:9.4f}       "
        f"{direction:10.4f}     "
        f"{curvature:+.7f}"
    )

print()
print("PROMENA PRAVCA IZMEDJU KONTROLNIH TACAKA")
print("-" * 65)

for (i0, j0), (i1, j1) in zip(knots[:-1], knots[1:]):
    t0 = s40[j0]
    t1 = s40[j1]

    change = np.degrees(
        heading_at(t1) - heading_at(t0)
    )

    print(
        f"P{i0}-P{i1}: "
        f"{change:+.6f} deg"
    )

print()
print("GRANICE DESNE KRIVINE")

for name, t in [
    ("Pocetak", zero_crossings[0]),
    ("Kraj", zero_crossings[1])
]:
    direction = np.degrees(
        heading_at(t) - heading_at(s40[0])
    )

    print(
        name,
        "s =", round(t, 4),
        "pravac =", round(direction, 4)
    )
print()
print("POREKLO DESNE KRIVINE")
print("-" * 60)

# Pocetni spline bez pomeranja kontrolnih tacaka
C_raw = CubicSpline(
    s40,
    points40,
    axis=0,
    bc_type=((1, entry), (1, new_exit))
)

def analyze_turns(C):
    t = np.linspace(s40[0], s40[-1], 20001)

    v = C(t, 1)
    a = C(t, 2)

    speed = np.linalg.norm(v, axis=1)

    cross = v[:, 0]*a[:, 1] - v[:, 1]*a[:, 0]
    k = cross / speed**3

    heading = np.unwrap(
        np.arctan2(v[:, 1], v[:, 0])
    )

    dtheta = np.diff(heading)

    left = np.degrees(
        np.maximum(dtheta, 0).sum()
    )

    right = np.degrees(
        np.minimum(dtheta, 0).sum()
    )

    # Priblizna duzina oblasti desnog skretanja
    dt = np.diff(t)
    right_length = np.sum(
        0.5 * (speed[:-1] + speed[1:]) * dt
        * (k[:-1] + k[1:] < 0)
    )

    error = distance_to_gpx(C(t))

    return {
        "left": left,
        "right": right,
        "net": left + right,
        "right_length": right_length,
        "rmin": 1 / np.max(np.abs(k)),
        "max_error": error.max(),
        "mean_error": error.mean()
    }


raw = analyze_turns(C_raw)
optimized = analyze_turns(C_fix)

print(
    f"{'Parametar':27s}"
    f"{'Pocetni':>13s}"
    f"{'Optimizovani':>16s}"
)

for key, label in [
    ("left", "Skretanje ulevo (deg)"),
    ("right", "Skretanje udesno (deg)"),
    ("net", "Neto skretanje (deg)"),
    ("right_length", "Duzina desne krivine (m)"),
    ("rmin", "Minimalni radijus (m)"),
    ("max_error", "Maks. odstupanje (m)"),
    ("mean_error", "Srednje odstupanje (m)")
]:
    print(
        f"{label:27s}"
        f"{raw[key]:13.4f}"
        f"{optimized[key]:16.4f}"
    )

print()
print("PROMENA DESNOG SKRETANJA OPTIMIZACIJOM")

print(
    round(
        optimized["right"] - raw["right"], 6
    ),
    "stepeni"
)
print()
print("PROVERA PRETERANOG SKRETANJA SPLINE-A")
print("-" * 65)

for index, knot in [(491, 4), (492, 5)]:

    before = unit(p[index-1], p[index])
    after = unit(p[index], p[index+1])

    # Simetrala susednih GPX pravaca
    bisector = before + after
    bisector /= np.linalg.norm(bisector)

    t = s40[knot]

    raw_tangent = C_raw(t, 1)
    optimized_tangent = C_fix(t, 1)

    raw_error = angle_between(
        bisector, raw_tangent
    )

    optimized_error = angle_between(
        bisector, optimized_tangent
    )

    gpx_change = angle_between(
        before, after
    )

    print()
    print(f"TACKA P{index}")
    print("-" * 42)

    print(
        "Promena pravca GPX:",
        round(gpx_change, 6), "deg"
    )

    print(
        "Pocetni spline - odstupanje:",
        round(raw_error, 6), "deg"
    )

    print(
        "Optimizovani spline - odstupanje:",
        round(optimized_error, 6), "deg"
    )

    print(
        "Promena usled optimizacije:",
        round(optimized_error - raw_error, 6),
        "deg"
    )
print()
print("OPTIMIZACIJA SA KONTROLOM TANGENTI")
print("-" * 58)

# GPX simetrale u P491 i P492
targets = []

for index, knot in [(491, 4), (492, 5)]:

    before = unit(p[index-1], p[index])
    after = unit(p[index], p[index+1])

    bisector = before + after
    bisector /= np.linalg.norm(bisector)

    targets.append((knot, bisector))


def tangent_errors(x):
    C = curve_fix(x)

    errors = []

    for knot, target in targets:
        tangent = C(s40[knot], 1)

        errors.append(
            angle_between(target, tangent)
        )

    return np.array(errors)


# Blaga kazna za ugaona odstupanja
weight = 0.003

def objective_smooth(z):
    x = z[:10]

    errors = tangent_errors(x)

    return (
        objective_fix(z)
        + weight * np.sum(errors**2)
    )


result_smooth = minimize(
    objective_smooth,
    result_fix.x.copy(),
    method="SLSQP",
    bounds=[(-6.0, 6.0)]*10 + [(0.0, 20.0)],
    constraints=[{
        "type": "ineq",
        "fun": constraints_fix
    }],
    options={
        "maxiter": 400,
        "ftol": 1e-9,
        "disp": False
    }
)

x_smooth = result_smooth.x[:10]
C_smooth = curve_fix(x_smooth)

k_smooth, speed_smooth = geometry_fix(
    x_smooth, dense7
)

error_smooth = distance_to_gpx(
    C_smooth(dense7)
)

old_angles = tangent_errors(x_fix)
new_angles = tangent_errors(x_smooth)

print("SLSQP uspesan:", result_smooth.success)
print("Poruka:", result_smooth.message)
print("Iteracije:", result_smooth.nit)

print()
print("POREDJENJE TANGENTI")

print(
    "P491:",
    round(old_angles[0], 6),
    "->",
    round(new_angles[0], 6),
    "deg"
)

print(
    "P492:",
    round(old_angles[1], 6),
    "->",
    round(new_angles[1], 6),
    "deg"
)

print()
print("GEOMETRIJA")

print(
    "Rmin:",
    round(1/np.max(np.abs(k_smooth)), 6),
    "m"
)

print(
    "Maks. odstupanje:",
    round(error_smooth.max(), 6),
    "m"
)

print(
    "Srednje odstupanje:",
    round(error_smooth.mean(), 6),
    "m"
)

print(
    "Minimalna brzina:",
    round(speed_smooth.min(), 6)
)

print(
    "Uzoraka ispod R4.5:",
    np.count_nonzero(
        np.abs(k_smooth) > 1/4.5
    )
)

print(
    "Najmanje ogranicenje:",
    round(
        np.min(constraints_fix(result_smooth.x)),
        9
    )
)

print()
print("POMERAJI KONTROLNIH TACAKA")

shifts = np.linalg.norm(
    x_smooth.reshape(5, 2),
    axis=1
)

print(
    "Maks. originalnih:",
    round(max(shifts[[0, 1, 3, 4]]), 6),
    "m"
)

print(
    "Pomocna:",
    round(shifts[2], 6),
    "m"
)
from scipy.integrate import cumulative_trapezoid

print()
print("POREDJENJE DESNE KRIVINE")
print("-" * 62)

def analyze_candidate(C):
    t = np.linspace(s40[0], s40[-1], 30001)

    v = C(t, 1)
    a = C(t, 2)

    speed = np.linalg.norm(v, axis=1)

    cross = v[:, 0]*a[:, 1] - v[:, 1]*a[:, 0]
    k = cross / speed**3

    heading = np.unwrap(
        np.arctan2(v[:, 1], v[:, 0])
    )

    dtheta = np.diff(heading)

    right_turn = np.degrees(
        np.minimum(dtheta, 0.0).sum()
    )

    left_turn = np.degrees(
        np.maximum(dtheta, 0.0).sum()
    )

    # Duzina intervala negativne zakrivljenosti
    ds = 0.5 * (speed[:-1] + speed[1:]) * np.diff(t)

    negative = (k[:-1] + k[1:]) < 0

    right_length = ds[negative].sum()

    error = distance_to_gpx(C(t))

    return {
        "right": right_turn,
        "left": left_turn,
        "right_length": right_length,
        "rmin": 1.0 / np.max(np.abs(k)),
        "error": error,
        "t": t
    }


old = analyze_candidate(C_fix)
new = analyze_candidate(C_smooth)

print(
    f"{'Parametar':28s}"
    f"{'C_fix':>12s}"
    f"{'C_smooth':>12s}"
)

for key, label in [
    ("right", "Desno skretanje (deg)"),
    ("left", "Levo skretanje (deg)"),
    ("right_length", "Duzina desne krivine (m)"),
    ("rmin", "Minimalni radijus (m)")
]:
    print(
        f"{label:28s}"
        f"{old[key]:12.4f}"
        f"{new[key]:12.4f}"
    )

print()
print("ODSTUPANJA PO GPX SEGMENTIMA")
print("-" * 62)

print("Segment        C_fix max.     C_smooth max.")

for j in range(len(s)-1):

    mask = (
        (old["t"] >= s[j]) &
        (old["t"] <= s[j+1])
    )

    old_max = old["error"][mask].max()
    new_max = new["error"][mask].max()

    print(
        f"P{488+j}-P{489+j}       "
        f"{old_max:10.4f}       "
        f"{new_max:10.4f}"
    )

print()
print("PROMENA DESNOG SKRETANJA")

print(
    round(new["right"] - old["right"], 6),
    "stepeni"
)
from scipy.optimize import minimize_scalar
from scipy.signal import find_peaks

print()
print("PRECIZNA PROVERA RADIJUSA C_smooth")
print("-" * 60)

def curvature_exact(t):
    v = C_smooth(t, 1)
    a = C_smooth(t, 2)

    speed = np.linalg.norm(v)

    cross = v[0]*a[1] - v[1]*a[0]

    return cross / speed**3


candidates = []

for j in range(len(s40)-1):

    lo = s40[j]
    hi = s40[j+1]

    ts = np.linspace(lo, hi, 2001)

    values = np.array([
        abs(curvature_exact(t)) for t in ts
    ])

    # Granice segmenta
    candidates.append((values[0], lo, j))
    candidates.append((values[-1], hi, j))

    # Lokalni maksimumi unutar segmenta
    peaks, _ = find_peaks(values)

    for i in peaks:
        result = minimize_scalar(
            lambda t: -abs(curvature_exact(t)),
            bounds=(ts[i-1], ts[i+1]),
            method="bounded",
            options={"xatol": 1e-12}
        )

        candidates.append((
            -result.fun,
            result.x,
            j
        ))


max_k, critical_t, segment = max(candidates)

r_min = 1.0 / max_k

print("Najveca |zakrivljenost|:", round(max_k, 10))
print("Minimalni radijus:", round(r_min, 9), "m")
print("Parametar s:", round(critical_t, 9))
print("Segment spline-a:", segment + 1)
print("Rezerva iznad R4.5:", round(
    1000 * (r_min - 4.5), 6
), "mm")

print()
print(
    "R >= 4.5 m:",
    "DA" if r_min >= 4.5 else "NE"
)
from numpy.polynomial import Polynomial as Poly

print()
print("POLINOMSKA PROVERA EKSTREMA ZAKRIVLJENOSTI")
print("-" * 65)

extrema = []

for j in range(len(s40) - 1):

    # Koeficijenti kubnog spline-a u segmentu j
    cx = C_smooth.c[:, j, 0]
    cy = C_smooth.c[:, j, 1]

    x = Poly(cx[::-1])
    y = Poly(cy[::-1])

    vx = x.deriv()
    vy = y.deriv()

    ax = vx.deriv()
    ay = vy.deriv()

    # Brojilac zakrivljenosti
    N = vx * ay - vy * ax

    # Kvadrat brzine
    Q = vx * vx + vy * vy

    # Brojilac izvoda zakrivljenosti
    F = N.deriv() * Q - 1.5 * N * Q.deriv()

    length = s40[j + 1] - s40[j]

    # Granice segmenta
    candidates = [0.0, length]

    # Svi realni koreni unutar segmenta
    for root in F.roots():
        if abs(root.imag) < 1e-8:
            u = float(root.real)

            if 0.0 < u < length:
                candidates.append(u)

    for u in candidates:
        t = s40[j] + u
        k = abs(curvature_exact(t))

        extrema.append((k, t, j + 1))


max_k, critical_t, segment = max(extrema)

R = 1.0 / max_k

print("Broj proverenih kandidata:", len(extrema))
print("Maksimalna |k|:", round(max_k, 12))
print("Minimalni radijus:", round(R, 9), "m")
print("Kriticni parametar:", round(critical_t, 9))
print("Segment:", segment)

print()
print("Rezerva:", round(1000 * (R - 4.5), 6), "mm")
print("R >= 4.5 m:", R >= 4.5)
from numpy.polynomial import Polynomial as Poly

minimum = (float("inf"), None, None)

for j in range(len(s40) - 1):
    x = Poly(C_smooth.c[:, j, 0][::-1])
    y = Poly(C_smooth.c[:, j, 1][::-1])

    Q = x.deriv()**2 + y.deriv()**2

    L = s40[j + 1] - s40[j]
    candidates = [0.0, L]

    for root in Q.deriv().roots():
        if abs(root.imag) < 1e-8:
            u = float(root.real)
            if 0 < u < L:
                candidates.append(u)

    for u in candidates:
        q = float(Q(u))
        if q < minimum[0]:
            minimum = (q, s40[j] + u, j + 1)

q_min, t_min, segment = minimum

print("Minimalni kvadrat brzine:", q_min)
print("Minimalna brzina:", np.sqrt(max(q_min, 0)))
print("Parametar:", t_min)
print("Segment:", segment)
print("Spline regularan:", q_min > 0)
print()
print("NAJVECE ODSTUPANJE C_smooth OD GPX-a")
print("-" * 60)

ts = np.linspace(s40[0], s40[-1], 30001)
curve_points = C_smooth(ts)

errors = distance_to_gpx(curve_points)

i = np.argmax(errors)

point = curve_points[i]
t = ts[i]

best = None

for j in range(len(local) - 1):
    A = local[j]
    B = local[j + 1]

    AB = B - A

    u = np.clip(
        np.dot(point - A, AB) / np.dot(AB, AB),
        0.0, 1.0
    )

    projection = A + u * AB

    distance = np.linalg.norm(
        point - projection
    )

    if best is None or distance < best[0]:
        cross = (
            AB[0] * (point[1] - A[1])
            - AB[1] * (point[0] - A[0])
        )

        best = (distance, j, u, cross, projection)

distance, j, u, cross, projection = best

print("Maksimalno odstupanje:", round(distance, 6), "m")
print("Parametar spline-a:", round(t, 6))

print(f"Najblizi GPX segment: P{488+j}-P{489+j}")

print("Polozaj na GPX segmentu:", round(u, 6))

print(
    "Strana:",
    "LEVO" if cross > 0 else
    "DESNO" if cross < 0 else "NA LINIJI"
)

print("Tacka spline-a:", point + origin)
print("Najbliza tacka GPX-a:", projection + origin)
import matplotlib.pyplot as plt

t = np.linspace(s40[0], s40[-1], 2000)

gpx = local + origin
fix = C_fix(t) + origin
smooth = C_smooth(t) + origin

critical = C_smooth(18.769545) + origin

fig, ax = plt.subplots(figsize=(11, 9))

ax.plot(
    gpx[:, 0], gpx[:, 1],
    "ko--", label="Originalni GPX",
    linewidth=1.5
)

ax.plot(
    fix[:, 0], fix[:, 1],
    color="blue", label="C_fix",
    linewidth=2
)

ax.plot(
    smooth[:, 0], smooth[:, 1],
    color="green", label="C_smooth",
    linewidth=2
)

for j, point in enumerate(gpx):
    ax.annotate(
        f"P{488+j}",
        point,
        xytext=(5, 6),
        textcoords="offset points"
    )

ax.plot(
    critical[0], critical[1],
    "ro", markersize=9,
    label="Maks. odstupanje"
)

nearest = np.array([
    -10074.00973656,
    -9736.48685175
])

ax.plot(
    [critical[0], nearest[0]],
    [critical[1], nearest[1]],
    "r-", linewidth=2
)

ax.set_aspect("equal")
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_title("Stelvio P488-P493: GPX i rekonstruisane krive")

#plt.show()
'''
np.savez(
    "stelvio_hairpin_488_493.npz",
    s40=s40,
    points40=points40,
    x_smooth=x_smooth,
    entry=entry,
    new_exit=new_exit
)'''
data = np.load("stelvio_hairpin_488_493.npz")

print("Sacuvano:", data.files)
from scipy.interpolate import CubicSpline

data = np.load("stelvio_hairpin_488_493.npz")

saved_points = data["points40"].copy()
saved_points[1:6] += data["x_smooth"].reshape(5, 2)

C_loaded = CubicSpline(
    data["s40"],
    saved_points,
    axis=0,
    bc_type=(
        (1, data["entry"]),
        (1, data["new_exit"])
    )
)

t = np.linspace(data["s40"][0], data["s40"][-1], 1001)

difference = np.max(
    np.linalg.norm(C_loaded(t) - C_smooth(t), axis=1)
)

print("Maksimalna razlika:", difference, "m")
print("Identicne krive:", np.allclose(C_loaded(t), C_smooth(t)))
filename = "stelvio_hairpin_488_493.npz"

with np.load(filename) as data:
    saved = {key: data[key] for key in data.files}

saved["origin"] = origin.copy()

np.savez(filename, **saved)

print("Sacuvano i poreklo koordinata!")
'@ | python -