# PyConfita: Confita-like for Python

Library that ease loading a value from multiple key-value stores/backends with ordered evaluation.

## Disclaimer

Free implementation of the GO library [Confita](https://github.com/heetch/confita).

## Features

- Backends/stores supported:
  - Environment variables (`EnvBackend`);
  - File (YAML format) (`FileBackend`);
  - Python dictionary object (`DictBackend`);
  - Vault key-value store (`VaultBackend`);
- Backends evaluation order: precedence of the evaluation is directly set by the order of backends in `Confita.backends` list. The last not `None` evaluated value is returned;
- Explicit type casting supported for `str, bool, int, float`.

## Quickstart

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
assert c.get("BOOL_2", **{"type": bool}) # Explicit type conversion requested

c = Confita(
    logger=dumb_logger,
    backends=[
        EnvBackend(),
        DictBackend({"KEY": "VALUE"}),
    ],
)

assert c.get("KEY") == "VALUE" # Dict backend overrides previous backends' values
```

## Tests

```
make test 
```

