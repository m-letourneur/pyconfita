import os
from typing import Optional, Any

import yaml
import json

from pyconfita.backend.backend import Backend as _Backend


class Backend(_Backend):
    """
    Load key from file (YAML or JSON)
    """

    name = "file"

    def __init__(self, file_path: str, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        _kv = None

        if not os.path.isfile(file_path):
            raise Exception("File not found")

        try:
            # Try as JSON
            with open(file_path, "r") as f:
                _kv = json.loads(f.read())
        except Exception as e:
            pass
        if _kv is None:
            try:
                # Try as YAML
                with open(file_path, "r") as f:
                    raw_yml = "".join(f.readlines())
                    _kv = yaml.safe_load(raw_yml)
            except Exception as e:
                pass

        if _kv is None:
            _kv = {}

        self.kv = _kv

    def _get(self, key: str, **kwargs) -> Optional[Any]:
        """

        :param key:
        :param kwargs:
        :return:
        """
        return self.kv.get(key)
