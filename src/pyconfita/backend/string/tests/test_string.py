from pyconfita.backend.string.string import Backend


def test_backend_with_json():
    """Test backend with JSON"""
    d = (
        '{"lower": "cased",'
        ' "upper": "CASED",'
        ' "int": 1,'
        ' "float": 1.0,'
        ' "bool": true,'
        ' "none": null}'
    )

    bk = Backend(d)

    # Keys found
    _val = bk.get("lower")
    assert _val == "cased"
    _val = bk.get("upper")
    assert _val == "CASED"
    _val = bk.get("int", type=int)
    assert _val == 1
    _val = bk.get("float", type=float)
    assert _val == 1.0
    _val = bk.get("bool", type=bool)
    assert _val == True
    _val = bk.get("none")
    assert _val is None

    # Key not found
    _val = bk.get("UNKNOWN")
    assert _val is None


def test_backend_json_simple_quotes():
    """Test backend with JSON"""
    d = (
        "{'lower': 'cased',"
        "'upper': 'CASED',"
        "'int': 1,"
        "'float': 1.0,"
        "'bool': true,"
        "'none': null}"
    )

    bk = Backend(d)

    # Keys found
    _val = bk.get("lower")
    assert _val == "cased"
    _val = bk.get("upper")
    assert _val == "CASED"
    _val = bk.get("int", type=int)
    assert _val == 1
    _val = bk.get("float", type=float)
    assert _val == 1.0
    _val = bk.get("bool", type=bool)
    assert _val == True
    _val = bk.get("none")
    assert _val is None

    # Key not found
    _val = bk.get("UNKNOWN")
    assert _val is None


def test_backend_yaml():
    """Test backend with YAML"""
    d = (
        "lower: cased\n"
        "upper: CASED\n"
        "int: 1\n"
        "float: 1.0\n"
        "bool: true\nnone: null"
    )

    bk = Backend(d)

    # Keys found
    _val = bk.get("lower")
    assert _val == "cased"
    _val = bk.get("upper")
    assert _val == "CASED"
    _val = bk.get("int", type=int)
    assert _val == 1
    _val = bk.get("float", type=float)
    assert _val == 1.0
    _val = bk.get("bool", type=bool)
    assert _val == True
    _val = bk.get("none")
    assert _val is None

    # Key not found
    _val = bk.get("UNKNOWN")
    assert _val is None


def test_backend_edge_cases():
    """Test backend"""

    # Empty string
    d = ""
    bk = Backend(d)
    _val = bk.get("UNKNOWN")
    assert _val is None

    # Empty dict
    d = "{}"
    bk = Backend(d)
    _val = bk.get("UNKNOWN")
    assert _val is None

    # Empty dict with spaces
    d = " {} "
    bk = Backend(d)
    _val = bk.get("UNKNOWN")
    assert _val is None
