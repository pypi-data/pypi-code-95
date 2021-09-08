from typing import Callable

from cement.core.exc import CaughtSignal

import motr.core.exc
import motr.motr_app


def main(
    app_class: Callable[[], motr.motr_app.MOTR] = motr.motr_app.MOTR
) -> None:
    with app_class() as app:
        try:
            app.run()

        except AssertionError as e:
            print("AssertionError > %s" % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback

                traceback.print_exc()

        except motr.core.exc.MOTRError as e:
            print("MOTRError > %s" % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback

                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print("\n%s" % e)
            app.exit_code = 0
