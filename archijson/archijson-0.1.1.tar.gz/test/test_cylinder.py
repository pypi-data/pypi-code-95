from geometry import Cylinder

if __name__ == '__main__':
    c = Cylinder(5, 10, properties={'color': 'red'})
    print(c)
    print(type(c))
    print(c.data)

    print(c.validate)

    print(Cylinder.is_valid(c.data))

