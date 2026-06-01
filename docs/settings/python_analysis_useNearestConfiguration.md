# python.analysis.useNearestConfiguration

Controls whether Pylance automatically discovers and uses configuration files (pyrightconfig.json, pyproject.toml) from parent directories, enabling support for virtual workspaces and monorepo setups.

## Description

When enabled, this setting allows Pylance to search up the directory tree for configuration files. This is particularly useful in:

- **Monorepos**: Multiple packages with different configurations
- **Virtual workspaces**: Workspace folders with their own settings
- **Nested projects**: Projects within projects with different type checking rules

## Default Value

- **Pylance**: `true`
- **Pyright**: `true`

## Supported Values

- `true` - Automatically discover and use nearest configuration files
- `false` - Only use configuration files in the workspace root

## How It Works

### Configuration Discovery

When `useNearestConfiguration` is enabled, Pylance searches for configuration files in this order:

1. Workspace root directory
2. Parent directory of workspace root
3. Continue up the directory tree until a configuration is found or filesystem root is reached

### Configuration File Priority

| Priority | File | Description |
|----------|------|-------------|
| 1 | `pyrightconfig.json` | Pyright-specific configuration |
| 2 | `pyproject.toml` | Pyproject with `[tool.pyright]` section |
| 3 | `pyrightconfig.<env>.json` | Environment-specific config (e.g., `pyrightconfig.dev.json`) |

### Example Monorepo Structure

```
monorepo/
├── pyrightconfig.json          # Root configuration
│   {
│     "typeCheckingMode": "basic"
│   }
├── packages/
│   ├── package-a/
│   │   ├── pyrightconfig.json  # Package A overrides root
│   │   │   {
│   │   │     "typeCheckingMode": "strict"
│   │   │   }
│   │   └── src/
│   ├── package-b/
│   │   └── src/                # Uses root configuration
│   └── package-c/
│       ├── pyrightconfig.json  # Package C overrides root
│       │   {
│       │     "typeCheckingMode": "off"
│       │   }
│       └── src/
```

With `useNearestConfiguration` enabled:
- `package-a/` uses `strict` type checking
- `package-b/` uses `basic` type checking (from root)
- `package-c/` uses `off` type checking

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.useNearestConfiguration": true
}
```

### pyrightconfig.json

```json
{
  "useNearestConfiguration": true
}
```

### pyproject.toml

```toml
[tool.pyright]
useNearestConfiguration = true
```

## When to Disable

You might want to disable this setting in these scenarios:

1. **Consistent configuration**: You want all files to use the same configuration
2. **Unexpected overrides**: Parent configurations cause unwanted behavior
3. **Performance**: Slight performance improvement by not searching parent directories
4. **Clear boundaries**: You want explicit configuration boundaries

## Virtual Workspace Support

This setting is essential for virtual workspace scenarios:

### Dev Containers

```
project/
├── .devcontainer/
│   └── devcontainer.json
├── pyrightconfig.json
└── src/
```

### WSL

When working in WSL, configurations from the Windows filesystem can be discovered:

```
/mnt/c/projects/myproject/
├── pyrightconfig.json
└── src/
```

### Remote SSH

Remote projects can have their own configurations that are discovered independently.

## Related Settings

- [`python.analysis.typeCheckingMode`](python_analysis_typeCheckingMode.md) - Control type checking strictness
- [`python.analysis.include`](python_analysis_include.md) - Include specific files for analysis
- [`python.analysis.exclude`](python_analysis_ignore.md) - Exclude files from analysis

## Troubleshooting

### Unexpected Configuration Applied

If the wrong configuration is being used:

1. **Check configuration hierarchy**: Look for config files in parent directories
2. **Disable useNearestConfiguration**: Set to `false` to use only workspace root config
3. **Check workspace folders**: Verify VS Code workspace folder boundaries
4. **Use explicit paths**: Specify settings explicitly in workspace root config

### Configuration Not Discovered

If configurations in subdirectories aren't being used:

1. **Verify setting is enabled**: Check `useNearestConfiguration` is `true`
2. **Check file names**: Ensure config files are named correctly
3. **Restart language server**: Run "Python: Restart Language Server"
4. **Check workspace structure**: Ensure subdirectories are separate workspace folders

### Conflicting Configurations

If you see conflicting settings:

1. **Review hierarchy**: Understand which config takes precedence
2. **Use explicit overrides**: Set values explicitly in each config
3. **Document conventions**: Establish clear configuration rules for your team

## Best Practices

1. **Root configuration**: Define sensible defaults in the root configuration
2. **Package overrides**: Only override settings that need to differ
3. **Document structure**: Clearly document your configuration hierarchy
4. **Consistent naming**: Use consistent configuration file names

## See Also

- [Settings Troubleshooting](../howto/settings-troubleshooting.md)
- [Remote Development Guide](../howto/remote-development.md)