from math import pi
from typing import Optional
from projections.base import Projection, Angles, Point


class EquirectangularProjection(Projection):
    def to_angles(self, point: Point) -> Optional[Angles]:
        return Angles(
            azimuth=point.x * 2.0 * pi,
            altitude=(point.y - 0.5) * pi,
        )

    def to_point(self, angles: Angles) -> Optional[Point]:
        return Point(
            x=angles.azimuth / (2.0 * pi),
            y=(angles.altitude / pi) + 0.5,
        )
