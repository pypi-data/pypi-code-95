try:
    import importlib.metadata

    __version__ = importlib.metadata.version(__name__)
except ImportError:
    import pkg_resources

    __version__ = pkg_resources.get_distribution(__name__).version
