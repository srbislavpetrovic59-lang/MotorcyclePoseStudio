
import numpy as np
from scipy.integrate import cumulative_trapezoid


class ArcLengthPath:
    def __init__(self, curve, samples=20001):
        self.curve = curve

        if isinstance(curve, np.ndarray):
            self.points = np.asarray(curve, dtype=float)

            if self.points.ndim != 2 or self.points.shape[1] != 2:
                raise ValueError("Putanja mora imati oblik (N, 2)")

            self.parameters = None
            segments = np.linalg.norm(
                np.diff(self.points, axis=0), axis=1
            )
            self.distances = np.concatenate(
                ([0.0], np.cumsum(segments))
            )

        else:
            self.points = None

            if hasattr(curve, "k"):
                start = curve.t[curve.k]
                end = curve.t[-curve.k - 1]
            else:
                start = curve.x[0]
                end = curve.x[-1]

            self.parameters = np.linspace(
                start, end, samples
            )

            derivative = curve.derivative(1)(
                self.parameters
            )
            speed = np.linalg.norm(derivative, axis=1)

            self.distances = np.concatenate((
                [0.0],
                cumulative_trapezoid(
                    speed, self.parameters
                )
            ))

        if (
            not np.all(np.isfinite(self.distances))
            or not np.all(np.diff(self.distances) > 0)
        ):
            raise ValueError(
                "Putanja nema strogo rastucu duzinu"
            )

        self.length = float(self.distances[-1])

    def point_at(self, distance):
        distance = float(distance)

        if not 0.0 <= distance <= self.length:
            raise ValueError(
                "Udaljenost je van opsega putanje"
            )

        if self.points is not None:
            x = np.interp(
                distance, self.distances,
                self.points[:, 0]
            )
            y = np.interp(
                distance, self.distances,
                self.points[:, 1]
            )
            return np.array([x, y])

        parameter = np.interp(
            distance,
            self.distances,
            self.parameters
        )
        return np.asarray(self.curve(parameter))



    def heading_at(self, distance):
        distance = float(distance)

        if not 0.0 <= distance <= self.length:
            raise ValueError(
                "Udaljenost je van opsega putanje"
            )

        if self.points is None:
            parameter = np.interp(
                distance,
                self.distances,
                self.parameters
            )

            direction = self.curve.derivative(1)(
                parameter
            )
        else:
            h = min(0.01, self.length / 4.0)

            s0 = max(0.0, distance - h)
            s1 = min(self.length, distance + h)

            direction = (
                self.point_at(s1) - self.point_at(s0)
            )

        if np.linalg.norm(direction) <= 1e-12:
            raise ValueError(
                "Pravac tangente nije definisan"
            )

        return float(np.degrees(
            np.arctan2(direction[1], direction[0])
        ))



    def curvature_at(self, distance):
        distance = float(distance)

        if not 0.0 <= distance <= self.length:
            raise ValueError(
                "Udaljenost je van opsega putanje"
            )

        if self.points is not None:
            raise NotImplementedError(
                "Zakrivljenost diskretne putanje "
                "jos nije implementirana"
            )

        parameter = np.interp(
            distance,
            self.distances,
            self.parameters
        )

        d1 = self.curve.derivative(1)(parameter)
        d2 = self.curve.derivative(2)(parameter)

        speed = np.linalg.norm(d1)

        if speed <= 1e-12:
            raise ValueError(
                "Zakrivljenost nije definisana"
            )

        cross = (
            d1[0] * d2[1]
            - d1[1] * d2[0]
        )

        return float(cross / speed**3)
