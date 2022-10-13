class LoggingInterface:
    """In-house logging interface"""

    def zlog(self, level=None, message=None):
        print(level, message)
