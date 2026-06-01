# python.analysis.nodeExecutable

Specifies the path to a custom Node.js executable to use for running the Pylance language server.

## Description

Pylance runs on Node.js. By default, it uses the Node.js runtime bundled with VS Code. This setting allows you to specify a custom Node.js executable, which can be useful for:

- Increasing memory limits beyond VS Code's bundled Node.js limits
- Using a specific Node.js version for compatibility
- Debugging language server issues

## Default Value

- **Pylance**: Uses VS Code's bundled Node.js
- **Pyright**: Uses system Node.js or bundled version

## Supported Values

- `null` (default) - Use the default Node.js executable
- `string` - Absolute path to a Node.js executable

## When to Use

### Increasing Memory Limits

VS Code's bundled Node.js has a default heap limit of approximately 4 GB. If you're working with very large codebases and experiencing out-of-memory errors, you can use a custom Node.js executable with increased heap limits via `nodeArguments`.

```json
{
  "python.analysis.nodeExecutable": "/usr/local/bin/node",
  "python.analysis.nodeArguments": ["--max-old-space-size=8192"]
}
```

### Using a Specific Node.js Version

If you need a specific Node.js version for compatibility reasons:

```json
{
  "python.analysis.nodeExecutable": "/path/to/node-v18.0.0/bin/node"
}
```

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.nodeExecutable": "/usr/local/bin/node"
}
```

### pyrightconfig.json

```json
{
  "nodeExecutable": "/usr/local/bin/node"
}
```

### pyproject.toml

```toml
[tool.pyright]
nodeExecutable = "/usr/local/bin/node"
```

## Finding Node.js Path

### macOS/Linux

```bash
# Find the path to the currently active Node.js
which node

# Example output: /usr/local/bin/node
```

### Windows

```cmd
:: Find the path to the currently active Node.js
where node

:: Example output: C:\Program Files\nodejs\node.exe
```

## Memory Considerations

### VS Code Bundled Node.js

- Default heap limit: ~4 GB
- Sufficient for most projects
- Automatically managed by VS Code

### External Node.js

- Can configure heap limits via `nodeArguments`
- Useful for very large codebases
- Requires separate Node.js installation

### Recommended Heap Sizes

| Project Size | Recommended Heap |
|--------------|------------------|
| Small (< 100 files) | Default (4 GB) |
| Medium (100-1000 files) | Default (4 GB) |
| Large (1000-5000 files) | 6-8 GB |
| Very Large (> 5000 files) | 8-12 GB |

## Related Settings

- [`python.analysis.nodeArguments`](python_analysis_nodeArguments.md) - Pass arguments to Node.js (e.g., heap limits)
- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing
- [`python.analysis.userFileIndexingLimit`](python_analysis_userFileIndexingLimit.md) - Limit files to index

## Troubleshooting

### Node.js Not Found

If you see "Node.js not found" errors:

1. **Verify path**: Ensure the path is correct and the executable exists
2. **Check permissions**: Ensure the executable has execute permissions
3. **Use absolute path**: Always use absolute paths, not relative paths
4. **Check Node.js version**: Ensure Node.js version is compatible (v14+)

### Performance Issues

If you experience performance issues after setting a custom executable:

1. **Compare versions**: Ensure your Node.js version is similar to VS Code's bundled version
2. **Check heap size**: Too large a heap can cause garbage collection pauses
3. **Revert to default**: Try removing the setting to use the default

### Out of Memory

If you still experience out-of-memory errors:

1. **Increase heap limit**: Use `nodeArguments` with `--max-old-space-size`
2. **Reduce indexing**: Disable indexing or reduce `userFileIndexingLimit`
3. **Exclude directories**: Use `exclude` to reduce analyzed files

## Security Note

> **Warning**: Only use Node.js executables from trusted sources. Using an untrusted executable could compromise your system.

## See Also

- [nodeArguments for Heap Limits](python_analysis_nodeArguments.md)
- [Performance Tuning](../howto/settings-troubleshooting.md#performance)
- [Memory Considerations for includeVenvInWorkspaceSymbols](python_analysis_includeVenvInWorkspaceSymbols.md)