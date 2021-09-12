# clustercron/version.py
# vim: ai et ts=4 sw=4 sts=4 ft=python fileencoding=utf-8


def get_version():
    version = None
    try:
        from importlib.metadata import PackageNotFoundError, version

    except ImportError:
        from pkg_resources import DistributionNotFound, get_distribution

        try:
            version = get_distribution("clustercron").version
        except DistributionNotFound:
            pass
    else:
        try:
            version = version("clustercron")
        except PackageNotFoundError:
            pass
    return version
