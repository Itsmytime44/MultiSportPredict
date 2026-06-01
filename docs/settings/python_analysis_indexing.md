# python.analysis.indexing

Controls whether Pylance/Pyright indexes library code for faster autocomplete and type information.

## Description

Indexing allows Pylance/Pyright to pre-analyze library code and cache the results, providing faster autocomplete suggestions and type information without re-analyzing libraries on every edit.

## Default Value

- **Pylance**: `"on"`
- **Pyright**: `"on"`

## Supported Values

| Value | Description |
|-------|-------------|
| `"on"` | Index library code for faster completions |
| `"off"` | Do not index library code |

## How Indexing Works

### Indexing Process

1. **Discovery**: Pylance discovers installed packages in your virtual environment
2. **Analysis**: Each package is analyzed to extract type information
3. **Caching**: Results are cached for fast access
4. **Usage**: Cached information is used for autocomplete and type checking

### What Gets Indexed

- **Standard library**: Python built-in modules
- **Installed packages**: Packages in your virtual environment's site-packages
- **Workspace code**: Your project's Python files (if enabled)

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.indexing": "on"
}
```

### pyrightconfig.json

```json
{
  "indexing": "on"
}
```

### pyproject.toml

```toml
[tool.pyright]
indexing = "on"
```

## When to Disable

You might want to disable indexing in these scenarios:

1. **Memory constraints**: Indexing uses additional memory
2. **Very large environments**: Environments with hundreds of packages
3. **Debugging**: To isolate issues with type information
4. **Performance**: If indexing causes slowdowns during startup

## Performance Considerations

### Memory Usage

| Setting | Memory Impact |
|---------|---------------|
| `indexing: "on"` | Higher - caches library types |
| `indexing: "off"` | Lower - analyzes on demand |

### Startup Time

| Setting | Startup Impact |
|---------|----------------|
| `indexing: "on"` | Slower initial startup (indexing), faster subsequent |
| `indexing: "off"` | Faster initial startup, slower autocomplete |

### Autocomplete Speed

| Setting | Autocomplete Impact |
|---------|---------------------|
| `indexing: "on"` | Faster suggestions |
| `indexing: "off"` | Slower suggestions (on-demand analysis) |

## Related Settings

- [`python.analysis.packageIndexDepths`](python_analysis_packageIndexDepths.md) - Control indexing depth per package
- [`python.analysis.persistAllIndices`](python_analysis_persistAllIndices.md) - Persist indices to disk
- [`python.analysis.userFileIndexingLimit`](python_analysis_userFileIndexingLimit.md) - Limit files to index in user code
- [`python.analysis.includeVenvInWorkspaceSymbols`](python_analysis_includeVenvInWorkspaceSymbols.md) - Include venv symbols in search

## Troubleshooting

### High Memory Usage

If Pylance uses too much memory:

1. **Disable indexing**: Set `indexing` to `"off"`
2. **Limit package depths**: Use `packageIndexDepths` to reduce indexing
3. **Clear cache**: Delete the Pylance cache directory

### Slow Startup

If VS Code startup is slow:

1. **Disable persistAllIndices**: Set to `false`
2. **Reduce indexed packages**: Use `packageIndexDepths`
3. **Consider disabling indexing**: Set to `"off"` temporarily

### Incomplete Autocomplete

If autocomplete suggestions are missing:

1. **Enable indexing**: Ensure `indexing` is `"on"`
2. **Restart language server**: Run "Python: Restart Language Server"
3. **Check package installation**: Ensure packages are installed correctly

## Best Practices

1. **Keep indexing enabled**: It provides the best experience for most users
2. **Use virtual environments**: Keeps package indexing manageable
3. **Clear cache periodically**: Remove stale cached data
4. **Monitor memory**: If memory is tight, consider disabling

## See Also

- [Performance Tuning](../howto/settings-troubleshooting.md#performance-troubleshooting)
- [packageIndexDepths](python_analysis_packageIndexDepths.md)
- [persistAllIndices](python_analysis_persistAllIndices.md)