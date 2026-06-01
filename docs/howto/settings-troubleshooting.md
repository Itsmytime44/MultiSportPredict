# How to Troubleshoot Pylance Settings

A comprehensive guide to diagnosing and resolving configuration issues with Pylance and Pyright.

## Configuration Precedence

Understanding which settings take precedence is crucial for troubleshooting. Settings are applied in this order (later overrides earlier):

1. **Default values** - Built-in defaults
2. **pyrightconfig.json** - Project configuration (nearest to workspace root)
3. **pyproject.toml** - Project configuration with `[tool.pyright]` section
4. **VS Code workspace settings** - `.vscode/settings.json`
5. **VS Code user settings** - Global user settings
6. **Environment-specific config** - `pyrightconfig.<env>.json`

### Example Precedence

```
Project structure:
/home/user/project/
├── pyrightconfig.json          # Sets typeCheckingMode: "basic"
├── .vscode/
│   └── settings.json           # Sets typeCheckingMode: "strict"
└── src/
    └── main.py
```

**Result**: `main.py` uses `strict` type checking (workspace settings override project config).

## Common Configuration Conflicts

### 1. Conflicting Type Checking Modes

**Symptom**: Different files show different diagnostic severity.

**Cause**: Multiple configuration files with different `typeCheckingMode` values.

**Solution**:
```json
// Check effective configuration
// Run: Pyright: Show Language Server Output
// Look for "configuration" section
```

### 2. Include/Exclude/Ignore Conflicts

**Symptom**: Files are analyzed when they shouldn't be, or vice versa.

**Cause**: Overlapping patterns in include/exclude/ignore settings.

**Solution**: Review the interaction:

| Setting | Effect on File Discovery | Effect on Diagnostics | Effect on Import Resolution |
|---------|-------------------------|----------------------|----------------------------|
| `include` | Only included files are candidates | Diagnostics reported | Imports resolved |
| `exclude` | Excluded files removed from candidates | No diagnostics | Imports still resolved |
| `ignore` | Files still in candidates | Diagnostics suppressed | Imports resolved |

**Important**: Import resolution works independently. Even excluded files can be imported if they exist.

### 3. extraPaths vs autoSearchPaths

**Symptom**: Imports work in some files but not others.

**Cause**: `autoSearchPaths` may conflict with manually configured `extraPaths`.

**Solution**:
```json
{
  "python.analysis.autoSearchPaths": false,
  "python.analysis.extraPaths": ["src", "lib"]
}
```

## Diagnostic Steps

### Step 1: Check Effective Configuration

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run: `Pyright: Show Language Server Output`
3. Look for configuration section

### Step 2: Verify Settings Location

Check settings in order of precedence:

1. Project root: `pyrightconfig.json` or `pyproject.toml`
2. Workspace: `.vscode/settings.json`
3. User: VS Code Settings (`Ctrl+,`)

### Step 3: Check for Syntax Errors

Invalid JSON or TOML syntax can cause settings to be ignored:

```bash
# Validate JSON
python -m json.tool pyrightconfig.json

# Validate TOML
python -m tomlkit pyproject.toml
```

### Step 4: Restart Language Server

After making changes:

1. Open Command Palette
2. Run: `Python: Restart Language Server`

## Performance Troubleshooting

### High Memory Usage

**Symptoms**: VS Code becomes slow, out-of-memory errors.

**Solutions**:

1. **Increase heap limit** (if using external Node.js):
```json
{
  "python.analysis.nodeExecutable": "/usr/local/bin/node",
  "python.analysis.nodeArguments": ["--max-old-space-size=8192"]
}
```

> **Note**: VS Code's bundled Node.js has a default heap limit of ~4 GB. For larger limits, use an external Node.js executable.

2. **Reduce indexing scope**:
```json
{
  "python.analysis.indexing": "off",
  "python.analysis.userFileIndexingLimit": 1000
}
```

3. **Exclude large directories**:
```json
{
  "python.analysis.exclude": [
    "**/node_modules/**",
    "**/.venv/**",
    "**/venv/**",
    "**/__pycache__/**"
  ]
}
```

### Slow Analysis

**Symptoms**: Long delays before diagnostics appear.

**Solutions**:

1. **Use workspace mode**:
```json
{
  "python.analysis.languageServerMode": "workspace"
}
```

2. **Disable unnecessary features**:
```json
{
  "python.analysis.autoImportCompletions": false,
  "python.analysis.includeVenvInWorkspaceSymbols": false
}
```

3. **Limit file scope**:
```json
{
  "python.analysis.include": ["src/**/*.py"],
  "python.analysis.exclude": ["**/test*/**", "**/migrations/**"]
}
```

## Auto-Import and Completions Issues

