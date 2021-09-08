import pytest


def test_import(main):
    assert main


def test_main_basic(main, test_helpers):
    def run():
        pass

    app = test_helpers.MOTRTest()
    app.run = run
    main.main(lambda: app)
    assert app.exit_code == 0


@pytest.mark.parametrize("debug", (False, True))
def test_assert(main, test_helpers, debug):
    def run():
        assert False

    app = test_helpers.MOTRTest(debug=debug)
    app.run = run
    main.main(lambda: app)
    assert app.exit_code == 1


@pytest.mark.parametrize("debug", (False, True))
def test_error(main, test_helpers, exc, debug):
    def run():
        raise exc.MOTRError("Test exception")

    app = test_helpers.MOTRTest(debug=debug)
    app.run = run
    main.main(lambda: app)
    assert app.exit_code == 1


def test_signal(main, test_helpers):
    def run():
        raise main.CaughtSignal(-1, None)

    app = test_helpers.MOTRTest()
    app.run = run
    main.main(lambda: app)
    assert app.exit_code == 0
