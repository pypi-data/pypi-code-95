from archijson.geometry import Cuboid
import archijson.geometry as geometry
import json

if __name__ == '__main__':
    b = Cuboid(3, 3, 3)
    print(dir(b))
    b.w = 2
    print(b.w)
    print(b.data)
    print(b.matrix)
    print(b.validate)

    print(json.dumps(b.validate))

    nb = json.loads('{"type": "Cuboid", "uuid": "ba79302c-c3a3-407a-a684-fa31eef602d6", "matrix": [2.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0, 1.0],  "position": {"x": 0, "y": 0, "z": 0}, "length": 2, "width": 3, "height": 3}')
    print(nb)
    print(Cuboid.is_valid(nb))

    cb = geometry.call['Cuboid'](**nb)
    # cb = Cuboid(1, 21, 23, type='Hello')
    # print(cb.data)

    