from typing import Any, Optional


class Backend:
    """
    Base class representing a key-value store/backend.
    """

    name: str

    def get(self, key: str, **kwargs) -> Optional[Any]:
        """
        Returns value found at key in key-value backend.
        Type conversion is handled by _cast method.
        """
        return self._cast(self._get(key, **kwargs), **kwargs)

    def _get(self, key: str, **kwargs) -> Optional[Any]:
        """
        Returns raw value found at key in key-value backend.
        Defaults to None if key not found in store.
        """
        return NotImplementedError

    def _cast(self, v: Any, **kwargs):
        """
        Convert value into type as defined by kwargs['type'] parameter.
        Supported types: [str, bool, float, int].
        Default conversion type is `str`.
        If value is None, returns None.
        """
        # Default expected type is string
        _type = kwargs.get("type", str)
        if _type not in [str, bool, float, int]:
            raise Exception(
                "Unsupported type conversion. Support for str," " bool, float, int."
            )

        if v is None:
            return v

        if isinstance(v, _type):
            # Right type
            return v

        # Mismatch: value is not None and type is incorrect
        if isinstance(v, str):
            if _type == bool:
                v = True if "t" in v.lower() else False
                return v
            if _type == int:
                v = int(v)
                return v
            if _type == float:
                v = float(v)
                return v

        else:
            raise Exception(
                "Type conversion cannot be achieved when variable" " is not a string"
            )
