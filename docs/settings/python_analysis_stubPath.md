# python.analysis.stubPath

Specifies a custom directory path for type stub files (.pyi).

## Description

Type stub files (`.pyi`) contain type information for Python modules. This setting allows you to specify a custom directory where Pylance/Pyright should look for stub files, in addition to the standard locations.

## Default Value

- **Pylance**: `null` (uses default stub locations)
- **Pyright**: `null` (uses default stub locations)

## Supported Values

- `null` - Use default stub locations
- `string` - Absolute or relative path to a directory containing `.pyi` files

## Default Stub Locations

Pylance/Pyright looks for stub files in these locations by default:

1. **Project stubs**: Directory specified by `stubPath` (if set)
2. **typeshed**: Vendored typeshed stubs
3. **Installed stubs**: `types-` packages installed via pip (e.g., `types-requests`)
4. **Inline stubs**: `.pyi` files alongside `.py` files

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.stubPath": "./stubs"
}
```

### pyrightconfig.json

```json
{
  "stubPath": "./stubs"
}
```

### pyproject.toml

```toml
[tool.pyright]
stubPath = "./stubs"
```

## Examples

### Custom Stubs Directory

```
my-project/
├── stubs/
│   ├── mymodule.pyi
│   └── third_party/
│       └── untyped_lib.pyi
├── src/
│   └── main.py
└── pyrightconfig.json
```

```json
{
  "stubPath": "./stubs"
}
```

### Absolute Path

```json
{
  "stubPath": "/home/user/.local/share/stubs"
}
```

## Creating Stub Files

### Basic Stub

```python
# mymodule.pyi
def greet(name: str) -> str: ...

class Calculator:
    def add(self, a: int, b: int) -> int: ...
    def multiply(self, a: float, b: float) -> float: ...
```

### Stub for Third-Party Library

```python
# untyped_library.pyi
from typing import List, Dict, Any

def fetch_data(url: str) -> Dict[str, Any]: ...

class Client:
    def __init__(self, api_key: str) -> None: ...
    def request(self, endpoint: str, **kwargs: Any) -> Any: ...
```

## When to Use

### 1. Untyped Third-Party Libraries

When a library doesn't have type stubs:

```bash
# Create a stub file for the library
mkdir -p stubs
touch stubs/untyped_library.pyi
```

```json
{
  "stubPath": "./stubs"
}
```

### 2. Custom Type Definitions

When you need to override or extend existing type definitions:

```python
# stubs/overrides.pyi
from typing import TypeVar

_T = TypeVar('_T')

def custom_function(x: _T) -> _T: ...
```

### 3. Monorepo Shared Stubs

When multiple packages share the same stub definitions:

```
monorepo/
├── shared-stubs/
│   └── common.pyi
├── packages/
│   ├── pkg-a/
│   └── pkg-b/
```

```json
{
  "stubPath": "../shared-stubs"
}
```

## Related Settings

- [`python.analysis.typeshedPaths`](python_analysis_typeshedPaths.md) - Additional typeshed paths
- [`python.analysis.useLibraryCodeForTypes`](python_analysis_useLibraryCodeForTypes.md) - Use library code for types when stubs unavailable
- [`python.analysis.extraPaths`](python_analysis_extraPaths.md) - Additional import paths

## Troubleshooting

### Stubs Not Found

If stubs aren't being recognized:

1. **Check path**: Ensure `stubPath` points to the correct directory
2. **Verify stub names**: Stub files should match module names (e.g., `mymodule.pyi` for `mymodule`)
3. **Check syntax**: Ensure stub files have valid Python syntax
4. **Restart language server**: Run "Python: Restart Language Server"

### Conflicting Stubs

If you have conflicting stub definitions:

1. **Check precedence**: Project stubs override installed stubs
2. **Use specific paths**: Point to specific stub directories
3. **Remove duplicates**: Ensure only one stub exists per module

## Best Practices

1. **Use types packages**: Prefer installing `types-*` packages over custom stubs
2. **Contribute upstream**: Submit stub improvements to typeshed
3. **Keep stubs minimal**: Only define what's necessary
4. **Version control**: Add stubs to version control

## See Also

- [Pyright Stub Files](https://microsoft.github.io/pyright/#/type-stubs)
- [Typeshed Repository](https://github.com/python/typeshed)
- [PEP 561 - Stub Support](https://peps.python.org/pep-0561/)