import time
from dataclasses import dataclass
from typing import Optional, Any, Dict
import hvac
import requests
from cacheout import Cache

from pyconfita.backend.backend import Backend as _Backend
from pyconfita.logging_interface import LoggingInterface

KEY_NOT_FOUND_IN_CACHE = "__key_not_found_in_cache__"


@dataclass
class KeyRef:
    """
    Reference a key-value path in Vault such that
    value = hvac.Client.read(path).get("data").get(key)
    """

    path: str
    key: str

    def get_cache_key(self) -> str:
        return f"{self.key}"


class Backend(_Backend):
    """
    Load a key from Vault key-value store.
    """

    name: str = "vault"

    def __init__(
        self,
        logger: LoggingInterface,
        default_key_path: str = "config-__CLUSTER_NAME__/data-team",
        url: str = "http://localhost:8200",
        readiness_timeout: int = 30,
        enable_cache: bool = False,
        *args,
        **kwargs,
    ):
        """
        Initializer for the Vault Client, communicating with a Vault agent.
        By default, the Vault agent is reachable locally in clear without
        authentication.

        :param logger: logging interface
        :param default_key_path: default path for key-value lookup
        :param url: Vault agent URL, defaults to http://localhost:8200
        :param readiness_timeout: timeout, defaults to 30 seconds
        :param enable_cache: bool, True to enable caching key-value stores
        """
        self.default_key_path = default_key_path
        self.url = url
        self.readiness_timeout = readiness_timeout
        self.cli = hvac.Client(self.url)
        if logger is None:
            raise Exception("Vault logger must not be None")
        self.logger = logger
        self.cache = None
        self.enable_cache = enable_cache
        if self.enable_cache:
            maxsize = kwargs.get("cache_maxsize", 1024)
            ttl = kwargs.get("cache_ttl", 600)  # Defaults to 10min
            self.cache = Cache(maxsize=maxsize, ttl=ttl)

    def is_agent_ready(self) -> bool:
        """
        Wait for Vault agent readiness until timeout.

        :return:
        """
        is_ready = False
        start_time = time.time()
        t = 0
        while not is_ready and t < self.readiness_timeout:
            try:
                res = requests.get(self.url)
                is_ready = res.status_code in [200, 201, 202, 203, 204]
            except Exception as e:
                self.logger.log(
                    **{
                        "level": "debug",
                        "message": {"message": f"Waiting Vault agent, t = {t}"},
                    }
                )
                is_ready = False

            # Increment timer
            time.sleep(1)
            t = time.time() - start_time

        if not is_ready:
            self.logger.log(
                **{
                    "level": "error",
                    "message": {"message": f"Vault agent is not ready"},
                }
            )

        self.logger.log(
            **{
                "level": "info",
                "message": {"message": f"Vault agent is ready!"},
            }
        )

        return is_ready

    def _get_kv_store(self, path: str) -> dict:
        """
        Return key-value store at path
        """
        try:
            kv_store = self.cli.read(path)
            return kv_store.get("data", {})
        except Exception as e:
            self.logger.log(
                **{
                    "level": "error",
                    "message": {
                        "message": f"[Vault] Error reading key-value store"
                        f" at path={path}: {e}"
                    },
                }
            )
            raise e

    def _get_key(self, k_ref: KeyRef) -> Optional[str]:
        """
        Read value for key in key-value store. Defaults to None.

        :param k_ref:
        :return:
        """
        v = None
        try:
            kv_store = self.cli.read(k_ref.path)
            return kv_store.get("data", {}).get(k_ref.key, None)
        except Exception as e:
            self.logger.log(
                **{
                    "level": "error",
                    "message": {
                        "message": f"[Vault] Error reading key={k_ref.key}"
                        f" at path={k_ref.path}: {e}"
                    },
                }
            )
            raise e

    def _get_multiple_keys(self, k_refs: Dict[str, KeyRef]) -> dict:
        """
        Read all key-value references in struct, and returns values
        wrapped in struct.

        E.g.:
            obj  =  {
                "var_name_1": KeyRef(path="path/in/vault/1", key="key1")
                "var_name_2": KeyRef(path="path/in/vault/2", key="key2")
                ...
            }

        Returns
            {
                "var_name": "value1"
                "var_name_2": "value2"
                ...
            }

        :param k_refs:
        :return:
        """
        return {kname: self._get_key(sec_ref) for kname, sec_ref in k_refs.items()}

    def _get_key_when_ready(self, k_ref: KeyRef) -> Optional[str]:
        """
        Call _get on key when Vault agent is ready.

        :param k_ref:
        :return:
        """
        is_ready = self.is_agent_ready()
        if is_ready:
            return self._get_key(k_ref)
        else:
            self.logger.log(
                **{
                    "level": "error",
                    "message": {
                        "message": f"[Vault] Failed to communicate with Vault agent. Cannot retrieve secret."
                    },
                }
            )
            raise Exception(
                "[Vault] Failed to communicate with Vault agent. Cannot retrieve secret."
            )

    def _get_multiple_keys_when_ready(self, k_refs: Dict[str, KeyRef]) -> dict:
        """
        Call _get_multiple_keys when Vault agent is ready.

        :param k_refs:
        :return:
        """
        is_ready = self.is_agent_ready()
        if is_ready:
            return self._get_multiple_keys(k_refs)
        else:
            self.logger.log(
                **{
                    "level": "error",
                    "message": {
                        "message": f"[Vault] Failed to communicate with Vault"
                        f" agent. Cannot retrieve secrets."
                    },
                }
            )
            raise Exception(
                "[Vault] Failed to communicate with Vault agent. Cannot "
                "retrieve secrets."
            )

    def _get_kv_store_when_ready(self, path: str) -> dict:
        """
        Return key-value store at path when Vault agent is ready.

        """
        is_ready = self.is_agent_ready()
        if is_ready:
            return self._get_kv_store(path=path)
        else:
            self.logger.log(
                **{
                    "level": "error",
                    "message": {
                        "message": f"[Vault] Failed to communicate with Vault"
                        f" agent. Cannot retrieve key-value"
                        f" store at path={path}"
                    },
                }
            )
            raise Exception(
                f"[Vault] Failed to communicate with Vault"
                f" agent. Cannot retrieve key-value"
                f" store at path={path}"
            )

    def _cache_kv_store(self, path: str, kv_store: dict):
        """
        Cache key-value store (loaded from path) if caching is enabled.
        """
        if self.enable_cache:
            for k, v in kv_store.items():
                cache_key = KeyRef(path=path, key=k).get_cache_key()
                try:
                    self.cache.set(cache_key, v)
                    self.logger.log(
                        **{
                            "level": "debug",
                            "message": {"message": f"[Vault] Set key {k}" f" in cache"},
                        }
                    )
                except Exception as e:
                    self.logger.log(
                        **{
                            "level": "error",
                            "message": {
                                "message": f"[Vault] Failed to cache value"
                                f" for key {k}"
                            },
                        }
                    )
                    raise e

    def _get(self, key: str, **kwargs) -> Optional[Any]:
        """
        Get key
        - from cache if enabled
        - directly when Vault is ready

        Default path is used if no one provided in kwargs.

        :param key:
        :param kwargs:
        :return:
        """
        _value = None

        _path = kwargs.get("path", self.default_key_path)
        k_ref = KeyRef(path=_path, key=key)
        if self.enable_cache:
            self.logger.log(
                **{
                    "level": "debug",
                    "message": {
                        "message": f"[Vault][cache enabled] try to get key"
                        f" {key} from cache"
                    },
                }
            )
            _value = self.cache.get(
                k_ref.get_cache_key(), default=KEY_NOT_FOUND_IN_CACHE
            )
            if _value == KEY_NOT_FOUND_IN_CACHE:
                self.logger.log(
                    **{
                        "level": "debug",
                        "message": {
                            "message": f"[Vault] key {key} not" f" found in cache"
                        },
                    }
                )
                kv_store = self._get_kv_store_when_ready(path=k_ref.path)
                self._cache_kv_store(path=k_ref.path, kv_store=kv_store)
                _value = self.cache.get(k_ref.get_cache_key(), default=None)
            else:
                self.logger.log(
                    **{
                        "level": "debug",
                        "message": {
                            "message": f"[Vault][cache enabled] key"
                            f" {key} found in cache"
                        },
                    }
                )
        else:
            self.logger.log(
                **{
                    "level": "debug",
                    "message": {
                        "message": f"[Vault][cache disabled] call"
                        f" _get_key_when_ready"
                    },
                }
            )
            _value = self._get_key_when_ready(k_ref)
        return _value

    def get_struct(self, schema: dict, **kwargs) -> dict:
        """ """
        _struct = {}

        _path = kwargs.get("path", self.default_key_path)
        kv_store = self._get_kv_store_when_ready(path=_path)
        for key, v_type in schema.items():
            _value = kv_store.get(key)
            if _value is not None:
                _value = self._cast(_value, v_type=v_type)
            _struct[key] = _value

        return _struct
