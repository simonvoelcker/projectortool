from typing import Optional
from math import atan2, pi, sqrt, sin, cos
from projections.base import Projection
from projections.utils import Direction, Angles, Point


class HemisphericalProjection(Projection):
    def __init__(self, hemi_fov_x=180, hemi_fov_y=180):
        super().__init__()
        self.fov_x = hemi_fov_x / 180.0 * pi
        self.fov_y = hemi_fov_y / 180.0 * pi

    @staticmethod
    def aspect_ratio() -> float:
        return 1.0

    def to_direction(self, point: Point) -> Optional[Direction]:
        center_x_angle = (point.x - 0.5) * self.fov_x
        center_y_angle = (point.y - 0.5) * self.fov_y

        center_distance_angle = sqrt(
            center_x_angle * center_x_angle +
            center_y_angle * center_y_angle
        )
        altitude = pi / 2.0 - center_distance_angle

        # azimuth special case
        if center_x_angle == 0:
            return Angles(
                altitude=altitude,
                azimuth=-pi / 2.0 if center_y_angle < 0 else +pi / 2.0
            )
        # azimuth general case
        azimuth = atan2(center_y_angle, center_x_angle)  # outputs [-pi;pi]
        if azimuth < 0.0:
            azimuth += 2.0 * pi  # map to [0;2pi]

        return Angles(altitude=altitude, azimuth=azimuth)

    def to_point(self, direction: Direction) -> Optional[Point]:
        angles = direction.as_angles()
        center_distance_angle = pi / 2.0 - angles.altitude

        x = center_distance_angle * cos(angles.azimuth) / self.fov_x + 0.5
        if x < 0 or x > 1:
            return None

        y = center_distance_angle * sin(angles.azimuth) / self.fov_y + 0.5
        if y < 0 or y > 1:
            return None

        return Point(x, y)
