from math import pi, atan2, sqrt, sin, cos
from dataclasses import dataclass


@dataclass
class Point:
    x: float = 0
    y: float = 0


class Direction:

    def as_vector(self) -> "Vector":
        raise NotImplementedError

    def as_angles(self) -> "Angles":
        raise NotImplementedError

    def rotate(self, angle_x: int, angle_y: int, angle_z: int) -> "Direction":
        return self.as_vector().rotate(angle_x, angle_y, angle_z)


class Vector(Direction):
    def __init__(self, x: float, y: float, z: float):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z

    def as_vector(self) -> "Vector":
        return self

    def as_angles(self) -> "Angles":
        # catch altitude special cases
        if self.x == 0 and self.z == 0:
            if self.y == 0:
                # null vector case: safe fallback
                return Angles(altitude=0, azimuth=0)
            elif self.y < 0:
                # again save fallback for azimuth
                return Angles(altitude=-pi / 2.0, azimuth=0)
            else:
                # again save fallback for azimuth
                return Angles(altitude=+pi / 2.0, azimuth=0)

        altitude = atan2(self.y, sqrt(self.x * self.x + self.z * self.z))

        # catch azimuth special case
        if self.x == 0:
            return Angles(
                altitude=altitude,
                azimuth=-pi / 2.0 if self.z < 0 else +pi / 2.0
            )

        # general case
        azimuth = atan2(self.z, self.x)  # outputs [-pi;pi]
        if azimuth < 0.0:
            azimuth += 2.0 * pi  # map to [0;2pi]
        angles = Angles(altitude=altitude, azimuth=azimuth)
        return angles

    def rotate(self, angle_x: int, angle_y: int, angle_z: int) -> "Direction":
        # TODO
        raise NotImplementedError


class Angles(Direction):
    def __init__(self, azimuth: float, altitude: float):
        super().__init__()
        self.azimuth = azimuth
        self.altitude = altitude

    def as_vector(self) -> "Vector":
        x, y, z = 1.0, 0.0, 0.0
        x, y = (
            x * cos(self.altitude) - y * sin(self.altitude),
            x * sin(self.altitude) + y * cos(self.altitude)
        )
        x, z = (
            x * cos(self.azimuth) - z * sin(self.azimuth),
            x * sin(self.azimuth) + z * cos(self.azimuth)
        )
        return Vector(x, y, z)

    def as_angles(self) -> "Angles":
        return self

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
