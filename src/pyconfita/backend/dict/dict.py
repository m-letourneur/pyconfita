from typing import Optional, Any

from pyconfita.backend.backend import Backend as _Backend


class Backend(_Backend):
    """
    Load key from dict
    """

    name = "dict"

    def __init__(self, kv: dict, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        self.kv = kv

    def _get(self, key: str, **kwargs) -> Optional[Any]:
        """

        :param key:
        :param kwargs:
        :return:
        """
        return self.kv.get(key)
