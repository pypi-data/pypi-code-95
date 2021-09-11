from pbcommon.FuturesConfig import FuturesConfig


def test_futures_config():
    cfg = FuturesConfig('./tests/FuturesConfigTestFile.json')
    cfg.load()

    assert len(cfg.data) == 2
    assert len([r for r in cfg.data if r['name'] == 'ES']) > 0
    assert len([r for r in cfg.data if r['name'] == 'FAKE']) == 0
