# reportUnknownVariableType

Reports when a variable's type cannot be determined by the type checker.

## Description

This diagnostic is raised when Pylance/Pyright cannot infer the type of a variable and the variable is used in a way that requires type information. This typically occurs when:

- A variable is assigned from an untyped source
- Type annotations are missing and cannot be inferred
- The variable comes from a library without type stubs

## Default Severity

- **Warning** (in basic/strict mode)
- **None** (in standard mode)

## Examples

### Example 1: Unknown Type from Function Return

```python
def get_data():  # No return type annotation
    return {"key": "value"}

data = get_data()  # Warning: Type of "data" is unknown
print(data["key"])  # Cannot verify if "key" is valid
```

**Fix**: Add type annotations:

```python
from typing import Dict

def get_data() -> Dict[str, str]:
    return {"key": "value"}

data = get_data()  # data is Dict[str, str]
print(data["key"])
```

### Example 2: Unknown Type from Unannotated Variable

```python
config = load_config()  # Warning: Type of "config" is unknown

if config.get("debug"):  # Cannot verify "get" method exists
    enable_debug()
```

**Fix**: Add explicit type annotation:

```python
from typing import Any, Dict

config: Dict[str, Any] = load_config()

if config.get("debug"):
    enable_debug()
```

### Example 3: Unknown Type from Dynamic Attribute

```python
obj = some_factory.create()  # Warning: Type of "obj" is unknown
result = obj.process()  # Cannot verify "process" method exists
```

**Fix**: Add type annotation or use type guard:

```python
from mymodule import Processor

obj: Processor = some_factory.create()
result = obj.process()
```

### Example 4: Unknown Type in Comprehension

```python
items = [x for x in get_items()]  # Warning: Type of "items" is unknown
for item in items:
    print(item.value)  # Cannot verify "value" attribute exists
```

**Fix**: Annotate the function or use explicit types:

```python
from typing import List
from mymodule import Item

def get_items() -> List[Item]:
    ...

items = [x for x in get_items()]  # items is List[Item]
for item in items:
    print(item.value)
```

### Example 5: Unknown Type from Unannotated Class Attribute

```python
class Config:
    def __init__(self):
        self.settings = {}  # Warning: Type of "settings" is unknown

config = Config()
print(config.settings["key"])  # Cannot verify subscript is valid
```

**Fix**: Annotate the class attribute:

```python
from typing import Dict, Any

class Config:
    settings: Dict[str, Any]

    def __init__(self):
        self.settings = {}

config = Config()
print(config.settings["key"])
```

## Common Causes

| Cause | Description | Solution |
|-------|-------------|----------|
| Missing return type | Function has no return type annotation | Add return type annotation |
| Unannotated variable | Variable assigned without type hint | Add explicit type annotation |
| Untyped library | Library lacks type stubs | Use `# type: ignore` or create stubs |
| Dynamic code | Type determined at runtime | Use type assertions or guards |
| Complex inference | Type too complex to infer | Add explicit type annotation |

## Suppressing the Diagnostic

### For Specific Variables

Use explicit type annotation:

```python
from typing import Any

unknown_var: Any = get_unknown()
```

Or use type ignore comment:

```python
unknown_var = get_unknown()  # type: ignore
```

### Configuration

In `pyrightconfig.json`:

```json
{
  "reportUnknownVariableType": "none"
}
```

### Using TYPE_CHECKING

For types only needed for type checking:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mymodule import MyType

def process():
    var: "MyType" = get_value()
```

## Related Diagnostics

- [`reportUnknownParameterType`](reportUnknownParameterType.md) - Parameter type is unknown
- [`reportUnknownMemberType`](reportUnknownMemberType.md) - Member type is unknown
- [`reportUnknownArgumentType`](reportUnknownArgumentType.md) - Argument type cannot be determined
- [`reportUnknownLambdaType`](reportUnknownLambdaType.md) - Lambda expression type is unknown

## See Also

- [Type Narrowing Guide](../howto/type-narrowing.md)
- [Pyright Type Inference](https://microsoft.github.io/pyright/#/type-inference)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)