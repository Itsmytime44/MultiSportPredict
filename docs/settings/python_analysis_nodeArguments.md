# python.analysis.nodeArguments

Passes command-line arguments to the Node.js process running the Pylance language server.

## Description

This setting allows you to pass custom arguments to the Node.js runtime that powers Pylance. The most common use case is increasing the heap memory limit for large codebases.

## Default Value

- **Pylance**: `[]` (no additional arguments)
- **Pyright**: `[]` (no additional arguments)

## Supported Values

- Array of strings representing Node.js command-line arguments

## Common Use Cases

### Increasing Heap Memory Limit

The most common use case is increasing the V8 heap limit for large codebases:

```json
{
  "python.analysis.nodeArguments": ["--max-old-space-size=8192"]
}
```

This sets the heap limit to 8 GB. The value is in megabytes.

### Recommended Heap Sizes

| Project Size | Recommended Heap | nodeArguments Value |
|--------------|------------------|---------------------|
| Small (< 100 files) | Default (4 GB) | Not needed |
| Medium (100-1000 files) | Default (4 GB) | Not needed |
| Large (1000-5000 files) | 6-8 GB | `["--max-old-space-size=6144"]` |
| Very Large (> 5000 files) | 8-12 GB | `["--max-old-space-size=8192"]` |

### Multiple Arguments

You can pass multiple arguments:

```json
{
  "python.analysis.nodeArguments": [
    "--max-old-space-size=8192",
    "--max-semi-space-size=64"
  ]
}
```

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.nodeArguments": ["--max-old-space-size=8192"]
}
```

### pyrightconfig.json

```json
{
  "nodeArguments": ["--max-old-space-size=8192"]
}
```

### pyproject.toml

```toml
[tool.pyright]
nodeArguments = ["--max-old-space-size=8192"]
```

## Important Node.js Arguments

### Memory-Related

| Argument | Description | Example |
|----------|-------------|---------|
| `--max-old-space-size` | Max size of old space (MB) | `--max-old-space-size=8192` |
| `--max-semi-space-size` | Max size of semi space (MB) | `--max-semi-space-size=64` |
| `--initial-old-space-size` | Initial size of old space (MB) | `--initial-old-space-size=2048` |

### Debugging

| Argument | Description | Example |
|----------|-------------|---------|
| `--inspect` | Enable inspector agent | `--inspect` |
| `--inspect-brk` | Enable inspector and break on start | `--inspect-brk` |

## When to Use

### Out of Memory Errors

If you see out-of-memory errors in the Pylance output:

```
<--- Last few GCs --->
FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
```

**Solution**: Increase the heap limit:

```json
{
  "python.analysis.nodeArguments": ["--max-old-space-size=8192"]
}
```

### Large Codebases

For codebases with thousands of files or complex type relationships:

1. Start with 6 GB: `["--max-old-space-size=6144"]`
2. Monitor memory usage
3. Increase if needed

### Performance Tuning

For performance optimization:

```json
{
  "python.analysis.nodeArguments": [
    "--max-old-space-size=4096",
    "--initial-old-space-size=1024"
  ]
}
```

## Important Considerations

### VS Code Bundled Node.js vs External

| Factor | VS Code Bundled | External Node.js |
|--------|-----------------|------------------|
| Default heap | ~4 GB | Configurable |
| Max heap | Limited by OS | Configurable |
| Setup | No setup needed | Requires `nodeExecutable` |

> **Note**: When using VS Code's bundled Node.js, the maximum heap size may be limited. For heap sizes above 4 GB, consider using an external Node.js executable with `python.analysis.nodeExecutable`.

### System Memory

Ensure your system has enough physical memory:

- Heap size should not exceed available RAM
- Leave memory for OS and other applications
- Consider swap space on Linux/macOS

### Performance Impact

Larger heap sizes can:

- **Pros**: Reduce garbage collection frequency
- **Cons**: Longer GC pauses when they occur
- **Balance**: Find the right size for your codebase

## Related Settings

- [`python.analysis.nodeExecutable`](python_analysis_nodeExecutable.md) - Specify custom Node.js executable
- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing
- [`python.analysis.userFileIndexingLimit`](python_analysis_userFileIndexingLimit.md) - Limit files to index

## Troubleshooting

### Arguments Not Applied

If arguments don't seem to be applied:

1. **Restart language server**: Run "Python: Restart Language Server"
2. **Check syntax**: Ensure arguments are in correct format
3. **Check Node.js version**: Some arguments require specific Node.js versions
4. **Use external Node.js**: Some arguments may not work with bundled Node.js

### Still Out of Memory

If you still see out-of-memory errors after increasing heap:

1. **Increase further**: Try 12 GB or more
2. **Reduce indexing**: Set `userFileIndexingLimit` lower
3. **Exclude files**: Use `exclude` to reduce analyzed files
4. **Use external Node.js**: Set `nodeExecutable` for more control

### Performance Degradation

If performance worsens after setting arguments:

1. **Reduce heap size**: Too large a heap can cause long GC pauses
2. **Check semi-space size**: Adjust `--max-semi-space-size`
3. **Monitor memory**: Use system tools to monitor actual usage

## Security Note

> **Warning**: Be cautious when passing arguments to Node.js. Malicious or incorrect arguments could cause unexpected behavior.

## See Also

- [nodeExecutable for Custom Node.js](python_analysis_nodeExecutable.md)
- [Performance Tuning](../howto/settings-troubleshooting.md#performance)
- [Memory Considerations](python_analysis_includeVenvInWorkspaceSymbols.md#memory-considerations)