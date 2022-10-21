# PyConfita: Confita-like for Python

Library that ease reading a value from multiple key-value stores/backends with ordered evaluation.

## Disclaimer

Free implementation of the GO library [Confita](https://github.com/heetch/confita).

## Features

- Backends/stores supported:
  - Environment variables (`EnvBackend`);
  - File (YAML format) (`FileBackend`);
  - Python dictionary object (`DictBackend`);
  - Vault key-value store (`VaultBackend`);
- Backends evaluation order: directly set by the order of backends in `Confita.backends` list. The last not `None` evaluated value is returned;
- Explicit type conversion supported for `str, bool, int, float`;
- Case sensitivity option: option to read key with casing variations (uppercased, lowercased).

## Quickstart

```python
from pyconfita import (
    LoggingInterface,
    Confita,
    EnvBackend,
    DictBackend,
    VaultBackend,
    FileBackend
)
dumb_logger = LoggingInterface()
c = Confita(
    logger=dumb_logger,
    backends=[
        FileBackend("/abs/path/vars.yaml"),
        DictBackend({"FOO": "bar"}),
        VaultBackend(dumb_logger, default_key_path=f"path1"),
        EnvBackend(),
    ],
)

v = c.get("FOO") 
# At least DictBackend should evaluate it as not None
assert v is not None
# Type should be `str` 
assert isinstance(v, str)
```

### Evaluation order

Evaluation is performed in order of the list of backends.
Next backend has priority over previous backend to set the value.

```python
import os
from pyconfita import (
    LoggingInterface,
    Confita,
    EnvBackend,
    DictBackend
)
dumb_logger = LoggingInterface()

os.environ.setdefault("KEY", "VALUE_FROM_ENV")

c = Confita(
    logger=dumb_logger,
    backends=[
        DictBackend({
            "KEY": "VALUE",
            "BOOL_1": "false",
            "BOOL_2": "true"
        }),
        EnvBackend(),
    ],
)

assert c.get("KEY") == "VALUE_FROM_ENV" # Environment backend overrides previous backends' values
assert c.get("BOOL_1") == "false" # No implicit type conversion 
assert c.get("BOOL_2", v_type=bool) # Explicit type conversion requested

# Reverse evaluation order by reversing list of backends
c = Confita(
    logger=dumb_logger,
    backends=[
        EnvBackend(),
        DictBackend({"KEY": "VALUE"}),
    ],
)

assert c.get("KEY") == "VALUE" # Dict backend overrides previous backends' values
```

### Explicit type conversion

Type conversion must be explicit. Only `str, bool, int, float` types are supported.
Default type is `str`.

```python
from pyconfita import (
    LoggingInterface,
    Confita,
    DictBackend
)
dumb_logger = LoggingInterface()

c = Confita(
    logger=dumb_logger,
    backends=[
        DictBackend({
            "BOOL_1": "false",
            "BOOL_2": "true"
        }),
    ],
)

assert c.get("BOOL_1") == "false" # No implicit type conversion 
assert c.get("BOOL_2", v_type=bool) # Explicit type conversion requested

```

### Case sensitivity

```python
from pyconfita import (
    LoggingInterface,
    Confita,
    DictBackend
)
dumb_logger = LoggingInterface()

# Case sensitivity is enabled by default
c = Confita(
    logger=dumb_logger,
    backends=[DictBackend({"KEY": "VALUE"})],
)

assert c.get("KEY") == "VALUE" 
assert c.get("key") == None 

# Disable case sensitivity
c = Confita(
    logger=dumb_logger,
    backends=[DictBackend({"KEY": "VALUE"})],
    case_sensitive=False
)

assert c.get("KEY") == "VALUE" 
assert c.get("key") == "VALUE" 
```


