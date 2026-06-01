# python.analysis.typeshedPaths

Specifies additional paths to search for typeshed-compatible type stub files.

## Description

Typeshed is a repository of type stub files for Python standard library and common third-party packages. This setting allows you to specify additional paths where Pylance/Pyright should look for typeshed-compatible stub files.

## Default Value

- **Pylance**: `[]` (uses bundled typeshed)
- **Pyright**: `[]` (uses bundled typeshed)

## Supported Values

Array of strings representing absolute or relative paths to typeshed directories.

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.typeshedPaths": [
    "./custom-typeshed",
    "/path/to/typeshed"
  ]
}
```

### pyrightconfig.json

```json
{
  "typeshedPaths": [
    "./custom-typeshed",
    "/path/to/typeshed"
  ]
}
```

### pyproject.toml

```toml
[tool.pyright]
typeshedPaths = [
    "./custom-typeshed",
    "/path/to/typeshed"
]
```

## Directory Structure

The typeshed directory should follow this structure:

```
typeshed/
├── stdlib/
│   ├── typing.pyi
│   ├── os.pyi
│   └── ...
├── third_party/
│   ├── requests/
│   │   └── __init__.pyi
│   └── ...
└── VERSIONS
```

## When to Use

### 1. Custom Typeshed Fork

When you maintain a fork of typeshed with custom modifications:

```json
{
  "python.analysis.typeshedPaths": [
    "/path/to/my-typeshed-fork"
  ]
}
```

### 2. Organization-Wide Stubs

When your organization maintains custom stubs for internal packages:

```json
{
  "python.analysis.typeshedPaths": [
    "/shared/stubs/typeshed"
  ]
}
```

### 3. Updated Stubs

When you need newer stubs than what's bundled with Pylance:

```bash
# Clone latest typeshed
git clone https://github.com/python/typeshed.git ~/typeshed
```

```json
{
  "python.analysis.typeshedPaths": [
    "~/typeshed"
  ]
}
```

## Search Order

Pylance/Pyright searches for stubs in this order:

1. **Project stubs**: `stubPath` setting
2. **Custom typeshed**: `typeshedPaths` settings (in order)
3. **Bundled typeshed**: Built-in typeshed
4. **Installed stubs**: `types-*` packages

## Related Settings

- [`python.analysis.stubPath`](python_analysis_stubPath.md) - Custom path for project stub files
- [`python.analysis.useLibraryCodeForTypes`](python_analysis_useLibraryCodeForTypes.md) - Use library code for types
- [`python.analysis.extraPaths`](python_analysis_extraPaths.md) - Additional import paths

## Troubleshooting

### Stubs Not Found

If custom typeshed stubs aren't being recognized:

1. **Check path**: Ensure path is correct and directory exists
2. **Verify structure**: Ensure directory follows typeshed structure
3. **Check VERSIONS file**: Ensure VERSIONS file exists
4. **Restart language server**: Run "Python: Restart Language Server"

### Conflicting Stubs

If you have conflicting stub definitions:

1. **Check search order**: Earlier paths take precedence
2. **Reorder paths**: Put preferred stubs first in `typeshedPaths`
3. **Remove duplicates**: Ensure only one definition exists

## Best Practices

1. **Use sparingly**: Most users don't need custom typeshed paths
2. **Prefer types packages**: Install `types-*` packages when possible
3. **Keep updated**: Regularly update custom typeshed forks
4. **Document changes**: Track why custom typeshed is needed

## See Also

- [Typeshed Repository](https://github.com/python/typeshed)
- [Stub Path Configuration](python_analysis_stubPath.md)
- [PEP 561 - Stub Support](https://peps.python.org/pep-0561/)