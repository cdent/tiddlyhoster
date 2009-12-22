


def test_compile():
    try:
        import tiddlywebplugins.hoster
        assert True
    except ImportError, exc:
        assert False, exc
