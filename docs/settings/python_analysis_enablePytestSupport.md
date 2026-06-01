# python.analysis.enablePytestSupport

Enables enhanced support for pytest fixtures, markers, and other pytest-specific features in Pylance.

## Description

When enabled, this setting provides improved type checking and autocomplete support for pytest-specific features including:

- **Fixtures**: Proper type inference for fixture parameters
- **Markers**: Recognition of pytest markers like `@pytest.mark.skip`
- **Parametrize**: Type checking for `@pytest.mark.parametrize`
- **conftest.py**: Proper fixture discovery and resolution

## Default Value

- **Pylance**: `true`
- **Pyright**: `false`

> **Note**: This setting is enabled by default in Pylance but disabled in Pyright CLI.

## Supported Values

- `true` - Enable enhanced pytest support
- `false` - Disable enhanced pytest support

## Features

### Fixture Type Inference

With pytest support enabled, Pylance correctly infers types from fixtures:

```python
import pytest

@pytest.fixture
def sample_data() -> dict:
    return {"key": "value"}

def test_with_fixture(sample_data: dict):
    # Pylance knows sample_data is a dict
    reveal_type(sample_data)  # dict
    assert sample_data["key"] == "value"
```

### Parametrize Support

Proper type checking for parametrized tests:

```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_doubled(input_value: int, expected: int):
    # Types are properly inferred from parametrize
    assert input_value * 2 == expected
```

### Marker Recognition

Pytest markers are recognized and validated:

```python
import pytest

@pytest.mark.slow
@pytest.mark.integration
def test_slow_operation():
    pass

# Custom markers are recognized
@pytest.mark.custom_marker("reason")
def test_with_custom_marker():
    pass
```

### conftest.py Fixtures

Fixtures defined in `conftest.py` are properly discovered:

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def db_connection():
    """Session-scoped database fixture."""
    conn = setup_database()
    yield conn
    conn.close()

# test_module.py
def test_database(db_connection):
    # Fixture from conftest.py is recognized
    assert db_connection.is_connected()
```

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.enablePytestSupport": true
}
```

### pyrightconfig.json

```json
{
  "enablePytestSupport": true
}
```

### pyproject.toml

```toml
[tool.pyright]
enablePytestSupport = true
```

## When to Disable

You might want to disable `enablePytestSupport` in these scenarios:

1. **Not using pytest**: Your project uses unittest or another test framework
2. **False positives**: pytest-specific behavior causes unwanted diagnostics
3. **Performance**: Minimal performance improvement by disabling unused features

## Common Issues

### Fixtures Not Recognized

If fixtures are not being recognized:

1. **Check setting is enabled**: Verify `enablePytestSupport` is `true`
2. **conftest.py location**: Ensure `conftest.py` is in the correct directory
3. **Fixture scope**: Check fixture scope matches test usage
4. **Reload window**: Run "Developer: Reload Window" in VS Code

### Parametrize Type Errors

If you see type errors with `@pytest.mark.parametrize`:

```python
# This may cause type errors if types don't match
@pytest.mark.parametrize("value", [1, "string", 3.14])
def test_mixed_types(value):  # What type is value?
    pass
```

**Solution**: Use consistent types or explicit type annotations:

```python
@pytest.mark.parametrize("value", [1, 2, 3])
def test_integers(value: int):
    pass
```

### Custom Markers Warnings

Pytest allows custom markers, but you may see warnings. To suppress:

1. Register markers in `pytest.ini` or `pyproject.toml`
2. Use `# type: ignore` comments if needed

## Related Settings

- [`python.analysis.typeCheckingMode`](python_analysis_typeCheckingMode.md) - Control type checking strictness
- [`python.analysis.ignore`](python_analysis_ignore.md) - Suppress diagnostics for specific files

## Performance Considerations

Enabling pytest support has minimal performance impact. The setting only affects test files and their analysis.

## See Also

- [Settings Troubleshooting](../howto/settings-troubleshooting.md)
- [Pytest Documentation](https://docs.pytest.org/)