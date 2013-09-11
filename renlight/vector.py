
"""
    This module contain implementation of basic vector types.
    
"""

import math

class Vector2:
    """
        Implementation of Vector2 type.
    """
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        """
            Constructor accept x and y component of the vector.
        """
        self.x = x
        self.y = y

    def __str__(self):
        """
            Return information about vector.
        """
        return '(%s,%s)' % (self.x, self.y)

    def __repr__(self):
        """
            Return information about vector.
        """
        return 'Vector2(%s,%s)' % (self.x, self.y)

    def __add__(self, vec):
        """
            Return new vector that is sum of two vectors.
        """
        return Vector2(self.x + vec.x, self.y + vec.y)

    def __sub__(self, vec):
        """
            Return new vector that is difference of two vectors.
        """
        return Vector2(self.x - vec.x, self.y - vec.y)

    def __eq__(self, vec):
        """
            Return True if two vectors are equal otherwise False.
        """
        return (self.x == vec.x) and (self.y == vec.y)

    def __mul__(self, t):
        """
            Return new vector that is scaled by factor t.
        """
        return Vector2(self.x * t, self.y * t)

    def __rmul__(self, t):
        """
            Return new vector that is scaled by factor t.
        """
        return Vector2(self.x * t, self.y * t)

    def scale(self, t):
        """
            Inplace scale vector by factor t.
        """
        self.x = t * self.x
        self.y = t * self.y
        return self

    @classmethod
    def create(cls, *args):
        """
            Create new Vector2.
        """
        return Vector2(float(args[0]), float(args[1]))


class Vector3:
    """
        Implementation of Vector3 type.
    """
    __slots__ = ['x', 'y', 'z']
    def __init__(self, x, y, z):
        """
            Constructor accept x, y and z component of the vector.
        """
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        """
            Return information about vector.
        """
        return '(%s,%s,%s)' % (self.x, self.y, self.z)

    def __repr__(self):
        """
            Return information about vector.
        """
        return 'Vector3(%s,%s,%s)' % (self.x, self.y, self.z)

    def __add__(self, vec):
        """
            Return new vector that is sum of two vectors.
        """
        return Vector3(self.x + vec.x, self.y + vec.y, self.z + vec.z)

    def __sub__(self, vec):
        """
            Return new vector that is difference of two vectors.
        """
        return Vector3(self.x - vec.x, self.y - vec.y, self.z - vec.z)

    def __eq__(self, vec):
        """
            Return True if two vectors are equal otherwise False.
        """
        return (self.x == vec.x) and (self.y == vec.y) and (self.z == vec.z)
    
    def __mul__(self, t):
        """
            Return new vector that is scaled by factor t.
        """
        return Vector3(self.x * t, self.y * t, self.z * t)

    def __rmul__(self, t):
        """
            Return new vector that is scaled by factor t.
        """
        return Vector3(self.x * t, self.y * t, self.z * t)

    def scale(self, t):
        """
            Inplace scale vector by factor t.
        """
        self.x = t * self.x
        self.y = t * self.y
        self.z = t * self.z
        return self

    def dot(self, vec):
        """
            Return dot product of two vectors.
        """
        return (self.x * vec.x) + (self.y * vec.y) + (self.z * vec.z)

    def length(self):
        """
            Return length of the vector.
        """
        return math.sqrt(self.dot(self))

    def length_squared(self):
        """
            Return length squared.
        """
        return (self.x * self.x) + (self.y * self.y) + (self.z * self.z) 

    def normalize(self):
        """
            Normalize the vector.
        """
        length = self.length()
        if length == 0.0:
            return self  
        return self.scale(1.0 / length)

    def cross(self, vec):
        """
            Return cross product of two vectors.
        """
        return Vector3(self.y * vec.z - self.z * vec.y,
                      self.z * vec.x - self.x * vec.z,
                      self.x * vec.y - self.y * vec.x)

    @classmethod
    def create(cls, *args):
        """
            Create new Vector3.
        """
        return Vector3(float(args[0]), float(args[1]), float(args[2]))

class Vector4:
    """
        Implementation of Vector4 type.
    """
    __slots__ = ['x', 'y', 'z', 'w']
    def __init__(self, x, y, z, w):
        """
            Constructor accept x, y, z and w component of the vector.
        """
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __str__(self):
        """
            Return information about vector.
        """
        return '(%s,%s,%s,%s)' % (self.x, self.y, self.z, self.w)

    def __repr__(self):
        """
            Return information about vector.
        """
        return 'Vector4(%s,%s,%s,%s)' % (self.x, self.y, self.z, self.w)

    def __add__(self, vec):
        """
            Return new vector that is sum of two vectors.
        """
        return Vector4(self.x + vec.x, self.y + vec.y, self.z + vec.z, self.w + vec.w)

    def __sub__(self, vec):
        """
            Return new vector that is difference of two vectors.
        """
        return Vector4(self.x - vec.x, self.y - vec.y, self.z - vec.z, self.w - vec.w)

    def __eq__(self, vec):
        """
            Return True if two vectors are equal otherwise False.
        """
        return (self.x == vec.x) and (self.y == vec.y) and (self.z == vec.z) and (self.w == vec.w)

    def __mul__(self, t):
        """
            Return new vector that is scaled by factor t.
        """
        return Vector4(self.x * t, self.y * t, self.z * t, self.w * t)

    def __rmul__(self, t):
        """
            Return new vector that is scaled by factor t.
        """
        return Vector4(self.x * t, self.y * t, self.z * t, self.w * t)

    def scale(self, t):
        """
            Inplace scale vector by factor t.
        """
        self.x = t * self.x
        self.y = t * self.y
        self.z = t * self.z
        self.w = t * self.w
        return self

