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

    def rotated(self, angle_x: int, angle_y: int, angle_z: int) -> "Direction":
        return self.as_vector().rotated(angle_x, angle_y, angle_z)


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

    def rotated(self, angle_x: int, angle_y: int, angle_z: int) -> "Direction":

        angle_x = float(angle_x) / 180.0 * pi
        angle_y = float(angle_y) / 180.0 * pi
        angle_z = float(angle_z) / 180.0 * pi

        sin_x, cos_x = sin(angle_x), cos(angle_x)
        y_dash = self.y * cos_x - self.z * sin_x
        z_dash = self.y * sin_x + self.z * cos_x
        self.y, self.z = y_dash, z_dash

        sin_y, cos_y = sin(angle_y), cos(angle_y)
        x_dash = self.x * cos_y - self.z * sin_y
        z_dash = self.x * sin_y + self.z * cos_y
        self.x, self.z = x_dash, z_dash

        sin_z, cos_z = sin(angle_z), cos(angle_z)
        x_dash = self.x * cos_z - self.y * sin_z
        y_dash = self.x * sin_z + self.y * cos_z
        self.x, self.y = x_dash, y_dash

        return self


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
