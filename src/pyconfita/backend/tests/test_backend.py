import pytest
from pyconfita.backend.backend import Backend


def test__cast():
    """Test _cast method"""
    bk = Backend()

    # Default to string
    exp_value = "s"
    _value = bk._cast("s")
    assert _value == exp_value

    exp_value = "true"
    _value = bk._cast("true")
    assert _value == exp_value

    exp_value = True
    _value = bk._cast("true", **{"type": bool})
    assert _value == exp_value

    # Match
    exp_value = True
    _value = bk._cast(True, **{"type": bool})
    assert _value == exp_value

    # Bool casting
    exp_value = True
    _value = bk._cast("T", **{"type": bool})
    assert _value == exp_value

    exp_value = False
    _value = bk._cast("f", **{"type": bool})
    assert _value == exp_value

    # Int / float
    exp_value = 10
    _value = bk._cast("10", **{"type": int})
    assert _value == exp_value
    assert isinstance(_value, int)

    exp_value = 10
    _value = bk._cast("10", **{"type": float})
    assert _value == exp_value
    assert isinstance(_value, float)

    # Match
    _value = bk._cast(10, **{"type": int})
    assert isinstance(_value, int)

    # Match
    _value = bk._cast(10.0, **{"type": float})
    assert isinstance(_value, float)

    # Mismatch with value not as a string
    with pytest.raises(Exception):
        _value = bk._cast(10, **{"type": bool})

    # Unsupported type conversion
    with pytest.raises(Exception):
        _value = bk._cast("s", **{"type": list})
