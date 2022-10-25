from unittest import mock

from pyconfita.backend.vault.vault import Backend, KeyRef
from pyconfita.logging_interface import DummyLoggingInterface

MOCK_VAULT_URL = "http://localhost:8200"
MOCK_VAULT_DATA = {"data": {"k_1": "secret_1", "k_2": "secret_2"}}
MOCK_VAULT_DATA_PATH = "path1"
MOCK_VAULT_STORE = {"path1": MOCK_VAULT_DATA}
MOCK_VAULT_TIMEOUT = 1
MOCK_LOGGER = DummyLoggingInterface()


def mocked_requests_read(path, *args, **kwargs):
    return MOCK_VAULT_STORE.get(path, None)


def test__get_kv_store():
    """Test _get_kv_store"""
    with mock.patch(
        "hvac.v1.Client.read", side_effect=lambda x: mocked_requests_read(x)
    ):
        bk = Backend(
            MOCK_LOGGER,
            readiness_timeout=MOCK_VAULT_TIMEOUT,
            default_key_path=MOCK_VAULT_DATA_PATH,
            enable_cache=True,
        )
        res = bk._get_kv_store(MOCK_VAULT_DATA_PATH)
        assert res == MOCK_VAULT_DATA.get("data")


def mocked_is_ready(*args, **kwargs):
    return True


def test__get_kv_store_when_ready():
    """Test _get_kv_store_when_ready"""
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
                enable_cache=True,
            )
            res = bk._get_kv_store_when_ready(MOCK_VAULT_DATA_PATH)
            assert res == MOCK_VAULT_DATA.get("data")


def test__cache_kv_store():
    """
    Test _cache_kv_store
    """
    bk = Backend(
        MOCK_LOGGER,
        readiness_timeout=MOCK_VAULT_TIMEOUT,
        default_key_path=MOCK_VAULT_DATA_PATH,
        enable_cache=True,
    )

    kv_store = {"unseen": "sofar", "other": "one"}
    path = "path_to_kv"
    _ = bk._cache_kv_store(path, kv_store)
    # Check one key-value pair has been cached
    key_ref = KeyRef(path=path, key="unseen")
    assert len(bk.cache.items()) == 2
    assert bk.cache.get(key_ref.get_cache_key()) == "sofar"

    # Check all k-v are cached...
    for k, v in kv_store.items():
        key_ref = KeyRef(path=path, key=k)
        assert bk.cache.get(key_ref.get_cache_key()) == v


def test_get():
    """Test get with caching enabled"""
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
                enable_cache=True,
            )
            res = bk.get("k_1")
            assert res == "secret_1"
            res = bk.get("k_2")
            assert res == "secret_2"
