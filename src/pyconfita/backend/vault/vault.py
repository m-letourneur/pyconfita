import time
from dataclasses import dataclass
from typing import Optional, Any, Dict
import hvac
import requests

from pyconfita.backend.backend import Backend as _Backend
from pyconfita.logging_interface import LoggingInterface


@dataclass
class KeyRef:
    """
    Reference a key-value path in Vault such that
    value = hvac.Client.read(path).get("data").get(key)
    """

    path: str
    key: str


class Backend(_Backend):
    """
    Load a key from Vault key-value store.
    WARNING: Env variables keys are by default stored lowercased in Vault KV
    store.
    """

    name: str = "vault"

    def __init__(
        self,
        logger: LoggingInterface,
        default_key_path: str = "config-__CLUSTER_NAME__/data-team",
        url: str = "http://localhost:8200",
        readiness_timeout: int = 30,
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
        """
        self.default_key_path = default_key_path
        self.url = url
        self.readiness_timeout = readiness_timeout
        self.cli = hvac.Client(self.url)
        if logger is None:
            raise Exception("Vault logger must not be None")
        self.logger = logger

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
                self.logger.zlog(
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
            self.logger.zlog(
                **{
                    "level": "error",
                    "message": {"message": f"Vault agent is not ready"},
                }
            )

        self.logger.zlog(
            **{
                "level": "info",
                "message": {"message": f"Vault agent is ready!"},
            }
        )

        return is_ready

    def _get_key(self, k_ref: KeyRef) -> Optional[str]:
        """
        Read value for key. Defaults to None.

        :param k_ref:
        :return:
        """
        v = None
        try:
            kv_store = self.cli.read(k_ref.path)
            v = kv_store.get("data", {}).get(k_ref.key, None)
        except Exception as e:
            self.logger.zlog(
                **{
                    "level": "error",
                    "message": {
                        "message": f"[Vault] Error reading key={k_ref.key}"
                        f" at path={k_ref.path}: {e}"
                    },
                }
            )
        return v

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
            _value = self._get_key(k_ref)
            return _value
        else:
            self.logger.zlog(
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
            _values = self._get_multiple_keys(k_refs)
            return _values
        else:
            self.logger.zlog(
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

    def _get(self, key: str, **kwargs) -> Optional[Any]:
        """
        Get key when Vault is ready. Default path is used if no one provided
        in kwargs.

        :param key:
        :param kwargs:
        :return:
        """
        _path = kwargs.get("path", self.default_key_path)
        k_ref = KeyRef(path=_path, key=key)
        return self._get_key_when_ready(k_ref)
