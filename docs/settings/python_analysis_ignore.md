# python.analysis.ignore

Specifies files or directories to ignore for diagnostic purposes. Unlike `exclude`, ignored files still have their imports resolved and are included in analysis of other files.

## Description

The `ignore` setting suppresses diagnostics (warnings and errors) for specified files, but unlike `exclude`:

- **Imports from ignored files are still resolved** - Other files can import from ignored files
- **Ignored files are still indexed** - Symbols in ignored files are available for autocomplete
- **Only diagnostics are suppressed** - Type checking still happens, but issues aren't reported

## Default Value

- **Pylance**: `[]` (no files ignored)
- **Pyright**: `[]` (no files ignored)

## Supported Values

Array of file or directory glob patterns to ignore for diagnostics.

## Difference Between `exclude` and `ignore`

| Feature | `exclude` | `ignore` |
|---------|-----------|----------|
| Diagnostics suppressed | ✅ | ✅ |
| Imports resolved | ❌ (file treated as external) | ✅ |
| File indexed | ❌ | ✅ |
| Symbols available for autocomplete | ❌ | ✅ |
| Import resolution for other files | ❌ | ✅ |

### When to Use Each

**Use `exclude` when:**
- You want to completely exclude files from analysis
- Files are not part of your codebase (e.g., generated files, vendored libraries)
- You want to improve performance by reducing analyzed files

**Use `ignore` when:**
- You want to suppress diagnostics but keep import resolution
- Files are part of your codebase but have known issues
- You need symbols from these files for autocomplete in other files

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.ignore": [
    "legacy_code/**/*.py",
    "generated/*.py",
    "**/migrations/*.py"
  ]
}
```

### pyrightconfig.json

```json
{
  "ignore": [
    "legacy_code/**/*.py",
    "generated/*.py",
    "**/migrations/*.py"
  ]
}
```

### pyproject.toml

```toml
[tool.pyright]
ignore = [
    "legacy_code/**/*.py",
    "generated/*.py",
    "**/migrations/*.py"
]
```

## Examples

### Ignoring Legacy Code

```json
{
  "python.analysis.ignore": ["legacy/**/*.py"]
}
```

Files in `legacy/` will:
- Not show any diagnostics
- Still be importable from other files
- Have their symbols available for autocomplete

### Ignoring Database Migrations

```json
{
  "python.analysis.ignore": ["**/migrations/*.py"]
}
```

Django/SQLAlchemy migrations often have patterns that don't follow typical type checking rules.

### Ignoring Generated Files

```json
{
  "python.analysis.ignore": ["src/generated/*.py"]
}
```

## Wildcard Support

The `ignore` setting supports glob patterns:

| Pattern | Description | Example Match |
|---------|-------------|---------------|
| `*.py` | Files in current directory | `test.py` |
| `**/*.py` | Files in all subdirectories | `src/module/test.py` |
| `dir/` | All files in directory | `dir/file.py`, `dir/sub/file.py` |
| `**/vendor/**` | Files in any vendor directory | `lib/vendor/pkg/module.py` |

## Related Settings

- [`python.analysis.exclude`](python_analysis_ignore.md) - Exclude files completely from analysis
- [`python.analysis.include`](python_analysis_include.md) - Include specific files for analysis
- [`python.analysis.diagnosticMode`](python_analysis_languageServerMode.md) - Control diagnostic scope

## Troubleshooting

### Diagnostics Still Appearing

If diagnostics still appear for ignored files:

1. **Check pattern**: Ensure the glob pattern matches the file path
2. **Check precedence**: `include` settings may override `ignore`
3. **Restart language server**: Run "Python: Restart Language Server"
4. **Check workspace root**: Patterns are relative to workspace root

### Imports Not Resolving

If imports from ignored files don't resolve:

1. **Check file exists**: Ensure the ignored file actually exists
2. **Check indexing**: Verify indexing is enabled
3. **Use `exclude` instead**: If you want to completely remove files, use `exclude`

### Performance Issues

If you have many ignored files:

1. **Consider `exclude`**: If you don't need import resolution, use `exclude`
2. **Limit patterns**: Be specific with ignore patterns
3. **Check indexing**: See [Performance Tuning](../howto/settings-troubleshooting.md#performance)

## See Also

- [Settings Troubleshooting](../howto/settings-troubleshooting.md)
- [Fix Unresolved Imports](../howto/fix-unresolved-imports.md)