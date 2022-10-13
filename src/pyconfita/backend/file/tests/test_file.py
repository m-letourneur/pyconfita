import os
import pytest
from pyconfita.backend.file.file import Backend


def test_backend():
    """Test backend get"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "vars.yaml")
    bk = Backend(file_path)

    assert bk.get("bool", **{"type": bool})
    assert bk.get("int", **{"type": int}) == 10
    assert bk.get("txt") == "world"


def test_backend_wrong_extension():
    """Test backend get when input file has unsupported extension"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "vars.txt")
    with pytest.raises(Exception):
        _ = Backend(file_path)
