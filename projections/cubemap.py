from typing import Optional
from projections.base import Projection, Angles, Point


class CubemapProjection(Projection):
    def to_angles(self, point: Point) -> Optional[Angles]:
        return Angles()

    def to_point(self, angles: Angles) -> Optional[Point]:
        return Point()
