# python.analysis.persistAllIndices

Controls whether Pylance/Pyright persists all indices to disk for faster startup on subsequent runs.

## Description

When enabled, this setting saves the analysis indices (type information, symbols, etc.) to disk so that they can be quickly loaded on the next VS Code startup, significantly reducing startup time for large projects.

## Default Value

- **Pylance**: `true`
- **Pyright**: `true`

## Supported Values

- `true` - Persist indices to disk (faster startup)
- `false` - Do not persist indices (slower startup, less disk usage)

## How It Works

### With persistAllIndices Enabled

1. **First Startup**: Analysis is performed and indices are saved to disk
2. **Subsequent Startups**: Indices are loaded from disk (much faster)
3. **On Changes**: Indices are updated and re-saved

### With persistAllIndices Disabled

1. **Every Startup**: Analysis is performed from scratch
2. **No Disk Cache**: No indices are saved
3. **Slower Startup**: Takes longer to become ready

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.persistAllIndices": true
}
```

### pyrightconfig.json

```json
{
  "persistAllIndices": true
}
```

### pyproject.toml

```toml
[tool.pyright]
persistAllIndices = true
```

## Performance Impact

### Startup Time

| Setting | First Startup | Subsequent Startups |
|---------|---------------|---------------------|
| `true` | Normal | Fast (loads from disk) |
| `false` | Normal | Slow (re-analyzes everything) |

### Disk Usage

| Setting | Disk Usage |
|---------|------------|
| `true` | Higher (stores indices) |
| `false` | Minimal |

### Memory Usage

| Setting | Memory Usage |
|---------|--------------|
| `true` | Similar (indices in memory) |
| `false` | Similar |

## When to Disable

You might want to disable this setting in these scenarios:

1. **Disk space constraints**: Indices can take up significant disk space
2. **Debugging**: To ensure fresh analysis every time
3. **CI/CD**: Not needed in continuous integration environments
4. **Rarely used projects**: Projects you open infrequently

## Cache Location

The indices are typically stored in:

- **Windows**: `%APPDATA%\Code\User\globalStorage\ms-python.vscode-pylance`
- **macOS**: `~/Library/Application Support/Code/User/globalStorage/ms-python.vscode-pylance`
- **Linux**: `~/.config/Code/User/globalStorage/ms-python.vscode-pylance`

## Related Settings

- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing
- [`python.analysis.userFileIndexingLimit`](python_analysis_userFileIndexingLimit.md) - Limit files to index
- [`python.analysis.languageServerMode`](python_analysis_languageServerMode.md) - Control language server mode

## Troubleshooting

### Stale Cache Issues

If you're seeing outdated type information:

1. **Clear cache**: Delete the Pylance cache directory
2. **Restart VS Code**: Fully restart VS Code
3. **Disable and re-enable**: Set `persistAllIndices` to `false`, restart, then set back to `true`

### High Disk Usage

If Pylance is using too much disk space:

1. **Disable persistAllIndices**: Set to `false`
2. **Clear cache**: Delete the cache directory
3. **Reduce indexing**: Use `userFileIndexingLimit` to limit indexed files

### Slow Startup Despite persistAllIndices

If startup is still slow:

1. **Check indexing**: Ensure `indexing` is enabled
2. **Reduce indexed files**: Lower `userFileIndexingLimit`
3. **Check disk speed**: Slow disks can impact cache loading

## Best Practices

1. **Keep enabled**: Provides the best experience for most users
2. **Clear periodically**: Clear cache if you notice issues
3. **Disable for CI**: Not needed in CI environments
4. **Monitor disk usage**: Check cache size occasionally

## See Also

- [Performance Tuning](../howto/settings-troubleshooting.md#performance-troubleshooting)
- [Indexing Configuration](python_analysis_indexing.md)
- [Settings Troubleshooting](../howto/settings-troubleshooting.md)