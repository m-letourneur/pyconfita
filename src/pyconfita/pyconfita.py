from typing import List, Optional, Any

from pyconfita.backend.backend import Backend
from pyconfita.logging_interface import LoggingInterface


class Confita:
    logger: LoggingInterface
    backends: List[Backend]
    case_sensitive: bool = True

    def __init__(
        self,
        logger: LoggingInterface,
        backends: List[Backend],
        case_sensitive: bool = True,
        *args,
        **kwargs,
    ):
        """

        :param logger:
        :param backends: list of key-value backends. Order sets the
        evaluation order for values.
        :param args:
        :param kwargs:
        """
        self.logger = logger
        self.backends = backends
        self.case_sensitive = case_sensitive

    def get(self, key: str, **kwargs) -> Optional[Any]:
        """
        Read the value at key in all the backends.
        Returns the last not None value found in order of the list of
        backends. Returns None if not found.

        :param key:
        :param kwargs:
        :return:
        """
        _value = None

        _all_values = []
        for bk in self.backends:
            tmp_value = None
            if self.case_sensitive:
                # Initial casing for key
                tmp_value = bk.get(key, **kwargs)
            else:
                # Try reading with casing variations on key
                tmp_value = (
                    bk.get(key, **kwargs)
                    or bk.get(key.upper(), **kwargs)
                    or bk.get(key.lower(), **kwargs)
                )
            self.logger.log(
                **{
                    "level": "debug",
                    "message": {"message": f"{bk.name} reads {key} = {tmp_value}"},
                }
            )
            _all_values.append(tmp_value)
        self.logger.log(
            **{
                "level": "debug",
                "message": {"message": f"All values read for {key} = {_all_values}"},
            }
        )
        d_values = [v for v in _all_values if v is not None]
        self.logger.log(
            **{
                "level": "debug",
                "message": {
                    "message": f"All defined values read for {key} = {d_values}"
                },
            }
        )
        if len(d_values) > 0:
            _value = d_values[-1]

        self.logger.log(
            **{
                "level": "debug",
                "message": {"message": f"Final value read for {key} = {_value}"},
            }
        )
        return _value

    def get_struct(self, schema: dict, **kwargs) -> dict:
        """
        Load all values defined in schema in a struct (dict) with identical
        backend precedence used in get: returns the last not None value found
        in order of the list of backends (defaults to None).
        """
        _struct = {k: None for k in schema.keys()}
        for bk in self.backends:
            tmp_struct = bk.get_struct(schema, **kwargs)
            for k, v in tmp_struct.items():
                if v is not None:
                    _struct[k] = v

        return _struct
