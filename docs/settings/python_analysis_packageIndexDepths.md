# python.analysis.packageIndexDepths

Controls the indexing depth for specific packages, allowing fine-grained performance tuning.

## Description

This setting allows you to specify how deeply Pylance/Pyright should index each package. By controlling indexing depth, you can optimize performance for large packages while maintaining good type information for frequently used ones.

## Default Value

- **Pylance**: `[]` (uses default depth for all packages)
- **Pyright**: `[]` (uses default depth for all packages)

## Supported Values

Array of objects with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Package name (e.g., "numpy", "pandas") |
| `depth` | integer | Indexing depth (0 = no indexing, higher = more detailed) |

## Indexing Depth Levels

| Depth | Description |
|-------|-------------|
| `0` | Do not index this package |
| `1` | Index only top-level symbols |
| `2` | Index one level deep (default) |
| `3+` | Index deeper into package structure |

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.packageIndexDepths": [
    { "name": "numpy", "depth": 1 },
    { "name": "pandas", "depth": 1 },
    { "name": "tensorflow", "depth": 0 },
    { "name": "requests", "depth": 3 }
  ]
}
```

### pyrightconfig.json

```json
{
  "packageIndexDepths": [
    { "name": "numpy", "depth": 1 },
    { "name": "pandas", "depth": 1 },
    { "name": "tensorflow", "depth": 0 },
    { "name": "requests", "depth": 3 }
  ]
}
```

### pyproject.toml

```toml
[tool.pyright]
packageIndexDepths = [
    { name = "numpy", depth = 1 },
    { name = "pandas", depth = 1 },
    { name = "tensorflow", depth = 0 },
    { name = "requests", depth = 3 }
]
```

## Examples

### Reduce Indexing for Large Packages

Large packages like numpy, pandas, and tensorflow can be expensive to index:

```json
{
  "python.analysis.packageIndexDepths": [
    { "name": "numpy", "depth": 1 },
    { "name": "pandas", "depth": 1 },
    { "name": "tensorflow", "depth": 0 },
    { "name": "torch", "depth": 0 }
  ]
}
```

### Increase Indexing for Frequently Used Packages

For packages you use heavily and need detailed type information:

```json
{
  "python.analysis.packageIndexDepths": [
    { "name": "requests", "depth": 3 },
    { "name": "flask", "depth": 3 },
    { "name": "django", "depth": 3 }
  ]
}
```

### Disable Indexing for Specific Packages

To completely skip indexing for packages you don't need type information for:

```json
{
  "python.analysis.packageIndexDepths": [
    { "name": "matplotlib", "depth": 0 },
    { "name": "seaborn", "depth": 0 }
  ]
}
```

## Performance Considerations

### Memory Usage by Package Size

| Package Type | Default Memory | With depth=1 | With depth=0 |
|--------------|----------------|--------------|--------------|
| Small (requests) | Low | Very Low | Minimal |
| Medium (flask) | Moderate | Low | Minimal |
| Large (numpy) | High | Moderate | Minimal |
| Very Large (tensorflow) | Very High | High | Minimal |

### Impact on Autocomplete

| Depth | Autocomplete Quality | Performance |
|-------|---------------------|-------------|
| `0` | No package symbols | Best |
| `1` | Top-level symbols only | Good |
| `2` | Good coverage | Moderate |
| `3+` | Complete coverage | Slower |

## When to Use

### High Memory Usage

If Pylance uses too much memory:

```json
{
  "python.analysis.packageIndexDepths": [
    { "name": "numpy", "depth": 0 },
    { "name": "pandas", "depth": 0 },
    { "name": "tensorflow", "depth": 0 }
  ]
}
```

### Slow Autocomplete

If autocomplete is slow for specific packages:

```json
{
  "python.analysis.packageIndexDepths": [
    { "name": "large_package", "depth": 1 }
  ]
}
```

### Missing Type Information

If you need better type information for a package:

```json
{
  "python.analysis.packageIndexDepths": [
    { "name": "important_package", "depth": 3 }
  ]
}
```

## Related Settings

- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing
- [`python.analysis.userFileIndexingLimit`](python_analysis_userFileIndexingLimit.md) - Limit files to index
- [`python.analysis.persistAllIndices`](python_analysis_persistAllIndices.md) - Persist indices to disk

## Troubleshooting

### Package Symbols Not Found

If symbols from a package don't appear:

1. **Check depth**: Ensure `depth` is not `0`
2. **Increase depth**: Try `depth: 2` or higher
3. **Restart language server**: Run "Python: Restart Language Server"

### Still High Memory

If memory is still high after adjusting:

1. **Reduce more packages**: Set more packages to `depth: 0`
2. **Disable indexing**: Set `indexing` to `"off"`
3. **Check other settings**: Review `userFileIndexingLimit`

## Best Practices

1. **Start with defaults**: Only adjust if you have performance issues
2. **Target large packages**: Focus on numpy, pandas, tensorflow, etc.
3. **Balance quality and performance**: Use `depth: 1` for a good balance
4. **Monitor memory**: Adjust based on actual memory usage

## See Also

- [Performance Tuning](../howto/settings-troubleshooting.md#performance-troubleshooting)
- [Indexing Configuration](python_analysis_indexing.md)
- [Memory Considerations](python_analysis_includeVenvInWorkspaceSymbols.md#memory-considerations)