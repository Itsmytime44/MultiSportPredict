# python.analysis.includeExtraPathSymbolsInSymbolSearch

Controls whether symbols from extra paths (configured via `python.analysis.extraPaths`) are included in workspace symbol search results.

## Description

When enabled, this setting includes symbols from directories specified in `extraPaths` when performing workspace-wide symbol searches (Ctrl+T in VS Code). This is useful when you have code in non-standard locations that you want to be searchable.

## Default Value

- **Pylance**: `true`
- **Pyright**: `true`

## Supported Values

- `true` - Include extra path symbols in workspace symbol search
- `false` - Exclude extra path symbols from workspace symbol search

## How It Works

### With extraPaths Configuration

When you configure extra paths:

```json
{
  "python.analysis.extraPaths": [
    "./shared-lib",
    "./common-utils"
  ],
  "python.analysis.includeExtraPathSymbolsInSymbolSearch": true
}
```

Symbols from `shared-lib/` and `common-utils/` will appear in workspace symbol search results.

### Example Project Structure

```
my-project/
├── src/
│   └── main_app/
│       └── app.py
├── shared-lib/
│   └── utils/
│       └── helpers.py    # Contains: def helper_function(): ...
└── common-utils/
    └── tools.py          # Contains: class Tool: ...
```

With `includeExtraPathSymbolsInSymbolSearch` enabled:
- Pressing Ctrl+T and searching for "helper_function" will find it in `shared-lib/utils/helpers.py`
- Searching for "Tool" will find it in `common-utils/tools.py`

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.extraPaths": ["./shared-lib", "./common-utils"],
  "python.analysis.includeExtraPathSymbolsInSymbolSearch": true
}
```

### pyrightconfig.json

```json
{
  "extraPaths": ["./shared-lib", "./common-utils"],
  "includeExtraPathSymbolsInSymbolSearch": true
}
```

### pyproject.toml

```toml
[tool.pyright]
extraPaths = ["./shared-lib", "./common-utils"]
includeExtraPathSymbolsInSymbolSearch = true
```

## When to Disable

You might want to disable this setting in these scenarios:

1. **Large extra paths**: Extra paths contain many symbols that slow down search
2. **Irrelevant symbols**: Extra paths contain third-party code you don't want in search
3. **Performance**: Improve symbol search performance by limiting scope
4. **Noise reduction**: Reduce clutter in search results

## Performance Considerations

Including extra paths in symbol search can impact performance:

| Factor | Impact |
|--------|--------|
| Number of extra paths | More paths = slower search |
| Size of extra path content | Larger codebases = slower indexing |
| Frequency of changes | Frequently changing code = more re-indexing |

### Optimization Tips

1. **Limit extra paths**: Only include necessary directories
2. **Disable if not needed**: Set to `false` if you don't use workspace symbol search
3. **Use specific paths**: Point to specific packages rather than large directories

## Related Settings

- [`python.analysis.extraPaths`](python_analysis_extraPaths.md) - Configure additional search paths
- [`python.analysis.includeVenvInWorkspaceSymbols`](python_analysis_includeVenvInWorkspaceSymbols.md) - Include venv symbols in search
- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing

## Troubleshooting

### Symbols Not Appearing in Search

If symbols from extra paths don't appear:

1. **Check extraPaths**: Verify paths are correctly configured
2. **Check setting**: Ensure `includeExtraPathSymbolsInSymbolSearch` is `true`
3. **Verify path exists**: Extra paths must exist and contain Python files
4. **Rebuild index**: Run "Python: Restart Language Server" in VS Code

### Slow Symbol Search

If symbol search becomes slow:

1. **Disable the setting**: Set `includeExtraPathSymbolsInSymbolSearch` to `false`
2. **Reduce extra paths**: Remove unnecessary paths from `extraPaths`
3. **Check indexing**: See [Performance Tuning](../howto/settings-troubleshooting.md#performance)

## See Also

- [Settings Troubleshooting](../howto/settings-troubleshooting.md)
- [Fix Unresolved Imports](../howto/fix-unresolved-imports.md)