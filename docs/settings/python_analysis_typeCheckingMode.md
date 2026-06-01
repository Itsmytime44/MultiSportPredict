# python.analysis.typeCheckingMode

Controls the strictness of type checking performed by Pylance/Pyright.

## Description

This setting determines how aggressively Pylance/Pyright checks types in your code. Different modes provide different levels of type safety and diagnostic reporting.

## Default Value

- **Pylance**: `"basic"`
- **Pyright**: `"off"`

## Supported Values

| Value | Description |
|-------|-------------|
| `"off"` | No type checking diagnostics |
| `"basic"` | Basic type checking (recommended for most projects) |
| `"strict"` | Strict type checking with additional diagnostics |
| `"standard"` | Between basic and strict (deprecated, use basic) |

## Mode Details

### off

- No type checking diagnostics are reported
- Only syntax errors and import resolution issues are reported
- Useful for projects that don't use type hints

### basic

- Reports common type errors
- Checks function arguments and return types
- Validates variable assignments
- Reports missing type annotations in some cases
- **Recommended for most projects**

### strict

- All basic checks plus:
- Reports unknown types (`reportUnknownVariableType`, etc.)
- Reports implicitly implicit `Any` types
- Stricter checking for `None` handling
- Reports unused expressions and values
- **Recommended for new projects or teams committed to typing**

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.typeCheckingMode": "basic"
}
```

### pyrightconfig.json

```json
{
  "typeCheckingMode": "basic"
}
```

### pyproject.toml

```toml
[tool.pyright]
typeCheckingMode = "basic"
```

## Gradual Adoption

### Starting with Basic

```json
{
  "python.analysis.typeCheckingMode": "basic"
}
```

### Moving to Strict

1. Start with `basic` mode
2. Fix all reported issues
3. Switch to `strict` mode
4. Address new diagnostics incrementally

### Per-File Configuration

Use `# pyright: reportUnknownVariableType=none` comments for specific files:

```python
# pyright: reportUnknownVariableType=none
def legacy_function():
    # This file won't report unknown variable types
    pass
```

## Related Settings

- [`python.analysis.ignore`](python_analysis_ignore.md) - Suppress diagnostics for specific files
- [`python.analysis.exclude`](python_analysis_ignore.md) - Exclude files from analysis
- [`python.analysis.useLibraryCodeForTypes`](python_analysis_useLibraryCodeForTypes.md) - Use library code for types

## Troubleshooting

### Too Many Diagnostics

If you're overwhelmed with diagnostics:

1. **Start with basic mode**: Use `basic` instead of `strict`
2. **Suppress specific diagnostics**: Use `# type: ignore` comments
3. **Configure diagnostic severity**: Set specific diagnostics to `warning` or `none`

### Not Enough Diagnostics

If you want more thorough checking:

1. **Use strict mode**: Set `typeCheckingMode` to `strict`
2. **Enable specific diagnostics**: Configure individual diagnostic settings
3. **Use type annotations**: Add more type hints to your code

## See Also

- [Type Narrowing Guide](../howto/type-narrowing.md)
- [Settings Troubleshooting](../howto/settings-troubleshooting.md)
- [Pyright Type Checking Modes](https://microsoft.github.io/pyright/#/type-concepts-advanced?id=type-checking-modes)