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
    def to_angle(self, point: Point) -> Angles:
        raise NotImplementedError()

    def to_point(self, angles: Angles) -> Point:
        raise NotImplementedError
