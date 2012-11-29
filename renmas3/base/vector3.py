import math

class Vector2:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '(%s,%s)' % (self.x, self.y)

    def __repr__(self):
        return 'Vector2(%s,%s)' % (self.x, self.y)

    def __add__(self, vec):
        return Vector2(self.x + vec.x, self.y + vec.y)

    def __sub__(self, vec):
        return Vector2(self.x - vec.x, self.y - vec.y)

    def __eq__(self, vec):
        return (self.x == vec.x) and (self.y == vec.y)

    def __mul__(self, t):
        return Vector2(self.x * t, self.y * t)

    def __rmul__(self, t):
        return Vector2(self.x * t, self.y * t)

    def scale(self, t):
        self.x = t * self.x
        self.y = t * self.y
        return self

    def negated(self):
        return self.scale(-1.0)

    def to_ds(self):
        return (float(self.x), float(self.y), 0.0, 0.0)

class Vector3:
    __slots__ = ['x', 'y', 'z']
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return '(%s,%s,%s)' % (self.x, self.y, self.z)

    def __repr__(self):
        return 'Vector3(%s,%s,%s)' % (self.x, self.y, self.z)

    def __add__(self, vec):
        return Vector3(self.x + vec.x, self.y + vec.y, self.z + vec.z)

    def __sub__(self, vec):
        return Vector3(self.x - vec.x, self.y - vec.y, self.z - vec.z)

    def __eq__(self, vec):
        return (self.x == vec.x) and (self.y == vec.y) and (self.z == vec.z)
    
    def __mul__(self, t):
        return Vector3(self.x * t, self.y * t, self.z * t)

    def __rmul__(self, t):
        return Vector3(self.x * t, self.y * t, self.z * t)

    def scale(self, t):
        self.x = t * self.x
        self.y = t * self.y
        self.z = t * self.z
        return self

    def dot(self, vec):
        return (self.x * vec.x) + (self.y * vec.y) + (self.z * vec.z)

    def length(self):
        return math.sqrt(self.dot(self))

    def length_squared(self):
        return (self.x * self.x) + (self.y * self.y) + (self.z * self.z) 

    def negated(self):
        return self.scale(-1)

    def normalize(self):
        length = self.length()
        if length == 0.0: return self  
        return self.scale(1.0 / length)

    def to_ds(self):
        return (float(self.x), float(self.y), float(self.z), 0.0)

    def cross(self, vec):
        return Vector3(self.y * vec.z - self.z * vec.y,
                      self.z * vec.x - self.x * vec.z,
                      self.x * vec.y - self.y * vec.x)


class Vector4:
    __slots__ = ['x', 'y', 'z', 'w']
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __str__(self):
        return '(%s,%s,%s,%s)' % (self.x, self.y, self.z, self.w)

    def __repr__(self):
        return 'Vector4(%s,%s,%s,%s)' % (self.x, self.y, self.z, self.w)

    def __add__(self, vec):
        return Vector4(self.x + vec.x, self.y + vec.y, self.z + vec.z, self.w + vec.w)

    def __sub__(self, vec):
        return Vector4(self.x - vec.x, self.y - vec.y, self.z - vec.z, self.w - vec.w)

    def __eq__(self, vec):
        return (self.x == vec.x) and (self.y == vec.y) and (self.z == vec.z) and (self.w == vec.w)

    def __mul__(self, t):
        return Vector4(self.x * t, self.y * t, self.z * t, self.w * t)

    def __rmul__(self, t):
        return Vector4(self.x * t, self.y * t, self.z * t, self.w * t)

    def scale(self, t):
        self.x = t * self.x
        self.y = t * self.y
        self.z = t * self.z
        self.w = t * self.w
        return self

    def negated(self):
        return self.scale(-1.0)

    def to_ds(self):
        return (float(self.x), float(self.y), float(self.z), float(self.w))

