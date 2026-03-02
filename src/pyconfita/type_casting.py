from typing import Any, Optional, Type, Union


def cast(
    value: Any,
    target_type: Type[Union[str, bool, int, float]] = str,
) -> Optional[Any]:
    """
    Convert value into the specified target type.

    Supported types: str, bool, float, int.
    Default conversion type is `str`.
    If value is None, returns None.

    Args:
        value: The value to convert
        target_type: The type to convert to (str, bool, int, or float)

    Returns:
        The converted value or None if input is None

    Raises:
        ValueError: If the target type is not supported
        ValueError: If type conversion cannot be achieved when variable is not a string

    Examples:
        >>> cast("123", int)
        123
        >>> cast("true", bool)
        True
        >>> cast("10.5", float)
        10.5
    """
    if target_type not in [str, bool, float, int]:
        raise ValueError(
            f"Unsupported type conversion: {target_type}. "
            "Supported types: str, bool, float, int."
        )

    if value is None:
        return value

    if isinstance(value, target_type):
        # Value is already the correct type
        return value

    # Value is not None and type is incorrect - conversion needed
    if isinstance(value, str):
        if target_type == bool:
            # Convert string to bool: 'true', 'True', 'T', 't' -> True
            return "t" in value.lower()
        if target_type == int:
            return int(value)
        if target_type == float:
            return float(value)
        if target_type == str:
            return value
    else:
        raise ValueError(
            f"Type conversion cannot be achieved when variable is not a string. "
            f"Got {type(value).__name__}, expected str."
        )
