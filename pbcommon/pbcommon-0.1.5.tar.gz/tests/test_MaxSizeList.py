from pbcommon.MaxSizeList import MaxSizeList


def test_max_size_list():
    """
    it tests that the MazSizeList class does not extend past the max length
    allow for list
    """
    lst = MaxSizeList(5)

    [lst.push(i) for i in range(1, 10)]

    assert len(lst.to_list()) == 5
