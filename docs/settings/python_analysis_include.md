# python.analysis.include

Specifies which files or directories to include for analysis. Files not matched by include patterns are not analyzed.

## Description

The `include` setting defines the scope of files that Pylance will analyze. Only files matching the include patterns will have diagnostics reported. This is useful for focusing analysis on specific parts of a large codebase.

## Default Value

- **Pylance**: `["**"]` (all files in workspace)
- **Pyright**: `["**"]` (all files in workspace)

## Supported Values

Array of file or directory glob patterns to include for analysis.

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.include": [
    "src/**/*.py",
    "lib/**/*.py"
  ]
}
```

### pyrightconfig.json

```json
{
  "include": [
    "src/**/*.py",
    "lib/**/*.py"
  ]
}
```

### pyproject.toml

```toml
[tool.pyright]
include = [
    "src/**/*.py",
    "lib/**/*.py"
]
```

## Examples

### Include Only Source Directory

```json
{
  "python.analysis.include": ["src/**/*.py"]
}
```

Only files in `src/` will be analyzed.

### Include Multiple Directories

```json
{
  "python.analysis.include": [
    "src/**/*.py",
    "tests/**/*.py",
    "scripts/**/*.py"
  ]
}
```

### Exclude Tests from Analysis

```json
{
  "python.analysis.include": ["src/**/*.py"],
  "python.analysis.exclude": ["src/**/test*.py"]
}
```

## Wildcard Support

The `include` setting supports glob patterns:

| Pattern | Description | Example Match |
|---------|-------------|---------------|
| `*.py` | Files in current directory | `test.py` |
| `**/*.py` | Files in all subdirectories | `src/module/test.py` |
| `dir/` | All files in directory | `dir/file.py`, `dir/sub/file.py` |
| `src/**/*.py` | Python files under src/ | `src/module/file.py` |

## Interaction with `exclude` and `ignore`

The settings work together in this order:

1. **Include**: Files matching include patterns are candidates for analysis
2. **Exclude**: Files matching exclude patterns are removed from analysis
3. **Ignore**: Files matching ignore patterns have diagnostics suppressed but are still analyzed

### Example

```json
{
  "python.analysis.include": ["**/*.py"],
  "python.analysis.exclude": ["dist/**/*.py", "build/**/*.py"],
  "python.analysis.ignore": ["legacy/**/*.py"]
}
```

- All `.py` files are candidates
- Files in `dist/` and `build/` are excluded (not analyzed)
- Files in `legacy/` are analyzed but no diagnostics shown

## Important Notes on Import Resolution

> **Important**: Import resolution works independently of `include`/`exclude` settings. Even if a file is not included in analysis, imports from that file can still be resolved if the file exists and is valid Python.

This means:
- A file not in `include` won't have diagnostics reported
- But other files can still import from it
- The imported symbols will be available for type checking

## Related Settings

- [`python.analysis.exclude`](python_analysis_ignore.md) - Exclude files from analysis
- [`python.analysis.ignore`](python_analysis_ignore.md) - Suppress diagnostics for files
- [`python.analysis.diagnosticMode`](python_analysis_languageServerMode.md) - Control diagnostic scope

## Troubleshooting

### Files Not Being Analyzed

If files aren't being analyzed:

1. **Check include pattern**: Ensure pattern matches the file path
2. **Check exclude pattern**: Ensure file isn't excluded
3. **Check workspace root**: Patterns are relative to workspace root
4. **Restart language server**: Run "Python: Restart Language Server"

### Diagnostics Not Appearing

If you expect diagnostics but don't see them:

1. **Check include**: File must be included
2. **Check ignore**: File might be in ignore list
3. **Check typeCheckingMode**: May be set to "off"
4. **Check file is saved**: Unsaved files may not be analyzed

### Performance Issues

If analysis is slow:

1. **Narrow include**: Be more specific with include patterns
2. **Exclude more**: Exclude unnecessary directories
3. **Check indexing**: See [Performance Tuning](../howto/settings-troubleshooting.md#performance)

## Best Practices

1. **Be specific**: Include only directories that need analysis
2. **Exclude build artifacts**: Always exclude `dist/`, `build/`, `__pycache__/`
3. **Consider performance**: Smaller include scope = faster analysis
4. **Document patterns**: Explain why certain patterns are used

## See Also

- [Settings Troubleshooting](../howto/settings-troubleshooting.md)
- [Fix Unresolved Imports](../howto/fix-unresolved-imports.md)