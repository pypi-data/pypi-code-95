import pytest

from dataclass_wizard.utils.dict_helper import DictWithLowerStore


def test_dict_with_lower_store():
    dls = DictWithLowerStore(Accept='application/json')

    # KeyError: The normal lookup is *case-sensitive*!
    with pytest.raises(KeyError):
        assert dls['aCCEPT'] == 'application/json'

    # The rest of these assertions will work without an issue.

    assert dls['Accept'] == 'application/json'
    assert dls.get('aCCEPT') == 'application/json'

    assert dls.get_key('aCCEPT') == 'Accept'
    assert list(dls) == ['Accept']


def test_dict_with_lower_store_complex():
    dls = DictWithLowerStore(Accept='application/json')

    # KeyError: The normal lookup is *case-sensitive*!
    with pytest.raises(KeyError):
        assert dls['aCCEPT'] == 'application/json'

    # The rest of these assertions will work without an issue.

    assert dls['Accept'] == 'application/json'
    assert dls.get('aCCEPT') == 'application/json'

    assert dls.get_key('aCCEPT') == 'Accept'
    assert list(dls) == ['Accept']
