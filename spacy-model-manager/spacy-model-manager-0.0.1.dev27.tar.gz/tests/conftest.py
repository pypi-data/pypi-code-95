import pytest

from spacy_model_manager.lib import SPACY_MODELS, uninstall_spacy_model


@pytest.fixture()
def zh_core_web_sm():
    """
    Make sure the model is not present before the test is run, and removed afterwards
    """
    model = SPACY_MODELS.zh_core_web_sm
    uninstall_spacy_model(model)
    yield model
    uninstall_spacy_model(model)