### Completions or Auto-Imports Not Showing

**Symptoms**: No autocomplete suggestions, auto-imports don't work.

**Diagnostic Steps**:

1. **Check indexing is enabled**:
```json
{
  "python.analysis.indexing": "on"
}
```

2. **Check auto-import completions**:
```json
{
  "python.analysis.autoImportCompletions": true
}
```

3. **Verify extraPaths**:
```json
{
  "python.analysis.extraPaths": ["src", "lib"]
}
```

4. **Check autoSearchPaths**:
```json
{
  "python.analysis.autoSearchPaths": true
}
```

5. **Restart language server** after changes.

### Wrong Import Style

**Symptoms**: Auto-imports use wrong style (relative vs absolute).

**Solution**:
```json
{
  "python.analysis.importFormat": "absolute"  // or "relative" or "both"
}
```

## Settings Override Table

| Setting | VS Code settings.json | pyrightconfig.json | pyproject.toml |
|---------|----------------------|--------------------|----------------|
| `python.analysis.autoSearchPaths` | ✅ | ✅ | ✅ |
| `python.analysis.enablePytestSupport` | ✅ | ✅ | ✅ |
| `python.analysis.exclude` | ✅ | ✅ | ✅ |
| `python.analysis.extraPaths` | ✅ | ✅ | ✅ |
| `python.analysis.ignore` | ✅ | ✅ | ✅ |
| `python.analysis.include` | ✅ | ✅ | ✅ |
| `python.analysis.includeAliasesFromUserFiles` | ✅ | ✅ | ✅ |
| `python.analysis.includeExtraPathSymbolsInSymbolSearch` | ✅ | ✅ | ✅ |
| `python.analysis.includeVenvInWorkspaceSymbols` | ✅ | ✅ | ✅ |
| `python.analysis.indexing` | ✅ | ✅ | ✅ |
| `python.analysis.nodeArguments` | ✅ | ✅ | ✅ |
| `python.analysis.nodeExecutable` | ✅ | ✅ | ✅ |
| `python.analysis.packageIndexDepths` | ✅ | ✅ | ✅ |
| `python.analysis.stubPath` | ✅ | ✅ | ✅ |
| `python.analysis.typeCheckingMode` | ✅ | ✅ | ✅ |
| `python.analysis.typeshedPaths` | ✅ | ✅ | ✅ |
| `python.analysis.useLibraryCodeForTypes` | ✅ | ✅ | ✅ |
| `python.analysis.useNearestConfiguration` | ✅ | ✅ | ✅ |
| `python.analysis.userFileIndexingLimit` | ✅ | ✅ | ✅ |
| `python.analysis.languageServerMode` | ✅ | ✅ | ✅ |
| `python.analysis.persistAllIndices` | ✅ | ✅ | ✅ |
| `python.analysis.importFormat` | ✅ | ✅ | ✅ |

### Type Evaluation Settings

| Setting | VS Code settings.json | pyrightconfig.json | pyproject.toml |
|---------|----------------------|--------------------|----------------|
| `python.analysis.typeEvaluation.*` | ✅ | ✅ | ✅ |

## Virtual Environment Issues

### Wrong Interpreter Selected

**Symptoms**: Imports from packages not found, wrong Python version.

**Solution**:

1. Open Command Palette
2. Run: `Python: Select Interpreter`
3. Choose the correct virtual environment

### venv Not Activated

**Symptoms**: Package imports fail, Pylance uses system Python.

**Solution**:

1. Activate virtual environment in terminal
2. Reload VS Code window
3. Or manually set Python path in settings:
```json
{
  "python.defaultInterpreterPath": "/path/to/venv/bin/python"
}
```

## Remote Development Issues

### WSL Configuration

When working in WSL, ensure configuration files are in the WSL filesystem:

```
\\wsl$\Ubuntu\home\user\project\pyrightconfig.json
```

### Dev Containers

Configuration should be in the container workspace:

```
/workspace/project/pyrightconfig.json
```

### Remote SSH

Configuration should be on the remote machine:

```
/home/user/project/pyrightconfig.json
```

## Quick Reference: Common Fixes

| Problem | Quick Fix |
|---------|-----------|
| Out of memory | Increase heap limit or reduce indexing |
| Slow analysis | Narrow include scope, exclude more |
| Imports not found | Check extraPaths, autoSearchPaths |
| Wrong type checking | Check precedence, restart server |
| No completions | Enable indexing, check autoImportCompletions |
| Wrong import style | Set importFormat |

## See Also

- [Fix Unresolved Imports](fix-unresolved-imports.md)
- [Remote Development Guide](remote-development.md)
- [Performance Tuning](#performance-troubleshooting)