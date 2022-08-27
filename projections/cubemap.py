from typing import Optional
from dataclasses import dataclass
from projections.base import Projection, Angles, Point
from math import atan2, sqrt, pi, sin, cos
from enum import Enum


class Face(Enum):
    neg_x = 1
    pos_x = 2
    neg_y = 3
    pos_y = 4
    neg_z = 5
    pos_z = 6


@dataclass
class FaceCoordinates:
    face: Face
    x: float
    y: float


@dataclass
class Direction:
    x: float
    y: float
    z: float


class CubemapProjection(Projection):
    """
    The cubemap is assumed to look like this:

    _______________________
    |      ####           |
    |      ####           |
    | #### #### #### #### |
    | #### #### #### #### |
    |      ####           |
    |      ####           |
    -----------------------

    The ideal image will therefore have 4:3 aspect ratio,
    which is why these numbers appear in the computations below.

    The projection is done via two intermediate representations
    of directions: a direction vector and a tuple of face and
    face-coordinates (cubemap faces).
    """

    @staticmethod
    def angles_from_direction(direction: Direction) -> Angles:
        # catch altitude special cases
        if direction.x == 0 and direction.z == 0:
            if direction.y == 0:
                # null vector case: safe fallback
                return Angles(altitude=0, azimuth=0)
            elif direction.y < 0:
                # again save fallback for azimuth
                return Angles(altitude=-pi / 2.0, azimuth=0)
            else:
                # again save fallback for azimuth
                return Angles(altitude=+pi / 2.0, azimuth=0)

        altitude = atan2(direction.y, sqrt(direction.x * direction.x + direction.z * direction.z))

        # catch azimuth special case
        if direction.x == 0:
            return Angles(
                altitude=altitude,
                azimuth=-pi / 2.0 if direction.z < 0 else +pi / 2.0
            )

        # general case
        azimuth = atan2(direction.z, direction.x)  # outputs [-pi;pi]
        if azimuth < 0.0:
            azimuth += 2.0 * pi  # map to [0;2pi]
        angles = Angles(altitude=altitude, azimuth=azimuth)
        return angles

    @staticmethod
    def direction_from_angles(angles: Angles) -> Direction:
        x, y, z = 1.0, 0.0, 0.0
        x, y = (
            x * cos(angles.altitude) - y * sin(angles.altitude),
            x * sin(angles.altitude) + y * cos(angles.altitude)
        )
        x, z = (
            x * cos(angles.azimuth) - z * sin(angles.azimuth),
            x * sin(angles.azimuth) + z * cos(angles.azimuth)
        )
        return Direction(x, y, z)

    @staticmethod
    def face_coordinates_from_point(point: Point) -> Optional[FaceCoordinates]:
        face_index_x = int(point.x * 4)
        face_offset_x = point.x * 4 - face_index_x
        face_index_y = int(point.y * 3)
        face_offset_y = point.y * 3 - face_index_y
        face_lookup = {
            (1, 1): Face.neg_x,
            (3, 1): Face.pos_x,
            (1, 0): Face.neg_y,
            (1, 2): Face.pos_y,
            (2, 1): Face.neg_z,
            (0, 1): Face.pos_z
        }
        face = face_lookup.get((face_index_x, face_index_y))
        if not face:
            return None
        return FaceCoordinates(face, face_offset_x, face_offset_y)

    @staticmethod
    def point_from_face_coordinates(face_coordinates: FaceCoordinates) -> Point:
        offset_lookup = {
            Face.neg_x: (1, 1),
            Face.pos_x: (3, 1),
            Face.neg_y: (1, 0),
            Face.pos_y: (1, 2),
            Face.neg_z: (2, 1),
            Face.pos_z: (0, 1)
        }
        face_offsets = offset_lookup[face_coordinates.face]
        return Point(
            x=(face_coordinates.x + face_offsets[0]) / 4.0,
            y=(face_coordinates.y + face_offsets[1]) / 3.0
        )

    @staticmethod
    def direction_from_face_coordinates(
        face_coordinates: FaceCoordinates
    ) -> Optional[Direction]:
        u = face_coordinates.x
        v = face_coordinates.y

        if face_coordinates.face == Face.neg_x:
            return Direction(-1, 2 * v - 1, -(2 * u - 1))
        if face_coordinates.face == Face.pos_x:
            return Direction(+1, 2 * v - 1, 2 * u - 1)
        if face_coordinates.face == Face.neg_y:
            return Direction(-(2 * v - 1), -1, -(2 * u - 1))
        if face_coordinates.face == Face.pos_y:
            return Direction(2 * v - 1, +1, -(2 * u - 1))
        if face_coordinates.face == Face.neg_z:
            return Direction(2 * u - 1, 2 * v - 1, -1)
        if face_coordinates.face == Face.pos_z:
            return Direction(-(2 * u - 1), 2 * v - 1, +1)

    @staticmethod
    def face_coordinates_from_direction(direction: Direction) -> FaceCoordinates:
        max_xyz = max(abs(direction.x), abs(direction.y), abs(direction.z))
        x, y, z = (direction.x / max_xyz, direction.y / max_xyz, direction.z / max_xyz)

        def to_uv(direction_component: float) -> float:
            return (direction_component + 1.0) / 2.0

        if x == -1.0:
            return FaceCoordinates(Face.neg_x, to_uv(-z), to_uv(+y))
        if x == +1.0:
            return FaceCoordinates(Face.pos_x, to_uv(+z), to_uv(+y))
        if y == -1.0:
            return FaceCoordinates(Face.neg_y, to_uv(-z), to_uv(-x))
        if y == +1.0:
            return FaceCoordinates(Face.pos_y, to_uv(-z), to_uv(+x))
        if z == -1.0:
            return FaceCoordinates(Face.neg_z, to_uv(+x), to_uv(+y))
        if z == +1.0:
            return FaceCoordinates(Face.pos_z, to_uv(-x), to_uv(+y))

        raise RuntimeError('Bad direction vector')

    def to_angles(self, point: Point) -> Optional[Angles]:
        face_coordinates = self.face_coordinates_from_point(point)
        if not face_coordinates:
            return None
        direction = self.direction_from_face_coordinates(face_coordinates)
        angles = self.angles_from_direction(direction)
        return angles

    def to_point(self, angles: Angles) -> Optional[Point]:
        direction = self.direction_from_angles(angles)
        face_coordinates = self.face_coordinates_from_direction(direction)
        point = self.point_from_face_coordinates(face_coordinates)
        return point
