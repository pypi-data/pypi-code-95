'''
Necessary testing for all functions from almutils.py
'''

# import functions from testing from almutils
import almutils as almutils

# datadim test checks


def testDatadim():
    print('Testing datadim...', end='')
    assert(almutils.datadim([[1], [2], [3]]) == 1)
    assert(almutils.datadim(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]) == 3)
    print('Passed.')


# arr2str test checks
def testArr2str():
    print('Testing arr2str...', end='')
    assert(almutils.arr2str([2, 3, 4]) == "2 3 4")
    assert(almutils.arr2str(2) == "2")
    assert(almutils.arr2str([[1, 2], [3, 4], [5, 6]]) == "1 2\n3 4\n5 6")
    assert(almutils.arr2str([[1], [2, 3], [4, 5, 6]] == "1\n2 3\n4 5 6"))
    print('Passed.')


# alm2lst test checks
def testAlm2lst():
    print('Testing alm2lst...', end='')
    assert(almutils.alm2lst("~/.temp.alm") == "~/.temp.lst")
    print('Passed.')


# zip_2d_lists test checks
def testZip2dLists():
    print('Testing zip2dLists...', end='')
    a = [[1], [2], [3]]
    b = [[4], [5], [6]]
    assert(almutils.zip_2d_lists(a, b) == [[1, 4], [2, 5], [3, 6]])
    print('Passed.')


# represent_model_str test checks
def testRepresentModelStr():
    print('Testing represent_model_str...', end='')
    assert(almutils.represent_model_str(
        ["1.0 X1", "0.5 X2"]) == "1.0 * X1 + 0.5 * X2")
    assert(almutils.represent_model_str(
        ["1.0 X1", "-0.5 X2^3"]) == "1.0 * X1 - 0.5 * X2^3")
    print('Passed.')

# data2min test checks
# assert(almutils.data2min([[0,1],[2,-1]]) == [0, -1])

# data2max test checks
# assert(almutils.data2max([[0,1],[2,-1]]) == [1, 2])


# only_contains test checks
def testOnlyContains():
    print('Testing onlyContains...', end='')
    assert(almutils.only_contains("*****", '*') == True)
    assert(almutils.only_contains("", '*') == False)
    print('Passed.')


# nets test checks
def testNets():
    print('Testing nets...', end='')
    assert(almutils.nets([1, 2, 3], 0, lambda x: x % 2 != 0) == (0, 1))
    assert(almutils.nets([1, 2, 3], 0, lambda x: x < 0) == None)
    print('Passed.')


# cast test checks
def testCast():
    print('Testing cast...', end='')
    assert(almutils.cast(1e4) == 10000)
    assert(almutils.cast(3.0) == 3.0)
    assert(almutils.cast('T') == True)
    assert(almutils.cast('t') == 't')
    assert(almutils.cast('a') == 'a')
    print('Passed.')


# increment test checks
def testIncrement():
    print('Testing increment...', end='')
    assert(almutils.increment([7, 8, 9], 2, 1) == None)
    assert(almutils.increment([7, 8, 9], 0, 2) == (2, 9))
    print('Passed.')


# format_extry test checks
def testFormatExtry():
    print('Testing formatExtry...', end='')
    opts = dict()
    opts["data"] = [1, 2, 3]
    assert(almutils.format_entry("data", opts) == "data 1 2 3\n")
    print('Passed.')


# format_section test checks
def testFormatSection():
    print('Testing formatSection...', end='')
    opts = dict()
    opts["data"] = [[1, 0], [2, 0], [3, 0]]
    assert(almutils.format_section("data", opts) ==
           "\nBEGIN_DATA\n1 0\n2 0\n3 0\nEND_DATA\n")
    print('Passed.')

# parse_term_code test checks


# vector_2d test checks
def testVector2D():
    print('Testing vector2D...', end='')
    assert(almutils.vector_2d([1, 2, 3]) == [[1], [2], [3]])
    assert(almutils.vector_2d(1) == [[1]])
    assert(almutils.vector_2d([[1], [2], [3]]) == [[1], [2], [3]])
    print('Passed.')

# get_alamo_version test checks


def testAll():
    testDatadim()
    testArr2str()
    testAlm2lst()
    testZip2dLists()
    testRepresentModelStr()
    testOnlyContains()
    testNets()
    testCast()
    testIncrement()
    testFormatExtry()
    testFormatSection()
    testVector2D()


def main():
    testAll()


if __name__ == '__main__':
    main()
