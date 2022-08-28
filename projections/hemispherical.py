from typing import Optional
from math import atan2, pi, sqrt, sin, cos
from projections.base import Projection
from projections.utils import Direction, Angles, Point


class HemisphericalProjection(Projection):

    # Angle between left and right edge of the image, in radians
    FOV = pi

    def to_direction(self, point: Point) -> Optional[Direction]:
        center_x, center_y = point.x - 0.5, point.y - 0.5
        center_distance = sqrt(center_x*center_x + center_y*center_y)
        center_distance_angle = center_distance * self.FOV
        altitude = pi / 2.0 - center_distance_angle

        # azimuth special case
        if center_x == 0:
            return Angles(
                altitude=altitude,
                azimuth=-pi / 2.0 if center_y < 0 else +pi / 2.0
            )
        # azimuth general case
        azimuth = atan2(center_y, center_x)  # outputs [-pi;pi]
        if azimuth < 0.0:
            azimuth += 2.0 * pi  # map to [0;2pi]

        return Angles(altitude=altitude, azimuth=azimuth)

    def to_point(self, direction: Direction) -> Optional[Point]:
        angles = direction.as_angles()
        center_distance_angle = pi / 2.0 - angles.altitude
        center_distance = center_distance_angle / self.FOV

        x = center_distance * cos(angles.azimuth) + 0.5
        if x < 0 or x > 1:
            return None

        y = center_distance * sin(angles.azimuth) + 0.5
        if y < 0 or y > 1:
            return None

        return Point(x, y)
