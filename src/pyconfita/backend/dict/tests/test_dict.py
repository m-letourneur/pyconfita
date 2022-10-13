from pyconfita.backend.dict.dict import Backend


def test_backend():
    """Test backend get"""
    d = {"lower": "cased"}
    bk = Backend(d)

    # key found
    _val = bk.get("lower")
    assert _val == "cased"

    # Key not found
    _val = bk.get("UNKNOWN")
    assert _val is None
