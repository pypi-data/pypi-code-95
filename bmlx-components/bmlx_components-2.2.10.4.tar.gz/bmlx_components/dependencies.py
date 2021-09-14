def make_required_install_packages():
    return [
        "kazoo==2.7.0",
        "pre-commit==2.4.0",
        "kafka-python==2.0.1",
        "lz4==3.1.0",
    ]


def make_required_test_packages():
    """Prepare extra packages needed for 'python setup.py test'."""
    return []
