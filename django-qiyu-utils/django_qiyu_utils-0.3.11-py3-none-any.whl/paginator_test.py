from .paginator import CustomPaginator


def test_custom_page():
    p = CustomPaginator(range(10), 5)
    p1 = p.page(1)

    assert p1.show_page_start_index() == 1
    assert p1.show_page_have_previous_ellipse() is False
    assert p1.show_page_have_next_ellipse() is False
    assert p1.show_page_end_index() == 2

    p = CustomPaginator(range(11), 5)
    p1 = p.page(1)

    assert p1.show_page_start_index() == 1
    assert p1.show_page_have_previous_ellipse() is False
    assert p1.show_page_have_next_ellipse() is False
    assert p1.show_page_end_index() == 3

    p = CustomPaginator(range(20), 2)
    p1 = p.page(1)

    assert p1.show_page_start_index() == 1
    assert p1.show_page_have_previous_ellipse() is False
    assert p1.show_page_have_next_ellipse() is True
    assert p1.show_page_end_index() == 9
    assert list(p1.show_page_range()) == list(range(1, 10))

    p = CustomPaginator(range(20), 2)
    p1 = p.page(5)

    assert p1.show_page_start_index() == 1
    assert p1.show_page_have_previous_ellipse() is False
    assert p1.show_page_have_next_ellipse() is True
    assert p1.show_page_end_index() == 9
    assert list(p1.show_page_range()) == list(range(1, 10))

    p = CustomPaginator(range(20), 2)
    p1 = p.page(6)

    assert p1.show_page_start_index() == 2
    assert p1.show_page_have_previous_ellipse() is True
    assert p1.show_page_have_next_ellipse() is False
    assert p1.show_page_end_index() == 10
    assert list(p1.show_page_range()) == list(range(2, 11))
