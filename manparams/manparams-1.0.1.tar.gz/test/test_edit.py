from manparams.edit import deepupdate


def test_deepupdate_changes_all_keys_in_other():
    inputs = dict(a=1,
                  b=dict(c=1),
                  c=[dict(a=1), dict(a=2)])
    other = dict(a=2,
                 b=dict(c=2),
                 c=[dict(a=2)])

    deepupdate(inputs, other)

    assert inputs['a'] == other['a']
    assert inputs['b']['c'] == other['b']['c']
    assert inputs['c'][0]['a'] == other['c'][0]['a']
    assert len(inputs['c']) == 1


def test_deepupdate_creates_missing_keys_from_other():
    inputs = dict(a=1)
    other = dict(a=2,
                 b=dict(c=2),
                 c=[dict(a=2)])

    deepupdate(inputs, other)

    assert 'b' in inputs
    assert 'c' in inputs
