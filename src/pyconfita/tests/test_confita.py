import os
from unittest import mock

from pyconfita import (
    Confita,
    LoggingInterface,
    EnvBackend,
    FileBackend,
    DictBackend,
    VaultBackend,
)

MOCK_VAULT_URL = "http://localhost:8200"
MOCK_VAULT_DATA = {"data": {"K_1": "secret_1", "K_2": "secret_2", "K_3": "secret_3"}}
MOCK_VAULT_DATA_PATH = "path1"
MOCK_VAULT_STORE = {"path1": MOCK_VAULT_DATA}
MOCK_VAULT_TIMEOUT = 10
MOCK_LOGGER = LoggingInterface()


def mocked_requests_read(path, *args, **kwargs):
    return MOCK_VAULT_STORE.get(path, None)


def mocked_is_ready(*args, **kwargs):
    return True


def test_get_multiple_backends():
    """Test get. Ensure values are correctly retrieved after waiting for Vault
    agent is ready."""

    # Set env variables
    os.environ.setdefault("K_3", "secret_3_from_environment")

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
            # From dict
            assert c.get("K_5") == "secret_5"
            # From env
            # Overrides Vault
            assert c.get("K_3") == "secret_3_from_environment"  # Overrides Vault


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
