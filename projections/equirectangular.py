from math import pi
from typing import Optional
from projections.base import Projection
from projections.utils import Point, Direction, Angles


class EquirectangularProjection(Projection):

    @staticmethod
    def aspect_ratio() -> float:
        return 2.0

    def to_direction(self, point: Point) -> Optional[Direction]:
        return Angles(
            azimuth=point.x * 2.0 * pi,
            altitude=(point.y - 0.5) * pi,
        )

    def to_point(self, direction: Direction) -> Optional[Point]:
        angles = direction.as_angles()
        return Point(
            x=angles.azimuth / (2.0 * pi),
            y=(angles.altitude / pi) + 0.5,
        )
