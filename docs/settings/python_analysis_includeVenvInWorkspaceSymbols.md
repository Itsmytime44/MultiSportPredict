# python.analysis.includeVenvInWorkspaceSymbols

Controls whether symbols from the active virtual environment's site-packages are included in workspace symbol search results.

## Description

When enabled, this setting includes symbols from your virtual environment's `site-packages` directory when performing workspace-wide symbol searches (Ctrl+T in VS Code). This allows you to search for symbols in installed packages alongside your own code.

## Default Value

- **Pylance**: `false`
- **Pyright**: `false`

## Supported Values

- `true` - Include venv site-packages symbols in workspace symbol search
- `false` - Exclude venv site-packages symbols from workspace symbol search

## How It Works

### With venv Enabled

When you enable this setting:

```json
{
  "python.analysis.includeVenvInWorkspaceSymbols": true
}
```

Pylance will index symbols from your active virtual environment's site-packages:

```
my-project/
├── .venv/
│   └── lib/
│       └── python3.11/
│           └── site-packages/
│               ├── requests/
│               │   └── api.py    # Contains: def get(): ...
│               └── numpy/
│                   └── core/
│                       └── array.py  # Contains: class ndarray: ...
└── src/
    └── main.py
```

With `includeVenvInWorkspaceSymbols` enabled:
- Pressing Ctrl+T and searching for "get" will find `requests.api.get`
- Searching for "ndarray" will find `numpy.core.array.ndarray`

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.includeVenvInWorkspaceSymbols": true
}
```

### pyrightconfig.json

```json
{
  "includeVenvInWorkspaceSymbols": true
}
```

### pyproject.toml

```toml
[tool.pyright]
includeVenvInWorkspaceSymbols = true
```

## When to Enable

You might want to enable this setting in these scenarios:

1. **Exploring libraries**: You frequently need to navigate to library source code
2. **Debugging dependencies**: You need to understand how dependencies work
3. **Learning**: You want to study library implementations
4. **Type stubs unavailable**: Library lacks type stubs and you need to inspect source

## When to Keep Disabled

Keep this setting disabled (default) in these scenarios:

1. **Performance**: Large site-packages with many packages slow down indexing
2. **Large environments**: Virtual environments with hundreds of packages
3. **Noise**: You don't want third-party symbols cluttering search results
4. **Memory**: Limited system memory for indexing

## Performance Considerations

Including venv symbols can significantly impact performance:

| Factor | Impact |
|--------|--------|
| Number of installed packages | More packages = slower indexing |
| Package size | Large packages (numpy, pandas) = much slower |
| Available memory | Indexing many packages requires more RAM |
| Search speed | Larger index = slower symbol search |

### Optimization Tips

1. **Keep disabled by default**: Only enable when needed
2. **Use Go to Definition**: Use F12 instead of search for library navigation
3. **Type stubs**: Install type stub packages (`types-requests`) instead
4. **Selective indexing**: Use `packageIndexDepths` to limit indexing depth

## Related Settings

- [`python.analysis.includeExtraPathSymbolsInSymbolSearch`](python_analysis_includeExtraPathSymbolsInSymbolSearch.md) - Include extra path symbols in search
- [`python.analysis.packageIndexDepths`](python_analysis_packageIndexDepths.md) - Control indexing depth per package
- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing

## Troubleshooting

### Slow Performance After Enabling

If VS Code becomes slow after enabling:

1. **Disable the setting**: Set `includeVenvInWorkspaceSymbols` to `false`
2. **Clear cache**: Delete the Pylance cache directory
3. **Limit packages**: Use `packageIndexDepths` to exclude large packages
4. **Check memory**: Monitor system memory usage

### Symbols Still Not Found

If library symbols don't appear even when enabled:

1. **Check virtual environment**: Ensure correct venv is activated
2. **Restart language server**: Run "Python: Restart Language Server"
3. **Verify package installation**: Ensure packages are installed in the venv
4. **Check indexing**: Verify indexing is enabled (`python.analysis.indexing`)

## Memory Considerations

> **Warning**: Enabling this setting can significantly increase memory usage, especially with large packages like numpy, pandas, or tensorflow.

If you experience memory issues:

1. **Disable the setting**
2. **Increase Node.js heap limit** (see [nodeArguments](python_analysis_nodeArguments.md))
3. **Use type stubs** instead of indexing full packages

## See Also

- [Performance Tuning](../howto/settings-troubleshooting.md#performance)
- [nodeArguments for Heap Limits](python_analysis_nodeArguments.md)
- [Fix Unresolved Imports](../howto/fix-unresolved-imports.md)