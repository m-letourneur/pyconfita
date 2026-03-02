from typing import Any, Optional

from pyconfita.type_casting import cast


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

        This method is a wrapper around the type_casting.cast function.
        """
        # Default expected type is string
        _type = kwargs.get("type", str)
        if "v_type" in kwargs:
            _type = kwargs.get("v_type", str)

        try:
            return cast(v, _type)
        except ValueError as e:
            # Convert ValueError to Exception for backward compatibility
            raise Exception(str(e))

    def get_struct(self, schema: dict, **kwargs) -> dict:
        """
        Load all values defined in schema in a struct (dict) with type
        underlyong conversion
        """
        _struct = {}
        for key, _type in schema.items():
            _struct[key] = self.get(key, type=_type, **kwargs)

        return _struct
