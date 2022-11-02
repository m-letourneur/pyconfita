import os
from unittest import mock

from pyconfita import (
    Confita,
    EnvBackend,
    FileBackend,
    DictBackend,
    VaultBackend,
    DummyLoggingInterface,
)

MOCK_VAULT_URL = "http://localhost:8200"
MOCK_VAULT_DATA = {"data": {"K_1": "secret_1", "K_2": "secret_2", "K_3": "secret_3"}}
MOCK_VAULT_DATA_PATH = "path1"
MOCK_VAULT_STORE = {"path1": MOCK_VAULT_DATA}
MOCK_VAULT_TIMEOUT = 10
MOCK_LOGGER = DummyLoggingInterface()


def mocked_requests_read(path, *args, **kwargs):
    return MOCK_VAULT_STORE.get(path, None)


def mocked_is_ready(*args, **kwargs):
    return True


def test_get_multiple_backends():
    """Test get. Ensure values are correctly retrieved after waiting for Vault
    agent is ready."""

    # Set env variables
    os.environ.setdefault("K_3", "secret_3_from_environment")
    os.environ.setdefault("K_7", "")

    # Dict file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    vars_file_path = os.path.join(dir_path, "vars.yaml")

    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        with mock.patch(
            "pyconfita.backend.vault.vault.Backend.is_agent_ready",
            side_effect=mocked_is_ready,
        ):
            c = Confita(
                logger=MOCK_LOGGER,
                backends=[
                    VaultBackend(MOCK_LOGGER, default_key_path=f"path1"),
                    FileBackend(vars_file_path),
                    DictBackend(
                        {
                            "K_5": "secret_5",
                        }
                    ),
                    EnvBackend(),
                ],
            )
            # From Vault
            assert c.get("K_1") == "secret_1"
            # From File
            assert c.get("K_2") == "secret_2_from_yml"  # Overrides Vault
            assert c.get("K_4") == "secret_4"
            assert c.get("K_8") is None
            # From dict
            assert c.get("K_5") == "secret_5"
            # From env
            # Overrides Vault
            assert c.get("K_3") == "secret_3_from_environment"  # Overrides Vault
            assert c.get("K_7") == ""
            assert c.get("K_UNKNOWN") is None


def test_get_ordered_backends():
    """Test get. Ensure values inverted when order of backends is
    reversed"""

    bk_1 = DictBackend({"K_1": "bk_1"})
    bk_2 = DictBackend({"K_1": "bk_2"})

    c = Confita(logger=MOCK_LOGGER, backends=[bk_1, bk_2])
    assert c.get("K_1") == "bk_2"

    # Reverse list of backends
    c = Confita(logger=MOCK_LOGGER, backends=[bk_2, bk_1])
    assert c.get("K_1") == "bk_1"


def test_case_sensitive():
    """Test get. Ensure values are read when case sensitivity is enabled or
    disabled"""
    # Lowercased key
    bk = DictBackend({"key_1": "bk_1"})
    c = Confita(logger=MOCK_LOGGER, backends=[bk], case_sensitive=True)
    assert c.get("key_1") == "bk_1"
    assert c.get("KEY_1") == None

    c = Confita(logger=MOCK_LOGGER, backends=[bk], case_sensitive=False)
    assert c.get("key_1") == "bk_1"
    assert c.get("KEY_1") == "bk_1"

    # Uppercased key
    bk = DictBackend({"KEY_1": "bk_1"})
    c = Confita(logger=MOCK_LOGGER, backends=[bk], case_sensitive=True)
    assert c.get("key_1") == None
    assert c.get("KEY_1") == "bk_1"

    c = Confita(logger=MOCK_LOGGER, backends=[bk], case_sensitive=False)
    assert c.get("key_1") == "bk_1"
    assert c.get("KEY_1") == "bk_1"


def test_empty_string():
    """Test get. Ensure values empty string values are not discarded"""

    bk_1 = DictBackend({"K_1": "bk_1"})
    bk_2 = DictBackend({"K_1": ""})

    c = Confita(logger=MOCK_LOGGER, backends=[bk_1, bk_2])
    assert c.get("K_1") == ""

    # Reverse list of backends
    c = Confita(logger=MOCK_LOGGER, backends=[bk_2, bk_1])
    assert c.get("K_1") == "bk_1"


def test_get_struct():
    """Test get_struct"""

    # Set env variables
    os.environ.setdefault("K_3", "secret_3_from_environment")
    os.environ.setdefault("K_7", "")

    # Dict file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    vars_file_path = os.path.join(dir_path, "vars.yaml")

    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        with mock.patch(
            "pyconfita.backend.vault.vault.Backend.is_agent_ready",
            side_effect=mocked_is_ready,
        ):
            c = Confita(
                logger=MOCK_LOGGER,
                backends=[
                    VaultBackend(MOCK_LOGGER, default_key_path=f"path1"),
                    FileBackend(vars_file_path),
                    DictBackend({"K_5": "secret_5", "K_10": "10.54"}),
                    EnvBackend(),
                ],
            )
            # From Vault
            schema = {
                "K_1": str,
                "K_2": str,
                "K_3": str,
                "K_4": str,
                "K_5": str,
                "K_6": str,
                "K_7": str,
                "K_8": str,
                "K_9": bool,
                "K_10": float,
            }

            _struct = c.get_struct(schema)
            assert len(_struct.keys()) == len(schema.keys())

            assert _struct.get("K_1") == "secret_1"
            # From File
            assert _struct.get("K_2") == "secret_2_from_yml"  # Overrides Vault
            assert _struct.get("K_4") == "secret_4"
            assert _struct.get("K_8") is None
            assert _struct.get("K_9") == True
            # From dict
            assert _struct.get("K_5") == "secret_5"
            assert _struct.get("K_10") == 10.54
            # From env
            # Overrides Vault
            assert _struct.get("K_3") == "secret_3_from_environment"  # Overrides Vault
            assert _struct.get("K_7") == ""
            assert _struct.get("K_UNKNOWN") is None
