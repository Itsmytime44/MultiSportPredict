# python.analysis.importFormat

Controls whether auto-imports use relative or absolute import paths.

## Description

This setting determines the style of import statements that Pylance suggests when you use auto-import completions. It affects how imports are formatted when you accept a completion suggestion.

## Default Value

- **Pylance**: `"absolute"`
- **Pyright**: `"absolute"`

## Supported Values

| Value | Description |
|-------|-------------|
| `"absolute"` | Use absolute imports (e.g., `from mypackage.module import MyClass`) |
| `"relative"` | Use relative imports (e.g., `from .module import MyClass`) |
| `"both"` | Suggest both absolute and relative imports |

## Examples

### Absolute Imports (Default)

```python
# File: src/mypackage/subpackage/module.py
from mypackage.utils import helper_function
from mypackage.models import User
```

### Relative Imports

```python
# File: src/mypackage/subpackage/module.py
from ..utils import helper_function
from ..models import User
```

### Both

When set to `"both"`, Pylance will suggest both styles in completions.

## Configuration

### VS Code settings.json

```json
{
  "python.analysis.importFormat": "absolute"
}
```

### pyrightconfig.json

```json
{
  "importFormat": "absolute"
}
```

### pyproject.toml

```toml
[tool.pyright]
importFormat = "absolute"
```

## When to Use Each

### Absolute Imports

**Best for:**
- Most projects
- Clear, explicit import paths
- Easier refactoring
- Better for larger codebases

### Relative Imports

**Best for:**
- Package-internal imports
- When package name is very long
- When moving packages frequently
- Smaller, tightly-coupled packages

### Both

**Best for:**
- Projects with mixed import styles
- When you want flexibility in choosing per-import

## Related Settings

### Auto-Import Completions

| Setting | Description |
|---------|-------------|
| [`python.analysis.autoImportCompletions`](python_analysis_autoImportCompletions.md) | Enable/disable auto-import suggestions |
| [`python.analysis.extraPaths`](python_analysis_extraPaths.md) | Additional paths for import resolution |
| [`python.analysis.autoSearchPaths`](python_analysis_autoSearchPaths.md) | Auto-detect search paths |

### Fix All Configuration

| Setting | Description |
|---------|-------------|
| [`python.analysis.fixAll`](python_analysis_fixAll.md) | Automatically fix certain issues on save |

## Troubleshooting

### Wrong Import Style Suggested

If Pylance suggests the wrong import style:

1. **Check setting**: Verify `importFormat` is set correctly
2. **Check file location**: Relative imports only work within packages
3. **Restart language server**: Run "Python: Restart Language Server"
4. **Check package structure**: Ensure `__init__.py` files exist

### No Auto-Import Suggestions

If you don't see auto-import suggestions:

1. **Enable auto-imports**: Set `python.analysis.autoImportCompletions` to `true`
2. **Check indexing**: Ensure indexing is enabled
3. **Check extraPaths**: Add necessary paths to `extraPaths`

### Relative Imports Not Working

If relative imports aren't suggested:

1. **Check package structure**: File must be in a package (with `__init__.py`)
2. **Set importFormat**: Set to `"relative"` or `"both"`
3. **Check file location**: Relative imports only work within packages

## Best Practices

1. **Be consistent**: Choose one style and stick with it
2. **Prefer absolute**: Absolute imports are generally clearer
3. **Consider team**: Follow your team's coding standards
4. **PEP 8**: Follow Python style guide recommendations

## See Also

- [Settings Troubleshooting](../howto/settings-troubleshooting.md)
- [Fix Unresolved Imports](../howto/fix-unresolved-imports.md)
- [PEP 8 - Imports](https://pep8.org/#imports)