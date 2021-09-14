from pkg_resources import resource_filename

from .. import layout


def test_load_template():
    layout.COLOR_INDEX = 0
    path = resource_filename(__name__, 'templates/test.yaml')
    t, _ = layout.load_template(path)
    assert t['time-window'] == -100


def test_create_template_chans0():
    layout.COLOR_INDEX = 0
    chans = ['A', 'B', 'C']
    t0, l0 = layout.template_from_chans(chans)
    layout.convert_layout(t0, 'grid')
    path = resource_filename(__name__, 'templates/test0.yaml')
    t1, l1 = layout.load_template(path)
    assert t0 == t1


def test_create_template_chans1():
    layout.COLOR_INDEX = 0
    chans = ['A', '.', 'B', 'C', '.', 'D']
    t0, l0 = layout.template_from_chans(chans)
    path = resource_filename(__name__, 'templates/test1.yaml')
    t1, l1 = layout.load_template(path)
    assert t0 == t1


def test_template_convert_grid():
    layout.COLOR_INDEX = 0
    path = resource_filename(__name__, 'templates/test1.yaml')
    t0, l0 = layout.load_template(path)
    layout.convert_layout(t0, 'grid')
    path = resource_filename(__name__, 'templates/test1-1.yaml')
    t1, l1 = layout.load_template(path)
    assert t0 == t1


def test_template_convert_stack():
    layout.COLOR_INDEX = 0
    path = resource_filename(__name__, 'templates/test1.yaml')
    t0, l0 = layout.load_template(path)
    layout.convert_layout(t0, 'stack')
    path = resource_filename(__name__, 'templates/test1-2.yaml')
    t1, l1 = layout.load_template(path)
    assert t0 == t1


def test_template_convert_single():
    layout.COLOR_INDEX = 0
    path = resource_filename(__name__, 'templates/test1.yaml')
    t0, l0 = layout.load_template(path)
    layout.convert_layout(t0, 'single')
    path = resource_filename(__name__, 'templates/test1-3.yaml')
    t1, l1 = layout.load_template(path)
    assert t0 == t1


def test_load_template_stp():
    path = resource_filename(__name__, 'templates/test2.stp')
    t0, l0 = layout.load_template(path)
    assert l0 == 'single'
    path = resource_filename(__name__, 'templates/test2.yaml')
    t1, l1 = layout.load_template(path)
    assert l1 == 'table'
    assert t0 == t1


def test_load_template_txt():
    layout.COLOR_INDEX = 0
    path = resource_filename(__name__, 'templates/test3.txt')
    t0, l0 = layout.load_template(path)
    assert l0 == 'grid'
    path = resource_filename(__name__, 'templates/test3.yaml')
    t1, l1 = layout.load_template(path)
    assert l1 == 'table'
    assert t0 == t1


def test_load_template_xml():
    layout.COLOR_INDEX = 0
    path = resource_filename(__name__, 'templates/test4.xml')
    t0, l0 = layout.load_template(path)
    assert l0 == 'grid'
    path = resource_filename(__name__, 'templates/test4.yaml')
    t1, l1 = layout.load_template(path)
    assert l1 == 'table'
    assert t0['plots'] == t1['plots']
