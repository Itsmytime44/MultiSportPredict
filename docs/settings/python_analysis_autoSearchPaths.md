# python.analysis.autoSearchPaths

Controls whether Pylance automatically adds common search paths to the Python import resolution paths.

## Description

When enabled, this setting automatically discovers and adds common directory patterns to the import search paths. This helps Pylance resolve imports from project-specific directories without manual configuration.

## Default Value

- **Pylance**: `true`
- **Pyright**: `true`

## Supported Values

- `true` - Automatically add common search paths
- `false` - Do not add any automatic search paths

## How It Works

When `autoSearchPaths` is enabled, Pylance looks for common directory patterns in your project:

| Pattern | Description |
|---------|-------------|
| `src/` | Common source directory pattern |
| `lib/` | Library directory pattern |
| `app/` | Application directory pattern |
| Directories with `__init__.py` | Package directories |

### Example Project Structure

```
my-project/
├── src/
│   ├── mypackage/
│   │   ├── __init__.py
│   │   └── module.py
│   └── utils/
│       └── helpers.py
├── tests/
│   └── test_module.py
└── pyproject.toml
```

With `autoSearchPaths` enabled, Pylance automatically adds `src/` to the search paths, allowing imports like:

```python
from mypackage import module
from utils import helpers
```

Without this setting, you would need to manually configure:

```json
{
  "python.analysis.extraPaths": ["src"]
}
```

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.autoSearchPaths": true
}
```

### pyrightconfig.json

```json
{
  "autoSearchPaths": true
}
```

### pyproject.toml

```toml
[tool.pyright]
autoSearchPaths = true
```

## When to Disable

You might want to disable `autoSearchPaths` in these scenarios:

1. **Custom project structure**: Your project uses non-standard directory names
2. **Performance**: Large projects where automatic discovery adds overhead
3. **Conflicts**: Auto-discovered paths conflict with manual `extraPaths` configuration
4. **Monorepo**: Multiple packages where automatic discovery causes ambiguity

## Related Settings

- [`python.analysis.extraPaths`](python_analysis_extraPaths.md) - Manually specify additional search paths
- [`python.analysis.include`](python_analysis_include.md) - Include specific files for analysis
- [`python.analysis.exclude`](python_analysis_ignore.md) - Exclude files from analysis

## Troubleshooting

### Imports Not Resolved Despite autoSearchPaths

If imports are still not resolved:

1. **Check project structure**: Ensure your source files follow common patterns
2. **Verify setting is enabled**: Check your effective configuration
3. **Try extraPaths**: Manually add paths if auto-detection fails
4. **Reload window**: Run "Developer: Reload Window" in VS Code

### Conflicting with Manual Paths

If `autoSearchPaths` conflicts with manually configured paths:

1. Disable `autoSearchPaths`
2. Use `extraPaths` for explicit control
3. Check [Settings Troubleshooting Guide](../howto/settings-troubleshooting.md)

## Performance Considerations

For very large projects, automatic path discovery may add a small startup delay. If you experience performance issues:

1. Disable `autoSearchPaths`
2. Manually configure only necessary paths
3. See [Performance Tuning](../howto/settings-troubleshooting.md#performance) for more tips

## See Also

- [Fix Unresolved Imports](../howto/fix-unresolved-imports.md)
- [Settings Troubleshooting](../howto/settings-troubleshooting.md)