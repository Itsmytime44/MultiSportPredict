# reportUndefinedVariable

Reports when a variable is used but has not been defined in any accessible scope.

## Description

This diagnostic is raised when Pylance/Pyright encounters a variable name that cannot be resolved to any definition. This is one of the most common Python errors and indicates a genuine runtime error that would occur if the code were executed.

## Default Severity

- **Error**

## Examples

### Example 1: Variable Never Defined

```python
def calculate():
    result = total + 10  # Error: "total" is undefined
    return result
```

**Fix**: Define `total` before using it:

```python
def calculate():
    total = 100
    result = total + 10
    return result
```

### Example 2: Typo in Variable Name

```python
def process():
    count = 5
    print(coutn)  # Error: "coutn" is undefined (typo of "count")
```

**Fix**: Correct the typo:

```python
def process():
    count = 5
    print(count)
```

### Example 3: Variable Defined in Different Scope

```python
def outer():
    if condition:
        inner_var = 42
    print(inner_var)  # Error: "inner_var" may be undefined if condition is False
```

**Fix**: Ensure variable is defined before use:

```python
def outer():
    inner_var = None
    if condition:
        inner_var = 42
    print(inner_var)
```

### Example 4: Missing Import

```python
def fetch():
    response = requests.get(url)  # Error: "requests" is undefined
```

**Fix**: Import the module:

```python
import requests

def fetch():
    response = requests.get(url)
```

### Example 5: Using Variable Before Assignment in Conditional

```python
def process(flag: bool):
    if flag:
        value = "yes"
    print(value)  # Error: "value" may be undefined if flag is False
```

**Fix**: Initialize the variable:

```python
def process(flag: bool):
    value = "no"
    if flag:
        value = "yes"
    print(value)
```

### Example 6: Scope Issues with Functions

```python
def outer():
    def inner():
        return x  # Error: "x" is undefined
    x = 10
    return inner()
```

**Fix**: Define variable before inner function is called:

```python
def outer():
    x = 10
    def inner():
        return x  # Now x is defined in enclosing scope
    return inner()
```

## Common Causes

| Cause | Description | Solution |
|-------|-------------|----------|
| Typo | Misspelled variable name | Check spelling |
| Missing import | Module not imported | Add import statement |
| Wrong scope | Variable defined in different scope | Move definition or use proper scoping |
| Conditional definition | Variable only defined in some branches | Initialize before conditional |
| Deleted variable | Variable was deleted with `del` | Don't use after deletion |

## Suppressing the Diagnostic

If you need to suppress this diagnostic (not recommended for genuine undefined variables):

```python
# Using type: ignore comment
print(undefined_var)  # type: ignore

# Or using configuration
# In pyrightconfig.json:
{
  "reportUndefinedVariable": "none"
}
```

> **Warning**: Suppressing this diagnostic is dangerous as it indicates a genuine runtime error.

## Related Diagnostics

- [`reportUnboundVariable`](reportUnboundVariable.md) - Variable is bound but may not have been assigned
- [`reportMaybeUndefined`](reportMaybeUndefined.md) - Variable may be undefined in some code paths

## See Also

- [Python Name Binding](https://docs.python.org/3/reference/executionmodel.html#execution-model)
- [Python Scoping Rules](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)