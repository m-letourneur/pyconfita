from typing import List, Optional, Any

from pyconfita.backend.backend import Backend
from pyconfita.logging_interface import LoggingInterface


class Confita:
    logger: LoggingInterface
    backends: List[Backend]

    def __init__(
        self, logger: LoggingInterface, backends: List[Backend], *args, **kwargs
    ):
        """

        :param backends: list of key-value backends. Ordered in opposite
        order of precedence.
        :param args:
        :param kwargs:
        """
        self.logger = logger
        self.backends = backends

    def get(self, key: str, **kwargs) -> Optional[Any]:
        """

        :param key:
        :param kwargs:
        :return:
        """
        _value = None
        for bk in self.backends:
            tmp_value = bk.get(key, **kwargs)
            if tmp_value:
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


if __name__ == "__main__":
    c = Confita(LoggingInterface(), [])
    print(c.backends)
