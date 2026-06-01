# reportUnusedVariable

Reports when a variable is assigned but never used within its scope.

## Description

This diagnostic is raised when a variable is assigned a value but that value is never read or used. This helps identify dead code and potential bugs where variables are assigned but forgotten.

## Default Severity

- **Warning** (in basic/strict mode)
- **Information** (in standard mode)

## Examples

### Example 1: Variable Assigned but Never Used

```python
def process():
    x = 42  # Warning: "x" is assigned but never used
    y = 10
    return y * 2
```

**Fix**: Remove the unused variable or use it:

```python
def process():
    y = 10
    return y * 2
```

Or:

```python
def process():
    x = 42
    y = 10
    return x + y * 2
```

### Example 2: Unused Loop Variable

```python
def sum_numbers(numbers: list[int]) -> int:
    total = 0
    for num in numbers:
        total += num
    return total

def print_numbers(numbers: list[int]) -> None:
    for num in numbers:  # Warning: "num" is assigned but never used
        print("Processing...")
```

**Fix**: Use underscore `_` for intentionally unused variables:

```python
def print_numbers(numbers: list[int]) -> None:
    for _ in numbers:
        print("Processing...")
```

### Example 3: Unused Function Parameter

```python
def greet(name: str, greeting: str) -> str:
    return "Hello!"  # Warning: "name" and "greeting" are assigned but never used
```

**Fix**: Use the parameters or prefix with underscore:

```python
def greet(_name: str, _greeting: str) -> str:
    return "Hello!"
```

Or:

```python
def greet(name: str, greeting: str) -> str:
    return f"{greeting}, {name}!"
```

### Example 4: Unused Unpacking

```python
def get_user_data() -> tuple[str, int, str]:
    return ("Alice", 30, "Engineer")

def process_user():
    name, age, job = get_user_data()
    print(name)  # Warning: "age" and "job" are assigned but never used
```

**Fix**: Use underscore for unused unpacked values:

```python
def process_user():
    name, _, _ = get_user_data()
    print(name)
```

### Example 5: Variable Overwritten Before Use

```python
def calculate():
    result = 10  # Warning: "result" is assigned but never used
    result = 20
    return result
```

**Fix**: Remove the first assignment:

```python
def calculate():
    result = 20
    return result
```

### Example 6: Unused Variable in Exception Handling

```python
def divide(a: int, b: int) -> float:
    try:
        return a / b
    except ZeroDivisionError as e:  # Warning: "e" is assigned but never used
        return 0
```

**Fix**: Use underscore for unused exception variable:

```python
def divide(a: int, b: int) -> float:
    try:
        return a / b
    except ZeroDivisionError:
        return 0
```

Or log the exception:

```python
def divide(a: int, b: int) -> float:
    try:
        return a / b
    except ZeroDivisionError as e:
        print(f"Division error: {e}")
        return 0
```

## Common Patterns

### Intentionally Unused Variables

Use underscore `_` or prefix with underscore for intentionally unused variables:

```python
# Unused loop variable
for _ in range(10):
    do_something()

# Unused parameter
def callback(_event):
    pass

# Unused unpacked value
first, *_ = [1, 2, 3, 4, 5]

# Unused exception
try:
    risky_operation()
except SomeError as _e:
    pass
```

### Walrus Operator

Sometimes the walrus operator can help avoid unused variables:

```python
# Before: unused variable
result = expensive_computation()
if result:
    process(result)

# After: no unused variable
if (result := expensive_computation()):
    process(result)
```

## Suppressing the Diagnostic

### For Specific Variables

Use underscore naming convention:

```python
# Instead of:
unused = get_value()

# Use:
_unused = get_value()  # No warning
# Or:
_ = get_value()  # No warning
```

### For Specific Lines

```python
def process():
    x = 42  # noqa: F841
    return 10
```

### Configuration

In `pyrightconfig.json`:

```json
{
  "reportUnusedVariable": "none"
}
```

> **Note**: Disabling this diagnostic globally is not recommended as it helps identify dead code.

## Related Diagnostics

- [`reportUnusedFunction`](reportUnusedFunction.md) - Function is defined but never used
- [`reportUnusedClass`](reportUnusedClass.md) - Class is defined but never used
- [`reportUnusedImport`](reportUnusedImport.md) - Import is never used
- [`reportUnusedExpression`](reportUnusedExpression.md) - Expression value is never used

## See Also

- [PEP 8 - Programming Recommendations](https://pep8.org/#programming-recommendations)
- [Pyright Type Ignored Variables](https://microsoft.github.io/pyright/#/type-concepts-advanced?id=ignored-variables)