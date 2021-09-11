"""Defines Vector2 class for simplification of vector math."""
import math

class Vector2:
    """Vector object with x and y components."""
    def __init__(self, x=0, y=0):
        """Creates a new Vector2 object.

        Args:
            x (int, optional): The x component of the vector. Defaults to 0.
            y (int, optional): The y component of the vector. Defaults to 0.
        """
        self.x = x
        self.y = y

    @property
    def angle(self):
        return math.atan2(self.y, self.x)

    @property
    def magnitude(self):
        return math.sqrt(self.magnitude2)

    @property
    def magnitude2(self):
        return (self.x * self.x) + (self.y * self.y)

    def __str__(self):
        return f"Vector2({self.x}, {self.y})"

    def __eq__(self, v2):
        if not isinstance(v2, Vector2):
            return False
        return self.x == v2.x and self.y == v2.y

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __add__(self, v2):
        if isinstance(v2, (int, float)):
            return Vector2(self.x + v2, self.y + v2)
        if isinstance(v2, Vector2):
            return Vector2(self.x + v2.x, self.y + v2.y)
        raise TypeError(f"unsupported operand type(s) for +: 'Vector2' and '{type(v2).__name__}'")

    def __sub__(self, v2):
        if isinstance(v2, (int, float)):
            return Vector2(self.x - v2, self.y - v2)
        if isinstance(v2, Vector2):
            return Vector2(self.x - v2.x, self.y - v2.y)
        raise TypeError(f"unsupported operand type(s) for -: 'Vector2' and '{type(v2).__name__}'")

    def __mul__(self, v2):
        if isinstance(v2, (int, float)):
            return Vector2(self.x * v2, self.y * v2)
        raise TypeError(f"unsupported operand type(s) for +: 'Vector2' and '{type(v2).__name__}'")

    def __truediv__(self, v2):
        if isinstance(v2, (int, float)):
            return Vector2(self.x / v2, self.y / v2)
        raise TypeError(f"unsupported operand type(s) for +: 'Vector2' and '{type(v2).__name__}'")

    def __floordiv__(self, v2):
        if isinstance(v2, (int, float)):
            return Vector2(self.x // v2, self.y // v2)
        raise TypeError(f"unsupported operand type(s) for +: 'Vector2' and '{type(v2).__name__}'")

    def dot(self, v2) -> float:
        """Returns the dot product of the two Vector2 objects.

        Args:
            v2 (Vector2): The second Vector2 object from which the dot product is computed.
        """
        if not isinstance(v2, Vector2):
            raise TypeError(f"v2 must be of type 'Vector2' (Type: '{type(v2).__name__}')")
        return (self.x * v2.x) + (self.y * v2.y)

    def normalized(self):
        """Returns a Vector2 object with the same direction and a magnitude of 1.

        Returns:
            Vector2: The normal of the original Vector2 object.
        """
        if self.x == 0 and self.y == 0:
            return Vector2()
        mag = self.magnitude
        x = self.x / mag
        y = self.y / mag
        return Vector2(x, y)