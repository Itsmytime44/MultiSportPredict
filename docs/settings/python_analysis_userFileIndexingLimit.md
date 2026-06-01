# python.analysis.userFileIndexingLimit

Limits the number of user (workspace) files that Pylance/Pyright will index.

## Description

This setting controls how many files in your workspace (not libraries) will be indexed for faster symbol search and autocomplete. Setting a limit helps manage memory usage and performance in large codebases.

## Default Value

- **Pylance**: `2000`
- **Pyright**: `2000`

## Supported Values

- `0` - Disable user file indexing
- `positive integer` - Maximum number of files to index
- `null` - No limit (index all files)

## How It Works

### Indexing Process

1. **File Discovery**: Pylance discovers Python files in your workspace
2. **Selection**: Selects up to the limit number of files
3. **Analysis**: Analyzes selected files to extract symbols and types
4. **Caching**: Caches results for fast access

### File Selection

Files are typically selected based on:
- Files in included directories (see [`include`](python_analysis_include.md))
- Files not in excluded directories (see [`exclude`](python_analysis_ignore.md))
- Most recently modified files (prioritized)

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.userFileIndexingLimit": 2000
}
```

### pyrightconfig.json

```json
{
  "userFileIndexingLimit": 2000
}
```

### pyproject.toml

```toml
[tool.pyright]
userFileIndexingLimit = 2000
```

## When to Adjust

### Increase the Limit

Consider increasing the limit when:

- Your codebase has more than 2000 files
- You need symbols from many files for autocomplete
- You have sufficient memory available
- You frequently search across the entire codebase

```json
{
  "python.analysis.userFileIndexingLimit": 5000
}
```

### Decrease the Limit

Consider decreasing the limit when:

- You experience high memory usage
- VS Code becomes slow during indexing
- Your codebase is small (< 1000 files)
- You only work in a few files at a time

```json
{
  "python.analysis.userFileIndexingLimit": 500
}
```

### Disable User File Indexing

Set to `0` to disable:

```json
{
  "python.analysis.userFileIndexingLimit": 0
}
```

This can improve performance in very large codebases where indexing all files is impractical.

## Performance Considerations

### Memory Usage

| Limit | Memory Impact |
|-------|---------------|
| `0` | Minimal - no user file indexing |
| `500` | Low |
| `2000` (default) | Moderate |
| `5000` | High |
| `null` (unlimited) | Very high for large codebases |

### Autocomplete Quality

| Limit | Autocomplete Impact |
|-------|---------------------|
| `0` | Limited - only current file and libraries |
| `500` | Good for small projects |
| `2000` (default) | Good for most projects |
| `5000` | Excellent for large projects |
| `null` (unlimited) | Complete coverage |

### Startup Time

| Limit | Startup Impact |
|-------|----------------|
| `0` | Fastest |
| `500` | Fast |
| `2000` (default) | Moderate |
| `5000` | Slower |
| `null` (unlimited) | Slowest for large codebases |

## Related Settings

- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing
- [`python.analysis.persistAllIndices`](python_analysis_persistAllIndices.md) - Persist indices to disk
- [`python.analysis.include`](python_analysis_include.md) - Include specific files for analysis
- [`python.analysis.exclude`](python_analysis_ignore.md) - Exclude files from analysis

## Troubleshooting

### High Memory Usage

If Pylance uses too much memory:

1. **Reduce limit**: Set `userFileIndexingLimit` to a lower value
2. **Disable indexing**: Set to `0`
3. **Exclude files**: Use `exclude` to reduce indexed files

### Missing Symbols in Autocomplete

If symbols from your code don't appear in autocomplete:

1. **Increase limit**: Set `userFileIndexingLimit` higher
2. **Check include/exclude**: Ensure files are included
3. **Restart language server**: Run "Python: Restart Language Server"

### Slow Performance

If indexing is slow:

1. **Reduce limit**: Lower the `userFileIndexingLimit`
2. **Exclude directories**: Use `exclude` for non-essential directories
3. **Disable persistAllIndices**: Set to `false`

## Best Practices

1. **Start with default**: 2000 is suitable for most projects
2. **Monitor memory**: Adjust based on your system's memory
3. **Use with exclude**: Combine with `exclude` to focus indexing
4. **Consider project size**: Match limit to your codebase size

## See Also

- [Performance Tuning](../howto/settings-troubleshooting.md#performance-troubleshooting)
- [Indexing Configuration](python_analysis_indexing.md)
- [Settings Troubleshooting](../howto/settings-troubleshooting.md)