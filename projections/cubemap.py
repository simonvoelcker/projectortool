from typing import Optional
from dataclasses import dataclass
from projections.base import Projection
from projections.utils import Point, Direction, Vector
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

    The projection is done via an intermediate representation
    of directions: A tuple of face and face-coordinates (cubemap faces).
    """

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
    ) -> Direction:
        u = face_coordinates.x
        v = face_coordinates.y

        if face_coordinates.face == Face.neg_x:
            return Vector(-1, 2 * v - 1, -(2 * u - 1))
        if face_coordinates.face == Face.pos_x:
            return Vector(+1, 2 * v - 1, 2 * u - 1)
        if face_coordinates.face == Face.neg_y:
            return Vector(-(2 * v - 1), -1, -(2 * u - 1))
        if face_coordinates.face == Face.pos_y:
            return Vector(2 * v - 1, +1, -(2 * u - 1))
        if face_coordinates.face == Face.neg_z:
            return Vector(2 * u - 1, 2 * v - 1, -1)
        if face_coordinates.face == Face.pos_z:
            return Vector(-(2 * u - 1), 2 * v - 1, +1)

    @staticmethod
    def face_coordinates_from_direction(
        direction: Direction
    ) -> FaceCoordinates:
        vector = direction.as_vector()
        max_xyz = max(abs(vector.x), abs(vector.y), abs(vector.z))
        x, y, z = (vector.x / max_xyz, vector.y / max_xyz, vector.z / max_xyz)

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

    def to_direction(self, point: Point) -> Optional[Direction]:
        face_coordinates = self.face_coordinates_from_point(point)
        if not face_coordinates:
            return None
        direction = self.direction_from_face_coordinates(face_coordinates)
        return direction

    def to_point(self, direction: Direction) -> Optional[Point]:
        face_coordinates = self.face_coordinates_from_direction(direction)
        point = self.point_from_face_coordinates(face_coordinates)
        return point
