import os
from typing import Optional, Any

import yaml

from pyconfita.backend.backend import Backend as _Backend


class Backend(_Backend):
    """
    Load key from file.
    WARNING: YAML support only!
    Extensions must be in ['.yaml', '.yml']
    """

    name = "file"

    def __init__(self, file_path: str, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        if not os.path.isfile(file_path):
            raise Exception("File not found")
        if ".yaml" not in file_path and ".yml" not in file_path:
            raise Exception("File extension should be .yaml or .yml")
        self.file_path = file_path

    def _get(self, key: str, **kwargs) -> Optional[Any]:
        """

        :param key:
        :param kwargs:
        :return:
        """
        _value = None
        with open(self.file_path, "r") as f:
            raw_yml = "".join(f.readlines())
            return yaml.safe_load(raw_yml).get(key)
