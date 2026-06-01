# python.analysis.includeAliasesFromUserFiles

Controls whether type aliases defined in user files are included in analysis and autocomplete.

## Description

Type aliases allow you to give a name to a complex type, making your code more readable. This setting controls whether Pylance/Pyright recognizes and uses type aliases defined in your project's Python files.

## Default Value

- **Pylance**: `true`
- **Pyright**: `true`

## Supported Values

- `true` - Include type aliases from user files in analysis
- `false` - Do not include type aliases from user files

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.includeAliasesFromUserFiles": true
}
```

### pyrightconfig.json

```json
{
  "includeAliasesFromUserFiles": true
}
```

### pyproject.toml

```toml
[tool.pyright]
includeAliasesFromUserFiles = true
```

## Examples

### Basic Type Alias

```python
# types.py
from typing import List, Dict

UserId = int
UserDatabase = Dict[UserId, Dict[str, str]]

# main.py
from types import UserId, UserDatabase

def get_user(db: UserDatabase, user_id: UserId) -> Dict[str, str]:
    return db.get(user_id, {})
```

With `includeAliasesFromUserFiles` enabled:
- `UserId` is recognized as `int`
- `UserDatabase` is recognized as `Dict[int, Dict[str, str]]`
- Autocomplete works correctly

### Type Alias with Generics

```python
# types.py
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

StringContainer = Container[str]
IntContainer = Container[int]

# main.py
from types import StringContainer

def process(container: StringContainer) -> str:
    return container.value  # Type is correctly inferred as str
```

### NewType Aliases

```python
# types.py
from typing import NewType

UserId = NewType('UserId', int)
ProductId = NewType('ProductId', int)

# main.py
from types import UserId, ProductId

def get_user(user_id: UserId) -> None:
    pass

def get_product(product_id: ProductId) -> None:
    pass

# Pylance correctly distinguishes between UserId and ProductId
user_id = UserId(123)
get_user(user_id)  # Correct
get_product(user_id)  # Error: Expected ProductId, got UserId
```

## When to Disable

You might want to disable this setting in these scenarios:

1. **Performance**: Very large codebases with many complex type aliases
2. **Conflicts**: Type aliases causing confusion or incorrect type inference
3. **Debugging**: To isolate issues with type alias resolution

## Related Settings

- [`python.analysis.typeCheckingMode`](python_analysis_typeCheckingMode.md) - Control type checking strictness
- [`python.analysis.useLibraryCodeForTypes`](python_analysis_useLibraryCodeForTypes.md) - Use library code for types
- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing

## Troubleshooting

### Type Aliases Not Recognized

If type aliases aren't being recognized:

1. **Check setting**: Ensure `includeAliasesFromUserFiles` is `true`
2. **Check import**: Ensure the alias is properly imported
3. **Restart language server**: Run "Python: Restart Language Server"
4. **Check typeCheckingMode**: Ensure type checking is enabled

### Incorrect Type Inference

If type inference with aliases is incorrect:

1. **Check alias definition**: Ensure the alias is properly defined
2. **Use explicit types**: Add explicit type annotations
3. **Simplify aliases**: Break down complex aliases

## Best Practices

1. **Use descriptive names**: Choose clear names for type aliases
2. **Document aliases**: Add docstrings or comments explaining the alias
3. **Group related aliases**: Keep related aliases in the same module
4. **Use NewType for distinct types**: Use `NewType` for semantically different types

## See Also

- [Python Type Aliases](https://docs.python.org/3/library/typing.html#type-aliases)
- [NewType Documentation](https://docs.python.org/3/library/typing.html#newtype)
- [Type Checking Mode](python_analysis_typeCheckingMode.md)