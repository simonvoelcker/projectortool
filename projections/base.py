from typing import Optional
from projections.utils import Point, Direction


class Projection:

    @staticmethod
    def aspect_ratio() -> float:
        # Ideal aspect ratio of an image using this projection
        raise NotImplementedError

    def to_direction(self, point: Point) -> Optional[Direction]:
        raise NotImplementedError()

    def to_point(self, direction: Direction) -> Optional[Point]:
        raise NotImplementedError
