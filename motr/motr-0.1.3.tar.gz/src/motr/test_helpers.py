from cement import TestApp

import motr.motr_app


class MOTRTest(TestApp, motr.motr_app.MOTR):
    """A sub-class of MOTR that is better suited for testing."""

    class Meta:
        label = "motr"
