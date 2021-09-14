def test_import():
    from bioformats_jar import loci

    assert loci.formats
    assert loci.common
    assert loci.plugins
    assert loci.poi
