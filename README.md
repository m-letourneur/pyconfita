# PyConfita: Confita-like for Python

A Python library that simplifies reading configuration values from multiple key-value stores/backends with ordered evaluation and flexible configuration management.

## Table of Contents

- [Disclaimer](#disclaimer)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
  - [Evaluation Order](#evaluation-order)
  - [Explicit Type Conversion](#explicit-type-conversion)
  - [Case Sensitivity](#case-sensitivity)
- [Backends](#backends)
  - [EnvBackend - Environment Variables](#envbackend---environment-variables)
  - [DictBackend - Python Dictionary](#dictbackend---python-dictionary)
  - [FileBackend - YAML Files](#filebackend---yaml-files)
  - [StringBackend - JSON/YAML Strings](#stringbackend---jsonyaml-strings)
  - [VaultBackend - HashiCorp Vault](#vaultbackend---hashicorp-vault)
- [Advanced Usage](#advanced-usage)
  - [Loading Multiple Keys with get_struct](#loading-multiple-keys-with-get_struct)
  - [Vault Caching](#vault-caching)
  - [Custom Logging](#custom-logging)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)
- [API Reference](#api-reference)

## Disclaimer

Free implementation of the GO library [Confita](https://github.com/heetch/confita).

## Features

- **Multiple Backend Support:**
  - Environment variables (`EnvBackend`)
  - YAML files (`FileBackend`)
  - Python dictionaries (`DictBackend`)
  - HashiCorp Vault (`VaultBackend`)
  - JSON/YAML strings (`StringBackend`)
- **Ordered Evaluation:** Backends are evaluated in the order specified. The last non-`None` value is returned, allowing for cascading configuration with clear override priorities.
- **Type Safety:** Explicit type conversion for `str`, `bool`, `int`, `float`
- **Case Sensitivity Control:** Optional case-insensitive key lookup
- **Bulk Loading:** Load multiple configuration keys with type definitions using `get_struct`
- **Vault Caching:** Optional caching for Vault backend to reduce API calls
- **Flexible Configuration:** Mix and match backends to create sophisticated configuration hierarchies

## Installation

```bash
pip install pyconfita
```

## Quick Start

```python
from pyconfita import Confita, DictBackend, EnvBackend, DummyLoggingInterface

# Create a simple configuration loader
logger = DummyLoggingInterface()
config = Confita(
    logger=logger,
    backends=[
        DictBackend({"API_KEY": "default-key", "DEBUG": "false"}),
        EnvBackend(),  # Environment variables override dict values
    ],
)

# Get configuration values
api_key = config.get("API_KEY")  # Returns value from env or fallback to dict
debug = config.get("DEBUG", type=bool)  # Returns boolean value

print(f"API Key: {api_key}")
print(f"Debug mode: {debug}")
```

## Core Concepts

### Evaluation Order

Backends are evaluated in the order they appear in the `backends` list. The **last non-`None` value** is returned. This allows you to create a configuration cascade with clear override priorities.

```python
import os
from pyconfita import Confita, DictBackend, EnvBackend, DummyLoggingInterface

logger = DummyLoggingInterface()
os.environ["DATABASE_URL"] = "postgres://prod-server/db"

# Environment variables override dict values
config = Confita(
    logger=logger,
    backends=[
        DictBackend({"DATABASE_URL": "postgres://localhost/db"}),
        EnvBackend(),  # Last backend has highest priority
    ],
)

assert config.get("DATABASE_URL") == "postgres://prod-server/db"

# Reverse the order to change priorities
config = Confita(
    logger=logger,
    backends=[
        EnvBackend(),
        DictBackend({"DATABASE_URL": "postgres://localhost/db"}),  # Now highest priority
    ],
)

assert config.get("DATABASE_URL") == "postgres://localhost/db"
```

**Important:** Empty strings (`""`) are considered valid values and will override previous backends.

```python
from pyconfita import Confita, DictBackend, DummyLoggingInterface

logger = DummyLoggingInterface()
config = Confita(
    logger=logger,
    backends=[
        DictBackend({"KEY": "value"}),
        DictBackend({"KEY": ""}),  # Empty string overrides
    ],
)

assert config.get("KEY") == ""  # Empty string is returned
```

### Explicit Type Conversion

Type conversion must be explicitly requested using the `type` parameter. Supported types are: `str`, `bool`, `int`, `float`. Default type is `str`.

```python
from pyconfita import Confita, DictBackend, DummyLoggingInterface

logger = DummyLoggingInterface()
config = Confita(
    logger=logger,
    backends=[
        DictBackend({
            "ENABLE_FEATURE": "true",
            "MAX_CONNECTIONS": "100",
            "TIMEOUT": "30.5",
            "APP_NAME": "myapp",
        }),
    ],
)

# String values (default)
app_name = config.get("APP_NAME")  # Returns "myapp"
assert isinstance(app_name, str)

# Boolean conversion
enable_feature = config.get("ENABLE_FEATURE", type=bool)
assert enable_feature is True
assert isinstance(enable_feature, bool)

# Integer conversion
max_connections = config.get("MAX_CONNECTIONS", type=int)
assert max_connections == 100
assert isinstance(max_connections, int)

# Float conversion
timeout = config.get("TIMEOUT", type=float)
assert timeout == 30.5
assert isinstance(timeout, float)
```

**Boolean Conversion Rules:**
- Any string containing "t" or "T" (case-insensitive) is converted to `True`
- All other strings are converted to `False`

```python
from pyconfita import Confita, DictBackend, DummyLoggingInterface

logger = DummyLoggingInterface()
config = Confita(
    logger=logger,
    backends=[
        DictBackend({
            "BOOL_1": "true",
            "BOOL_2": "True",
            "BOOL_3": "t",
            "BOOL_4": "false",
            "BOOL_5": "False",
            "BOOL_6": "no",
        }),
    ],
)

assert config.get("BOOL_1", type=bool) is True
assert config.get("BOOL_2", type=bool) is True
assert config.get("BOOL_3", type=bool) is True
assert config.get("BOOL_4", type=bool) is False  # Contains 't' but also other chars
assert config.get("BOOL_5", type=bool) is False
assert config.get("BOOL_6", type=bool) is False
```

### Case Sensitivity

By default, key lookups are case-sensitive. You can disable this to allow case-insensitive lookups.

```python
from pyconfita import Confita, DictBackend, DummyLoggingInterface

logger = DummyLoggingInterface()

# Case-sensitive (default)
config = Confita(
    logger=logger,
    backends=[DictBackend({"API_KEY": "secret-key"})],
    case_sensitive=True,  # This is the default
)

assert config.get("API_KEY") == "secret-key"
assert config.get("api_key") is None  # Different case, not found
assert config.get("Api_Key") is None

# Case-insensitive
config = Confita(
    logger=logger,
    backends=[DictBackend({"API_KEY": "secret-key"})],
    case_sensitive=False,
)

assert config.get("API_KEY") == "secret-key"
assert config.get("api_key") == "secret-key"  # Works!
assert config.get("Api_Key") == "secret-key"  # Works!
```

**Case-insensitive lookup strategy:** When `case_sensitive=False`, PyConfita tries the following variations in order:
1. Original case
2. UPPERCASE
3. lowercase

The first non-`None` value is used.

## Backends

### EnvBackend - Environment Variables

Reads configuration from environment variables.

```python
import os
from pyconfita import Confita, EnvBackend, DummyLoggingInterface

# Set environment variables
os.environ["DATABASE_HOST"] = "localhost"
os.environ["DATABASE_PORT"] = "5432"

logger = DummyLoggingInterface()
config = Confita(logger=logger, backends=[EnvBackend()])

host = config.get("DATABASE_HOST")
port = config.get("DATABASE_PORT", type=int)

print(f"Database: {host}:{port}")  # Output: Database: localhost:5432
```

### DictBackend - Python Dictionary

Reads configuration from a Python dictionary. Useful for default values or testing.

```python
from pyconfita import Confita, DictBackend, DummyLoggingInterface

logger = DummyLoggingInterface()
defaults = {
    "APP_NAME": "MyApp",
    "VERSION": "1.0.0",
    "DEBUG": "false",
}

config = Confita(logger=logger, backends=[DictBackend(defaults)])

app_name = config.get("APP_NAME")
version = config.get("VERSION")
debug = config.get("DEBUG", type=bool)

print(f"{app_name} v{version} (debug={debug})")
```

### FileBackend - YAML Files

Reads configuration from YAML files.

**Example YAML file (`config.yaml`):**
```yaml
database:
  host: localhost
  port: 5432
  name: myapp

api:
  key: secret-key-123
  timeout: 30

features:
  enable_cache: true
```

**Note:** FileBackend reads flat key-value pairs from YAML files. Nested structures are not supported directly.

**Flat YAML file (`config.yaml`):**
```yaml
DATABASE_HOST: localhost
DATABASE_PORT: 5432
API_KEY: secret-key-123
ENABLE_CACHE: true
```

```python
from pyconfita import Confita, FileBackend, DummyLoggingInterface

logger = DummyLoggingInterface()
config = Confita(
    logger=logger,
    backends=[FileBackend("/path/to/config.yaml")],
)

db_host = config.get("DATABASE_HOST")
db_port = config.get("DATABASE_PORT", type=int)
api_key = config.get("API_KEY")
enable_cache = config.get("ENABLE_CACHE", type=bool)

print(f"Database: {db_host}:{db_port}")
```

### StringBackend - JSON/YAML Strings

Parses JSON or YAML formatted strings. Useful for configuration passed as command-line arguments or from external sources.

```python
from pyconfita import Confita, StringBackend, DummyLoggingInterface

logger = DummyLoggingInterface()

# JSON string
json_config = '{"API_KEY": "secret", "TIMEOUT": 30}'
config = Confita(
    logger=logger,
    backends=[StringBackend(json_config)],
)

assert config.get("API_KEY") == "secret"
assert config.get("TIMEOUT") == 30

# Also supports single-quoted JSON (will be converted)
single_quoted = "{'API_KEY': 'secret', 'DEBUG': 'true'}"
config = Confita(
    logger=logger,
    backends=[StringBackend(single_quoted)],
)

assert config.get("API_KEY") == "secret"
assert config.get("DEBUG", type=bool) is True

# YAML string
yaml_config = """
API_KEY: secret
TIMEOUT: 30
DEBUG: true
"""
config = Confita(
    logger=logger,
    backends=[StringBackend(yaml_config)],
)

assert config.get("API_KEY") == "secret"
```

### VaultBackend - HashiCorp Vault

Reads secrets from HashiCorp Vault. Supports caching and custom paths.

**Basic Usage:**

```python
from pyconfita import Confita, VaultBackend, DummyLoggingInterface

logger = DummyLoggingInterface()
config = Confita(
    logger=logger,
    backends=[
        VaultBackend(
            logger=logger,
            default_key_path="secret/data/myapp",
            url="http://localhost:8200",
            readiness_timeout=30,
        ),
    ],
)

# Read from default path
db_password = config.get("DATABASE_PASSWORD")

# Read from custom path
api_key = config.get("API_KEY", path="secret/data/external-services")
```

**Parameters:**
- `logger`: Logging interface (required)
- `default_key_path`: Default Vault path for key lookups (default: `"config-__CLUSTER_NAME__/data-team"`)
- `url`: Vault agent URL (default: `"http://localhost:8200"`)
- `readiness_timeout`: Timeout in seconds to wait for Vault agent (default: `30`)
- `enable_cache`: Enable caching of Vault responses (default: `False`)
- `cache_maxsize`: Maximum number of cached items (default: `1024`, only if `enable_cache=True`)
- `cache_ttl`: Cache time-to-live in seconds (default: `600`, only if `enable_cache=True`)

## Advanced Usage

### Loading Multiple Keys with get_struct

The `get_struct` method allows you to load multiple configuration keys at once with type definitions. This is more efficient than calling `get` multiple times, especially with the VaultBackend.

```python
import os
from pyconfita import Confita, EnvBackend, DictBackend, DummyLoggingInterface

logger = DummyLoggingInterface()
os.environ["API_KEY"] = "prod-key-123"
os.environ["MAX_WORKERS"] = "10"

config = Confita(
    logger=logger,
    backends=[
        DictBackend({
            "APP_NAME": "MyApp",
            "DEBUG": "false",
            "TIMEOUT": "30.5",
            "MAX_WORKERS": "4",
        }),
        EnvBackend(),  # Overrides dict values
    ],
)

# Define schema with types
schema = {
    "APP_NAME": str,
    "API_KEY": str,
    "DEBUG": bool,
    "TIMEOUT": float,
    "MAX_WORKERS": int,
    "OPTIONAL_KEY": str,  # May be None
}

# Load all values at once
config_dict = config.get_struct(schema)

print(config_dict)
# Output:
# {
#     'APP_NAME': 'MyApp',
#     'API_KEY': 'prod-key-123',
#     'DEBUG': False,
#     'TIMEOUT': 30.5,
#     'MAX_WORKERS': 10,
#     'OPTIONAL_KEY': None
# }
```

**Benefits of `get_struct`:**
- Load multiple keys in a single call
- Automatic type conversion for all keys
- Returns a dictionary with all keys (missing keys are `None`)
- More efficient with VaultBackend (reduces API calls)

### Vault Caching

Enable caching for the VaultBackend to reduce API calls and improve performance.

```python
from pyconfita import Confita, VaultBackend, DummyLoggingInterface

logger = DummyLoggingInterface()
config = Confita(
    logger=logger,
    backends=[
        VaultBackend(
            logger=logger,
            default_key_path="secret/data/myapp",
            enable_cache=True,
            cache_maxsize=2048,  # Cache up to 2048 keys
            cache_ttl=300,  # Cache for 5 minutes
        ),
    ],
)

# First call hits Vault
api_key = config.get("API_KEY")

# Subsequent calls within TTL use cache
api_key = config.get("API_KEY")  # Retrieved from cache
```

### Custom Logging

Implement a custom logging interface to integrate with your application's logging system.

```python
from pyconfita import Confita, EnvBackend, LoggingInterface

class MyLogger(LoggingInterface):
    def log(self, level="info", message=None, **kwargs):
        print(f"[{level.upper()}] {message}")

logger = MyLogger()
config = Confita(
    logger=logger,
    backends=[EnvBackend()],
)

value = config.get("MY_KEY")  # Logs debug messages about backend evaluation
```

The `LoggingInterface` requires a `log` method with the following signature:
```python
def log(self, level="info", message=None, **kwargs):
    pass
```

For simple use cases, use `DummyLoggingInterface` which does nothing:
```python
from pyconfita import DummyLoggingInterface

logger = DummyLoggingInterface()  # No-op logger
```

## Complete Examples

### Example 1: Multi-tier Configuration

```python
import os
from pyconfita import (
    Confita,
    DictBackend,
    FileBackend,
    EnvBackend,
    DummyLoggingInterface,
)

logger = DummyLoggingInterface()

# Set environment variable
os.environ["DATABASE_HOST"] = "prod-db.example.com"

# Create configuration with multiple tiers
config = Confita(
    logger=logger,
    backends=[
        DictBackend({  # Tier 1: Defaults
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "myapp",
            "DEBUG": "false",
        }),
        FileBackend("./config/production.yaml"),  # Tier 2: File config
        EnvBackend(),  # Tier 3: Environment (highest priority)
    ],
)

# Load all configuration
schema = {
    "DATABASE_HOST": str,
    "DATABASE_PORT": int,
    "DATABASE_NAME": str,
    "DEBUG": bool,
}

app_config = config.get_struct(schema)
print(app_config)
# {
#     'DATABASE_HOST': 'prod-db.example.com',  # From env
#     'DATABASE_PORT': 5432,  # From file or dict
#     'DATABASE_NAME': 'myapp',  # From file or dict
#     'DEBUG': False  # From file or dict
# }
```

### Example 2: Using Vault with Fallbacks

```python
from pyconfita import (
    Confita,
    VaultBackend,
    DictBackend,
    EnvBackend,
    DummyLoggingInterface,
)

logger = DummyLoggingInterface()

config = Confita(
    logger=logger,
    backends=[
        DictBackend({  # Defaults
            "API_KEY": "development-key",
            "DATABASE_PASSWORD": "dev-password",
        }),
        VaultBackend(  # Production secrets
            logger=logger,
            default_key_path="secret/data/myapp/prod",
            enable_cache=True,
        ),
        EnvBackend(),  # Override for local testing
    ],
)

# Get secrets with automatic fallback
api_key = config.get("API_KEY")  # Uses Vault in prod, defaults in dev
db_password = config.get("DATABASE_PASSWORD")
```

### Example 3: Case-insensitive Configuration

```python
import os
from pyconfita import Confita, EnvBackend, DummyLoggingInterface

logger = DummyLoggingInterface()

# Different casing in environment
os.environ["api_key"] = "key-from-env"
os.environ["DATABASE_URL"] = "postgres://localhost/db"

config = Confita(
    logger=logger,
    backends=[EnvBackend()],
    case_sensitive=False,  # Enable case-insensitive lookup
)

# All these work
assert config.get("api_key") == "key-from-env"
assert config.get("API_KEY") == "key-from-env"
assert config.get("Api_Key") == "key-from-env"

assert config.get("database_url") == "postgres://localhost/db"
assert config.get("DATABASE_URL") == "postgres://localhost/db"
```

## Best Practices

1. **Order backends from lowest to highest priority:**
   ```python
   backends=[
       DictBackend({...}),  # Defaults
       FileBackend("config.yaml"),  # File config
       EnvBackend(),  # Environment overrides
   ]
   ```

2. **Use `get_struct` for loading multiple values:**
   - More efficient, especially with VaultBackend
   - Clearer intent and better type safety

3. **Always specify types explicitly:**
   ```python
   # Bad: May return string "true" instead of boolean
   debug = config.get("DEBUG")

   # Good: Guaranteed to return boolean
   debug = config.get("DEBUG", type=bool)
   ```

4. **Enable Vault caching in production:**
   ```python
   VaultBackend(
       logger=logger,
       enable_cache=True,
       cache_ttl=600,  # 10 minutes
   )
   ```

5. **Use case-insensitive mode carefully:**
   - Only enable if you need to support multiple casing conventions
   - Be aware that it may mask configuration errors

6. **Provide defaults with DictBackend:**
   - Always have a DictBackend with sensible defaults as the first backend
   - Makes configuration more resilient and easier to test

## API Reference

### Confita

```python
class Confita:
    def __init__(
        self,
        logger: LoggingInterface,
        backends: List[Backend],
        case_sensitive: bool = True,
    ):
        """
        Initialize configuration loader.

        :param logger: Logging interface implementation
        :param backends: List of backends (evaluated in order)
        :param case_sensitive: Enable case-sensitive key lookup (default: True)
        """

    def get(self, key: str, **kwargs) -> Optional[Any]:
        """
        Get configuration value for key.

        :param key: Configuration key
        :param type: Optional type for conversion (str, bool, int, float)
        :param path: Optional custom path (VaultBackend only)
        :return: Configuration value or None
        """

    def get_struct(self, schema: dict, **kwargs) -> dict:
        """
        Load multiple configuration values with type definitions.

        :param schema: Dictionary mapping keys to types
        :return: Dictionary with all keys (None for missing values)
        """
```

### Backends

```python
class EnvBackend:
    """Read from environment variables."""
    pass

class DictBackend:
    """Read from Python dictionary."""
    def __init__(self, data: dict):
        pass

class FileBackend:
    """Read from YAML file."""
    def __init__(self, file_path: str):
        pass

class StringBackend:
    """Parse JSON/YAML string."""
    def __init__(self, input_str: str):
        pass

class VaultBackend:
    """Read from HashiCorp Vault."""
    def __init__(
        self,
        logger: LoggingInterface,
        default_key_path: str = "config-__CLUSTER_NAME__/data-team",
        url: str = "http://localhost:8200",
        readiness_timeout: int = 30,
        enable_cache: bool = False,
        cache_maxsize: int = 1024,
        cache_ttl: int = 600,
    ):
        pass
```

### LoggingInterface

```python
class LoggingInterface:
    """Base logging interface."""
    def log(self, level="info", message=None, **kwargs):
        pass

class DummyLoggingInterface(LoggingInterface):
    """No-op logging interface."""
    pass
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See the [LICENSE](LICENSE) file for details.
