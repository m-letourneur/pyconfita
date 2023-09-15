import os
import pytest
from pyconfita.backend.file.file import Backend


def test_backend_yaml():
    """Test backend get with YAML file"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "vars.yaml")
    bk = Backend(file_path)

    assert bk.get("bool", **{"type": bool})
    assert bk.get("int", **{"type": int}) == 10
    assert bk.get("txt") == "world"
    assert bk.get("null") is None
    assert bk.get("txt_empty_string") == ""


def test_backend_json():
    """Test backend get with JSON file"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "vars.json")
    bk = Backend(file_path)

    assert bk.get("bool", **{"type": bool})
    assert bk.get("int", **{"type": int}) == 10
    assert bk.get("txt") == "world"
    assert bk.get("null") is None
    assert bk.get("txt_empty_string") == ""


def test_backend_empty_yaml_file():
    """Test backend get with empty YAML file"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "empty_vars.yaml")
    bk = Backend(file_path)

    assert bk.get("bool") is None


def test_backend_empty_json_file():
    """Test backend get with empty JSON file"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "empty_vars.json")
    bk = Backend(file_path)

    assert bk.get("bool") is None
