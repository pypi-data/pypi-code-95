#
#   Test if all pygeos methods are implemented
#   This makes it easier to update PGPD to new PyGEOS versions
#
import pytest
import pygeos
import pgpd

skips = {
    'geometry': (
        'get_geometry',
        'get_rings',
        'IntEnum',
    ),
    'creation': (
        'box',
        'collections_1d',
        'geometrycollections',
        'linearrings',
        'linestrings',
        'multilinestrings',
        'multipoints',
        'multipolygons',
        'points',
        'polygons',
        'simple_geometries_1d',
    ),
    'measurement': (),
    'predicates': (
        'warnings',
    ),
    'set_operations': (
        'box',
        'UnsupportedGEOSOperation',
    ),
    'constructive': (
        'BufferCapStyles',
        'BufferJoinStyles',
        'ParamEnum',
        'polygonize_full',
    ),
    'linear': (
        'warn',
    ),
    'coordinates': (),
    'strtree': (
        'BinaryPredicate',
        'ParamEnum',
        'VALID_PREDICATES',
    ),
}


@pytest.mark.parametrize('module', skips.keys())
def test_for_missing_methods(module):
    skip = skips[module]
    mod = getattr(pygeos, module)

    for func in dir(mod):
        if func.startswith('_'):
            continue
        if func in ('Geometry', 'GeometryType', 'lib', 'np', 'requires_geos', 'multithreading_enabled'):
            continue
        if func in skip:
            continue

        if func not in dir(pgpd.GeosSeriesAccessor):
            raise NotImplementedError(f'{module}.{func}')
