from typing import Optional
from projections.utils import Point, Direction


class Projection:
    def to_direction(self, point: Point) -> Optional[Direction]:
        raise NotImplementedError()

    def to_point(self, direction: Direction) -> Optional[Point]:
        raise NotImplementedError
