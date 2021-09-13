from archijson.geometry import BasePoint, BaseGeometry
import numpy as np

import pytest

def test_basepoint():
    pt = BasePoint(0, 3, 5)
    assert pt.x == 0
    assert pt.y == 3
    assert pt.z == 5
    print(pt.data)
    
    testpt = {'x': 0, 'y': 2, 'z': 3.1}
    print(BasePoint.DATASCHEMA().validate(testpt))

def test_basegeometry():
    bg = BaseGeometry('Geom')
    print(bg)
    print(bg.data)
    print(bg.validate())

    bg.position = BasePoint(2, 3, 4)
    print(bg.data)


test_basepoint()
False

test_basegeometry()




