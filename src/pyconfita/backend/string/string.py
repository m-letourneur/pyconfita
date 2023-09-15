from typing import Optional, Any
import yaml
import json

from pyconfita.backend.backend import Backend as _Backend


class Backend(_Backend):
    """
    Parse string as YAML/JSON, convert to dict, load key from dict
    """

    name = "string"

    def __init__(self, input_str: str, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        _kv = None
        if input_str is not None:
            try:
                _kv = json.loads(input_str)
            except Exception as e:
                try:
                    _input_str = input_str.strip().replace("'", '"')
                    _kv = json.loads(_input_str)
                except Exception as ee:
                    pass

            if _kv is None:
                try:
                    _kv = yaml.safe_load(input_str)
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
