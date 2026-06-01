# Type Narrowing Guide

A comprehensive guide to understanding and using type narrowing in Pylance and Pyright.

## What is Type Narrowing?

Type narrowing is the process by which Pylance/Pyright refines the type of a variable within a specific code scope based on runtime checks. This allows for more precise type checking and better autocomplete suggestions.

## Type Narrowing Techniques

### 1. isinstance() Checks

The most common way to narrow types:

```python
def process(value: str | int) -> None:
    if isinstance(value, str):
        # value is narrowed to str
        reveal_type(value)  # str
        print(value.upper())
    else:
        # value is narrowed to int
        reveal_type(value)  # int
        print(value + 1)
```

### 2. is None / is not None Checks

Narrowing optional types:

```python
def process(value: str | None) -> None:
    if value is not None:
        # value is narrowed to str
        reveal_type(value)  # str
        print(value.upper())
    else:
        # value is narrowed to None
        reveal_type(value)  # None
```

### 3. Type Guards with isinstance()

Multiple type checks:

```python
def process(value: str | int | list[str]) -> None:
    if isinstance(value, str):
        # value is str
        print(value.upper())
    elif isinstance(value, int):
        # value is int
        print(value + 1)
    elif isinstance(value, list):
        # value is list[str]
        print(", ".join(value))
```

### 4. Literal Type Narrowing

Narrowing based on literal values:

```python
from typing import Literal

def process(status: Literal["open", "closed"]) -> None:
    if status == "open":
        # status is Literal["open"]
        reveal_type(status)  # Literal["open"]
    else:
        # status is Literal["closed"]
        reveal_type(status)  # Literal["closed"]
```

### 5. Discriminated Unions

Using a discriminator field:

```python
from typing import Literal

class Dog:
    kind: Literal["dog"]
    def bark(self) -> str:
        return "Woof!"

class Cat:
    kind: Literal["cat"]
    def meow(self) -> str:
        return "Meow!"

def process(animal: Dog | Cat) -> None:
    if animal.kind == "dog":
        # animal is Dog
        reveal_type(animal)  # Dog
        print(animal.bark())
    else:
        # animal is Cat
        reveal_type(animal)  # Cat
        print(animal.meow())
```

### 6. TypeGuard and TypeIs

Custom type guards for complex narrowing:

```python
from typing import TypeGuard, TypeIs

def is_string_list(values: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(v, str) for v in values)

def process(values: list[object]) -> None:
    if is_string_list(values):
        # values is narrowed to list[str]
        reveal_type(values)  # list[str]
        print(", ".join(values))

# TypeIs (Python 3.13+) - more precise narrowing
def is_non_empty_string(value: object) -> TypeIs[str]:
    return isinstance(value, str) and len(value) > 0

def process_value(value: str | None) -> None:
    if is_non_empty_string(value):
        # value is narrowed to str (not None)
        reveal_type(value)  # str
        print(value.upper())
```

## Common Pitfalls

### 1. Narrowing Lost After Reassignment

```python
def process(value: str | int | None) -> None:
    if value is not None:
        # value is str | int here
        temp = value
        # If value is reassigned, narrowing is lost
        value = None  # Now temp is still str | int
        reveal_type(temp)  # str | int (not narrowed)
```

### 2. Narrowing in Nested Scopes

```python
def process(value: str | int) -> None:
    if isinstance(value, str):
        # value is str
        def inner() -> None:
            # value is still str in nested function
            print(value.upper())
        inner()
```

### 3. Narrowing with Multiple Variables

```python
def process(a: str | None, b: str | None) -> None:
    if a is not None and b is not None:
        # Both a and b are narrowed to str
        print(a + b)
    elif a is not None:
        # Only a is narrowed, b is still str | None
        print(a)
```

### 4. Narrowing with walrus operator

```python
def process(value: str | None) -> None:
    if (trimmed := value.strip()) if value else None:
        # trimmed is str (not None)
        reveal_type(trimmed)  # str
        print(trimmed)
```

## FAQ

### Q: Why doesn't narrowing work with `type()`?

**A**: Use `isinstance()` instead. `type()` checks are not reliable for type narrowing because they don't work with subclasses.

```python
# ❌ Doesn't narrow properly
if type(value) is str:
    ...

# ✅ Use isinstance instead
if isinstance(value, str):
    ...
```

### Q: Can I narrow with `hasattr()`?

**A**: `hasattr()` can narrow types in some cases, but it's limited:

```python
class A:
    x: int

class B:
    y: str

def process(obj: A | B) -> None:
    if hasattr(obj, 'x'):
        # obj is narrowed to A
        reveal_type(obj)  # A
    elif hasattr(obj, 'y'):
        # obj is narrowed to B
        reveal_type(obj)  # B
```

### Q: How do I narrow with enums?

**A**: Enum values can be narrowed with equality checks:

```python
from enum import Enum

class Status(Enum):
    OPEN = "open"
    CLOSED = "closed"

def process(status: Status) -> None:
    if status == Status.OPEN:
        # status is Status.OPEN
        reveal_type(status)  # Literal[Status.OPEN]
    else:
        # status is Status.CLOSED
        reveal_type(status)  # Literal[Status.CLOSED]
```

### Q: Does narrowing work with `assert`?

**A**: Yes, `assert` can narrow types:

```python
def process(value: str | None) -> None:
    assert value is not None
    # value is narrowed to str
    reveal_type(value)  # str
```

### Q: Can I narrow with `match` statements?

**A**: Yes, Python 3.10+ `match` statements support type narrowing:

```python
def process(value: str | int | list[str]) -> None:
    match value:
        case str():
            # value is str
            reveal_type(value)  # str
        case int():
            # value is int
            reveal_type(value)  # int
        case list():
            # value is list[str]
            reveal_type(value)  # list[str]
```

## Related Diagnostics

Type narrowing helps resolve these diagnostics:

- [`reportOptionalMemberAccess`](../diagnostics/reportOptionalMemberAccess.md) - Accessing members on possibly None values
- [`reportOptionalSubscript`](../diagnostics/reportOptionalSubscript.md) - Subscripting possibly None values
- [`reportOptionalCall`](../diagnostics/reportOptionalCall.md) - Calling possibly None values
- [`reportArgumentType`](../diagnostics/reportArgumentType.md) - Argument type mismatches
- [`reportGeneralTypeIssues`](../diagnostics/reportGeneralTypeIssues.md) - General type errors

## See Also

- [Type Narrowing in Pyright Documentation](https://microsoft.github.io/pyright/#/type-narrowing)
- [Python Type Spec - Type Guards](https://typing.python.org/)
- [Settings Troubleshooting](settings-troubleshooting.md)