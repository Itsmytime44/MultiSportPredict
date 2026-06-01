# python.analysis.useLibraryCodeForTypes

Controls whether Pylance/Pyright uses library source code to determine types when type stubs are unavailable.

## Description

When a Python library doesn't have type stub files (`.pyi`), Pylance/Pyright can analyze the library's source code to extract type information. This setting controls whether this behavior is enabled.

## Default Value

- **Pylance**: `true`
- **Pyright**: `true`

## Supported Values

- `true` - Use library source code to determine types when stubs are unavailable
- `false` - Do not use library source code; treat untyped libraries as `Unknown`

## How It Works

### With useLibraryCodeForTypes Enabled

```python
# Using a library without type stubs
import untyped_library

# Pylance analyzes the source code to infer types
obj = untyped_library.create_object()  # Type inferred from source
result = obj.process()  # Return type inferred from source
```

### With useLibraryCodeForTypes Disabled

```python
import untyped_library

# Types are Unknown
obj = untyped_library.create_object()  # Type is Unknown
result = obj.process()  # Type is Unknown
```

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.useLibraryCodeForTypes": true
}
```

### pyrightconfig.json

```json
{
  "useLibraryCodeForTypes": true
}
```

### pyproject.toml

```toml
[tool.pyright]
useLibraryCodeForTypes = true
```

## When to Disable

You might want to disable this setting in these scenarios:

1. **Performance**: Analyzing library source code can be slow for large libraries
2. **Memory**: Reduces memory usage by not analyzing library source
3. **Accuracy**: Library source may have complex patterns that lead to incorrect type inference
4. **Preference**: You prefer to use explicit type stubs instead

## Performance Impact

| Setting | Performance Impact |
|---------|-------------------|
| `true` | Slower analysis of untyped libraries, better type information |
| `false` | Faster analysis, but less type information for untyped libraries |

## Related Settings

- [`python.analysis.stubPath`](python_analysis_stubPath.md) - Custom path for type stub files
- [`python.analysis.typeshedPaths`](python_analysis_typeshedPaths.md) - Additional typeshed paths
- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing

## Troubleshooting

### Slow Analysis of Libraries

If analysis is slow when working with untyped libraries:

1. **Disable useLibraryCodeForTypes**: Set to `false`
2. **Install type stubs**: Use `types-*` packages if available
3. **Create custom stubs**: Add stub files for frequently used libraries

### Inaccurate Type Information

If type information from library source is incorrect:

1. **Install type stubs**: Prefer official or community stubs
2. **Create custom stubs**: Override with your own type definitions
3. **Disable and use Any**: Set `useLibraryCodeForTypes` to `false`

### Missing Type Information

If you're not getting type information for libraries:

1. **Enable useLibraryCodeForTypes**: Set to `true`
2. **Check library installation**: Ensure library is properly installed
3. **Restart language server**: Run "Python: Restart Language Server"

## Best Practices

1. **Prefer type stubs**: Install `types-*` packages when available
2. **Keep enabled for development**: Provides better autocomplete and type checking
3. **Disable for CI**: Can speed up type checking in CI environments
4. **Use with indexing**: Works well with `indexing: "on"`

## See Also

- [Stub Path Configuration](python_analysis_stubPath.md)
- [Typeshed Paths](python_analysis_typeshedPaths.md)
- [Performance Tuning](../howto/settings-troubleshooting.md#performance-troubleshooting)