import os
from typing import Optional, Any

from pyconfita.backend.backend import Backend as _Backend


class Backend(_Backend):
    """
    Load key from environment (environment variable)
    """

    name: str = "environment"

    def _get(self, key: str, **kwargs) -> Optional[Any]:
        """

        :param key:
        :param kwargs:
        :return:
        """
        return os.environ.get(key)
