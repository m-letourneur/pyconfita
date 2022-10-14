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

        for bk in self.backends:
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
            if tmp_value:  # Override if defined only
                _value = tmp_value
                self.logger.zlog(
                    **{
                        "level": "debug",
                        "message": {"message": f"{bk.name} reads {key} = {tmp_value}"},
                    }
                )

        self.logger.zlog(
            **{
                "level": "debug",
                "message": {"message": f"Final value read for {key} = {_value}"},
            }
        )
        return _value
