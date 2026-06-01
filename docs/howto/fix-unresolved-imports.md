# How to Fix Unresolved Import Errors in Pylance

A comprehensive guide to diagnosing and resolving import resolution issues in Pylance and Pyright.

## Understanding Import Resolution

Pylance uses several mechanisms to resolve imports:

1. **Standard library** - Built-in Python modules
2. **Virtual environment** - Packages installed in the active venv
3. **Workspace paths** - Files in your project
4. **Extra paths** - Manually configured additional paths
5. **Auto-search paths** - Automatically discovered paths (src/, lib/, etc.)

## Common Import Error Types

### 1. Import Not Resolved

**Error**: `Import "my_module" could not be resolved`

**Causes**:
- Module not installed in virtual environment
- Module path not in search paths
- Wrong interpreter selected

**Solutions**:

#### Check Interpreter

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run: `Python: Select Interpreter`
3. Choose the correct virtual environment

#### Install Missing Package

```bash
# Activate your virtual environment first
pip install my_module
```

#### Add Extra Paths

If the module is in your project but not in a standard location:

```json
{
  "python.analysis.extraPaths": ["./my_custom_path"]
}
```

### 2. Relative Import Not Resolved

**Error**: `Import ".sibling_module" could not be resolved`

**Causes**:
- File not in a package (missing `__init__.py`)
- Relative import used outside of package

**Solutions**:

#### Ensure Package Structure

```
my_project/
├── my_package/
│   ├── __init__.py          # Required for package
│   ├── module_a.py
│   └── module_b.py
```

#### Use Absolute Imports

Instead of:
```python
from .sibling_module import something
```

Use:
```python
from my_package.sibling_module import something
```

### 3. Conditional Import Not Resolved

**Error**: `Import "optional_module" could not be resolved from type "module"`

**Causes**:
- Module only available in certain environments
- Optional dependency not installed

**Solutions**:

#### Use Type Ignore

```python
try:
    import optional_module  # type: ignore[import-not-found]
except ImportError:
    optional_module = None
```

#### Add to Settings

```json
{
  "python.analysis.ignore": ["**/optional/**/*.py"]
}
```

## Diagnostic Steps

### Step 1: Verify File Exists

```bash
# Check if the module file exists
find . -name "my_module.py"

# Or check if package is installed
pip show my_module
```

### Step 2: Check Python Path

In a Python shell:

```python
import sys
print(sys.path)
```

### Step 3: Check Pylance Output

1. Open Command Palette
2. Run: `Pyright: Show Language Server Output`
3. Look for import resolution messages

### Step 4: Test Import Manually

```python
# In a Python shell
import my_module
print(my_module.__file__)
```

## Solutions by Scenario

### Scenario 1: Monorepo with Multiple Packages

```
monorepo/
├── package_a/
│   └── src/
│       └── my_module.py
└── package_b/
    └── src/
        └── main.py
```

**Problem**: `package_b` can't import from `package_a`.

**Solution**:

```json
{
  "python.analysis.extraPaths": [
    "../package_a/src",
    "./src"
  ]
}
```

### Scenario 2: src/ Layout

```
my_project/
├── src/
│   └── my_package/
│       └── module.py
└── tests/
    └── test_module.py
```

**Problem**: Tests can't import from src/.

**Solution**:

```json
{
  "python.analysis.autoSearchPaths": true
}
```

Or manually:

```json
{
  "python.analysis.extraPaths": ["src"]
}
```

### Scenario 3: Namespace Packages

```
my_project/
├── my_namespace/
│   └── my_package/
│       └── __init__.py
```

**Problem**: Namespace package not recognized.

**Solution**:

Ensure proper namespace package structure (no `__init__.py` in namespace directory) or use:

```json
{
  "python.analysis.extraPaths": ["."]
}
```

### Scenario 4: Development Install

```bash
# Install package in development mode
pip install -e .
```

This creates proper egg-link files that Pylance can resolve.

## Configuration Examples

### Basic Setup

```json
{
  "python.analysis.autoSearchPaths": true,
  "python.analysis.extraPaths": ["src", "lib"],
  "python.analysis.include": ["src/**/*.py"]
}
```

### Complex Monorepo

```json
{
  "python.analysis.autoSearchPaths": false,
  "python.analysis.extraPaths": [
    "packages/core/src",
    "packages/utils/src",
    "packages/api/src"
  ],
  "python.analysis.include": [
    "packages/*/src/**/*.py"
  ]
}
```

### With Virtual Environment

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.analysis.autoSearchPaths": true,
  "python.analysis.extraPaths": ["src"]
}
```

## Troubleshooting Checklist

- [ ] Correct interpreter selected
- [ ] Package installed in virtual environment
- [ ] `__init__.py` files present for packages
- [ ] Extra paths configured for non-standard locations
- [ ] Auto-search paths enabled for common patterns
- [ ] File paths are correct (case-sensitive on Linux/macOS)
- [ ] Language server restarted after configuration changes

## Performance Considerations

Adding too many extra paths can slow down analysis. Best practices:

1. **Be specific**: Only add necessary paths
2. **Use autoSearchPaths**: Let Pylance discover common patterns
3. **Exclude unnecessary directories**:
```json
{
  "python.analysis.exclude": [
    "**/node_modules/**",
    "**/.venv/**",
    "**/venv/**"
  ]
}
```

## See Also

- [Settings Troubleshooting](settings-troubleshooting.md)
- [autoSearchPaths](../settings/python_analysis_autoSearchPaths.md)
- [extraPaths](../settings/python_analysis_extraPaths.md)
- [include](../settings/python_analysis_include.md)