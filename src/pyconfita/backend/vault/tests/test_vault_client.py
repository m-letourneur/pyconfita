import time
from dataclasses import dataclass
from unittest import mock
import pytest
import requests

from pyconfita.backend.vault.vault import Backend, KeyRef
from pyconfita.logging_interface import LoggingInterface

MOCK_VAULT_URL = "http://localhost:8200"
MOCK_VAULT_DATA = {"data": {"k_1": "secret_1", "k_2": "secret_2"}}
MOCK_VAULT_DATA_PATH = "path1"
MOCK_VAULT_STORE = {"path1": MOCK_VAULT_DATA}
MOCK_VAULT_TIMEOUT = 1
MOCK_LOGGER = LoggingInterface()


def mocked_requests_read(path, *args, **kwargs):
    return MOCK_VAULT_STORE.get(path, None)


def test_mock_vault_client_read():
    """Assess that patch for Vault client read returns the default dict when
    path is defined. Returns None if path not found"""
    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        bk = Backend(
            MOCK_LOGGER,
            readiness_timeout=MOCK_VAULT_TIMEOUT,
            default_key_path=MOCK_VAULT_DATA_PATH,
        )

        res = bk.cli.read(MOCK_VAULT_DATA_PATH)
        assert res == MOCK_VAULT_DATA

        res = bk.cli.read("unknown path")
        assert res is None


def test__get_key():
    """Check _get returns value if exists, defaulting to None"""
    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        bk = Backend(MOCK_LOGGER, readiness_timeout=MOCK_VAULT_TIMEOUT)

        k_ref = KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_1")
        res = bk._get_key(k_ref)
        assert res == "secret_1"

        secret = KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_2")
        res = bk._get_key(secret)
        assert res == "secret_2"

        secret = KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_3")
        res = bk._get_key(secret)
        assert res is None


def test__get_multiple_keys():
    """Check _get_multiple_keys returns values wrapped in struct.
    Values defaults to None"""
    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        bk = Backend(
            MOCK_LOGGER,
            readiness_timeout=MOCK_VAULT_TIMEOUT,
            default_key_path=MOCK_VAULT_DATA_PATH,
        )

        obj = {
            "k_secret_1": KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_1"),
            "k_secret_2": KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_2"),
            "k_secret_3": KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_3"),
        }

        res = bk._get_multiple_keys(obj)
        assert "k_secret_1" in res.keys()
        assert "k_secret_2" in res.keys()
        assert "k_secret_3" in res.keys()
        assert res.get("k_secret_1") == "secret_1"
        assert res.get("k_secret_2") == "secret_2"
        assert res.get("k_secret_3") is None


def mocked_is_ready(*args, **kwargs):
    return True


def test_get():
    """Test get. Ensure values are correctly retrieved after waiting for Vault
    agent is ready"""
    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        with mock.patch(
            "pyconfita.backend.vault.vault.Backend.is_agent_ready",
            side_effect=mocked_is_ready,
        ):
            bk = Backend(
                MOCK_LOGGER,
                readiness_timeout=MOCK_VAULT_TIMEOUT,
                default_key_path=MOCK_VAULT_DATA_PATH,
            )
            res = bk.get("k_1")
            assert res == "secret_1"


def test__get_multiple_keys_when_ready():
    """Test _get_multiple_keys_when_ready. Ensure values are correctly
    retrieved after waiting for Vault agent is ready"""
    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        with mock.patch(
            "pyconfita.backend.vault.vault.Backend.is_agent_ready",
            side_effect=mocked_is_ready,
        ):
            bk = Backend(
                MOCK_LOGGER,
                readiness_timeout=MOCK_VAULT_TIMEOUT,
                default_key_path=MOCK_VAULT_DATA_PATH,
            )

            obj = {
                "k_secret_1": KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_1"),
                "k_secret_2": KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_2"),
                "k_secret_3": KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_3"),
            }

            res = bk._get_multiple_keys_when_ready(obj)
            assert "k_secret_1" in res.keys()
            assert "k_secret_2" in res.keys()
            assert "k_secret_3" in res.keys()
            assert res.get("k_secret_1") == "secret_1"
            assert res.get("k_secret_2") == "secret_2"
            assert res.get("k_secret_3") is None


def mocked_is_ready_false(*args, **kwargs):
    return requests.Response()


def test__get_key_when_not_ready():
    """Test _get_key_when_ready. Ensure Exception raised when Vault agent cannot
    be reached"""
    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        with mock.patch(
            "pyconfita.backend.vault.vault.Backend.is_agent_ready",
            side_effect=mocked_is_ready_false,
        ):
            bk = Backend(
                MOCK_LOGGER,
                readiness_timeout=MOCK_VAULT_TIMEOUT,
                default_key_path=MOCK_VAULT_DATA_PATH,
            )
            with pytest.raises(Exception):
                _ = bk._get_key_when_ready(KeyRef(path=MOCK_VAULT_DATA_PATH, key="k_1"))


def test__get_multiple_key_when_not_ready():
    """Test _get_multiple_keys_when_ready. Ensure Exception raised when Vault
    agent cannot be reached"""
    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        with mock.patch(
            "pyconfita.backend.vault.vault.Backend.is_agent_ready",
            side_effect=mocked_is_ready_false,
        ):
            bk = Backend(
                MOCK_LOGGER,
                readiness_timeout=MOCK_VAULT_TIMEOUT,
                default_key_path=MOCK_VAULT_DATA_PATH,
            )
            with pytest.raises(Exception):
                _ = bk._get_multiple_keys_when_ready({})


@dataclass
class MockResponse:
    status_code: int


def mocked_readiness(*args, **kwargs):
    return MockResponse(status_code=200)


def mocked_readiness_failure(*args, **kwargs):
    return MockResponse(status_code=404)


def mocked_readiness_timeout(*args, **kwargs):
    time.sleep(2)
    return MockResponse(status_code=404)


def test_is_agent_ready():
    """Check is_agent_ready behavior"""
    with mock.patch("requests.get", side_effect=mocked_readiness):
        timeout = 1
        bk = Backend(MOCK_LOGGER, readiness_timeout=timeout)
        is_ready = bk.is_agent_ready()
        assert is_ready

    with mock.patch("requests.get", side_effect=mocked_readiness_failure):
        timeout = 1
        bk = Backend(MOCK_LOGGER, readiness_timeout=timeout)
        is_ready = bk.is_agent_ready()
        assert not is_ready

    with mock.patch("requests.get", side_effect=mocked_readiness_timeout):
        timeout = 1
        bk = Backend(MOCK_LOGGER, readiness_timeout=timeout)
        is_ready = bk.is_agent_ready()
        assert not is_ready
