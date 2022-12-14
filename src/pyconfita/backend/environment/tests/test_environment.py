import os

from pyconfita.backend.environment.environment import Backend


def test_backend():
    """Test backend get"""
    bk = Backend()

    env_var = "foo"
    exp_value = "bar"
    _val = bk.get(env_var)
    assert _val is None

    os.environ.setdefault(env_var, exp_value)
    _val = bk.get(env_var)
    assert _val == exp_value

    # Unset variable should return None
    del os.environ[env_var]
    _val = bk.get(env_var)
    assert _val is None
