from math import pi

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

    def apply_offsets(self, azimuth_offset: int, altitude_offset: int):
        """
        Apply angle offsets, in degrees.
        """
        self.azimuth += azimuth_offset / 180.0 * pi
        self.altitude += altitude_offset / 180.0 * pi
        self.clamp()

    def clamp(self):
        """
        Apply angle range checks and correction, such that:
        - azimuth lies within 0 to 2*pi
        - altitude within -0.5*pi to +0.5*pi
        - the direction is maintained
        """

        # Rough clamping to -pi...pi in case we need to flip
        while self.altitude < -pi:
            self.altitude += 2.0 * pi
        while self.altitude > pi:
            self.altitude -= 2.0 * pi

        assert -pi <= self.altitude <= pi

        # Flip both angles if altitude is outside of range
        if self.altitude < -0.5 * pi:
            self.altitude = - pi - self.altitude
            self.azimuth += pi
        elif self.altitude > 0.5 * pi:
            self.altitude = pi - self.altitude
            self.azimuth += pi

        while self.azimuth < 0:
            self.azimuth += 2.0 * pi
        while self.azimuth > 2.0 * pi:
            self.azimuth -= 2.0 * pi

        assert -0.5 * pi <= self.altitude <= 0.5 * pi
        assert 0 <= self.azimuth <= 2.0 * pi


class Projection:
    def to_angles(self, point: Point) -> Optional[Angles]:
        raise NotImplementedError()

    def to_point(self, angles: Angles) -> Optional[Point]:
        raise NotImplementedError
