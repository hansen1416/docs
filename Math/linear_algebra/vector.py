import math
import decimal


class Vector(object):
    NORMALIZE_ZERO_VECTOR = 'normalize zero magnitude vector'
    NO_UNIQUE_PARALLEL_COMPONENT_MSG = 'NO_UNIQUE_PARALLEL_COMPONENT_MSG'
    NO_UNIQUE_ORTHOGONAL_COMPONENT_MSG = 'NO_UNIQUE_ORTHOGONAL_COMPONENT_MSG'

    def __init__(self, coordinates):
        try:
            if not coordinates:
                raise ValueError
            self.coordinates = tuple([decimal.Decimal(x) for x in coordinates])
            self.dimension = len(self.coordinates)

        except ValueError:
            raise ValueError('The coordinates must be nonempty')

        except TypeError:
            raise TypeError('The coordinates must be an iterable')

    def __str__(self):
        return 'Vector: {}'.format(self.coordinates)

    def __eq__(self, v):
        return self.coordinates == v.coordinates

    def plus(self, v):
        new_coordinates = [x + y for x, y in zip(self.coordinates, v.coordinates)]
        return Vector(new_coordinates)

    def minus(self, v):
        new_coordinates = [x - y for x, y in zip(self.coordinates, v.coordinates)]
        return Vector(new_coordinates)

    def times_scalar(self, c):
        new_coordinates = [c * x for x in self.coordinates]
        return new_coordinates

    def magnitude(self):
        coordinates_squared = [x ** 2 for x in self.coordinates]
        return math.sqrt(sum(coordinates_squared))

    def normalized(self):
        try:
            magnitude = self.magnitude()
            return self.times_scalar(decimal.Decimal('1.0') / magnitude)
        except ZeroDivisionError:
            raise Exception(self.NORMALIZE_ZERO_VECTOR)

    def dot_product(self, v):
        return sum([x * y for x, y in zip(self.coordinates, v.coordinates)])

    def angle_with(self, v, in_degrees=False):
        try:
            u1 = self.normalized()
            u2 = v.normalized()
            angle_in_radians = math.acos(u1.dot(u2))

            if in_degrees:
                return angle_in_radians * 180. / math.pi
            else:
                return angle_in_radians

        except Exception as e:
            if str(e) == self.NORMALIZE_ZERO_VECTOR:
                raise Exception(self.NORMALIZE_ZERO_VECTOR)
            else:
                raise e

    def is_orthogonal_to(self, v, tolerance=1e-10):
        return abs(self.dot(v)) < tolerance

    def is_zero(self, tolerance=1e-10):
        return self.magnitude() < tolerance

    def is_parallel_to(self, v):
        return (
            self.is_zero()
            or v.is_zero()
            or self.angle_with(v) == 0
            or self.angle_with(v) == math.pi
        )

    def component_parallel_to(self, basis):
        try:
            u = basis.normalized()
            weight = self.dot(u)
            return u.times_scalar(weight)
        except Exception as e:
            if str(e) == self.NORMALIZE_ZERO_VECTOR:
                raise Exception(self.NO_UNIQUE_PARALLEL_COMPONENT_MSG)
            else:
                raise e

    def component_orthogonal_to(self, basis):
        try:
            projection = self.component_orthogonal_to(basis)
            return self.minus(projection)
        except Exception as e:
            if str(e) == self.NO_UNIQUE_PARALLEL_COMPONENT_MSG:
                raise Exception(self.NO_UNIQUE_ORTHOGONAL_COMPONENT_MSG)
            else:
                raise e

    def cross(self, v):
        try:
            x1, y1, z1 = self.coordinates
            x2, y2, z2 = v.coordinates
            new_coordinates = [
                y1 * z2 - y2 * z1,
                - (x1 * z2 - x2 * z1),
                x1 * y2 - x2 * y1
            ]
            return Vector(new_coordinates)

        except ValueError as e:
            msg = str(e)
            if msg == 'need more than 2 values to unpack':
                self_embedded_in_r3 = Vector(self.coordinates + ('0',))
                v_embedded_in_r3 = Vector(self.coordinates + ('0',))
                return self_embedded_in_r3.cross(v_embedded_in_r3)
            else:
                raise e
