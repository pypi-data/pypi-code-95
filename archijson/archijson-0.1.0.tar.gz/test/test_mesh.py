from geometry import Vertices, Segments, Faces, Mesh



v = Vertices([1, 1, 1, 3, 3, 3], 2)

print(v.validate)
print(v.param)
print(v.coordinates)
print(Vertices.is_valid(v.data))
print(v.toList())

s = Segments([1, 1, 1, 3, 3, 3], 2)
print(s.data)
print(s.validate)
print(s.toList())

f = Faces([1], [3], [1, 2, 3])
print(f.data)

ff = Faces([1], [2], [1, 2])
print(ff.validate)

m = Mesh(v, f)
print(m.data)
print(m.validate)

print('')


