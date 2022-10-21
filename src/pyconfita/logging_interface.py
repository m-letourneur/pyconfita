class LoggingInterface:
    """Simple logging interface"""

    def log(self, level=None, message=None, *args, **kwargs) -> None:
        raise NotImplementedError


class DummyLoggingInterface(LoggingInterface):
    """
    Dummy logging interface.
    Do not use in production.
    """

    def log(self, level=None, message=None, *args, **kwargs) -> None:
        print(level, message)
