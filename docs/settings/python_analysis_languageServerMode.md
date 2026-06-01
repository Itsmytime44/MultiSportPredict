# python.analysis.languageServerMode

Controls the operating mode of the language server, optimizing for different use cases.

## Description

This setting determines how the language server prioritizes its resources and features. Different modes optimize for document responsiveness, workspace-wide analysis, or full IDE features.

## Default Value

- **Pylance**: `"document"` (optimized for responsiveness)
- **Pyright**: `"document"` (optimized for responsiveness)

## Supported Values

| Value | Description |
|-------|-------------|
| `"document"` | Optimize for document responsiveness (default) |
| `"workspace"` | Optimize for workspace-wide analysis |
| `"ide"` | Full IDE mode with all features enabled |

## Mode Details

### document

- **Priority**: Fast response to user actions in the current document
- **Diagnostics**: Only for open files
- **Autocomplete**: Fast, focused on current file
- **Memory**: Lower memory usage
- **Best for**: General development, large codebases

### workspace

- **Priority**: Workspace-wide analysis and refactoring
- **Diagnostics**: For all files in workspace
- **Autocomplete**: Includes workspace symbols
- **Memory**: Higher memory usage
- **Best for**: Refactoring, finding references across project

### ide

- **Priority**: Full feature set
- **Diagnostics**: Comprehensive across entire project
- **Autocomplete**: All available symbols
- **Memory**: Highest memory usage
- **Best for**: Small to medium projects, full development experience

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.languageServerMode": "document"
}
```

### pyrightconfig.json

```json
{
  "languageServerMode": "document"
}
```

### pyproject.toml

```toml
[tool.pyright]
languageServerMode = "document"
```

## Performance Comparison

| Feature | document | workspace | ide |
|---------|----------|-----------|-----|
| Startup time | Fast | Medium | Slow |
| Memory usage | Low | Medium | High |
| Diagnostics scope | Open files | Workspace | Full project |
| Autocomplete speed | Fast | Medium | Slow |
| Refactoring | Limited | Good | Full |
| Find all references | Limited | Good | Full |

## When to Use Each Mode

### Use "document" when:

- Working on large codebases
- Memory is limited
- You want fast autocomplete
- You primarily work in one file at a time

### Use "workspace" when:

- You need workspace-wide refactoring
- You frequently search for references
- Your codebase is medium-sized
- You want comprehensive diagnostics

### Use "ide" when:

- Working on small to medium projects
- You want all features available
- Memory is not a constraint
- You need full refactoring support

## Related Settings

- [`python.analysis.indexing`](python_analysis_indexing.md) - Control library indexing
- [`python.analysis.diagnosticMode`](python_analysis_diagnosticMode.md) - Control diagnostic scope
- [`python.analysis.userFileIndexingLimit`](python_analysis_userFileIndexingLimit.md) - Limit files to index

## Troubleshooting

### Slow Performance

If the language server is slow:

1. **Use document mode**: Set `languageServerMode` to `"document"`
2. **Disable indexing**: Set `indexing` to `"off"`
3. **Reduce file scope**: Use `include` and `exclude` settings

### Missing Features

If some features aren't working:

1. **Try workspace mode**: Set `languageServerMode` to `"workspace"`
2. **Check settings**: Ensure related settings are enabled
3. **Restart server**: Run "Python: Restart Language Server"

### High Memory Usage

If VS Code uses too much memory:

1. **Use document mode**: Set `languageServerMode` to `"document"`
2. **Disable persistAllIndices**: Set to `false`
3. **Reduce indexing**: Use `userFileIndexingLimit`

## See Also

- [Performance Tuning](../howto/settings-troubleshooting.md#performance-troubleshooting)
- [Settings Troubleshooting](../howto/settings-troubleshooting.md)