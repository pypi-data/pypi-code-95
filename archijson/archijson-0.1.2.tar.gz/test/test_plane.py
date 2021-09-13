from archijson.geometry import Plane

if __name__ == '__main__':
    c = Plane(5, 10, properties={'color': 'red'})
    print(c)
    print(type(c))
    print(c.data)

    print(c.validate)

    print(Plane.is_valid(c.data))

