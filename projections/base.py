from typing import Optional
from dataclasses import dataclass


@dataclass
class Point:
    x: float = 0
    y: float = 0


@dataclass
class Angles:
    azimuth: float = 0
    altitude: float = 0


class Projection:
    def to_angles(self, point: Point) -> Optional[Angles]:
        raise NotImplementedError()

    def to_point(self, angles: Angles) -> Optional[Point]:
        raise NotImplementedError
