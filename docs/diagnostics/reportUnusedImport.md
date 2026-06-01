# reportUnusedImport

Reports when an import statement is present but the imported name is never used in the code.

## Description

This diagnostic is raised when a module, class, function, or variable is imported but never referenced in the code. This helps keep code clean by identifying unnecessary imports that should be removed.

## Default Severity

- **Warning** (in basic/strict mode)
- **Information** (in standard mode)

## Examples

### Example 1: Unused Module Import

```python
import os  # Warning: "os" is imported but never used
import sys

def get_path():
    return sys.path
```

**Fix**: Remove the unused import:

```python
import sys

def get_path():
    return sys.path
```

### Example 2: Unused from Import

```python
from typing import List, Dict, Optional  # Warning: "Dict" is imported but never used

def process(items: List[str]) -> Optional[str]:
    return items[0] if items else None
```

**Fix**: Remove the unused import:

```python
from typing import List, Optional

def process(items: List[str]) -> Optional[str]:
    return items[0] if items else None
```

### Example 3: Unused Aliased Import

```python
import pandas as pd  # Warning: "pd" is imported but never used
import numpy as np

def calculate():
    return np.array([1, 2, 3])
```

**Fix**: Remove the unused import:

```python
import numpy as np

def calculate():
    return np.array([1, 2, 3])
```

### Example 4: Wildcard Import (Not Reported)

```python
from module import *  # No warning - wildcard imports are not checked
```

> **Note**: Wildcard imports (`from x import *`) are not checked for unused imports because it's unclear which names are actually used.

### Example 5: Import Used Only in Type Comments

```python
from typing import List  # Warning: "List" is imported but never used

def process(items):
    # type: (list) -> List[str]  # Type comments don't count as usage
    return [str(item) for item in items]
```

**Fix**: Use type annotations instead of type comments:

```python
from typing import List

def process(items: list) -> List[str]:
    return [str(item) for item in items]
```

### Example 6: Import Used Only in String Annotations

```python
from typing import List  # Warning: "List" is imported but never used

def process(items: "List[str]"):  # String annotations may not be recognized
    return items
```

**Fix**: Use proper type annotations (Python 3.9+):

```python
from typing import List

def process(items: List[str]):
    return items
```

Or enable `from __future__ import annotations`:

```python
from __future__ import annotations
from typing import List

def process(items: List[str]):
    return items
```

## Common Patterns

### Conditional Imports

Imports used only in certain conditions are still considered used:

```python
import optional_module

def process():
    if optional_module:
        return optional_module.do_something()
    return None
```

### Re-exports

Imports that are re-exported are considered used:

```python
# In __init__.py
from .module import SomeClass  # No warning if SomeClass is part of __all__

__all__ = ["SomeClass"]
```

### TYPE_CHECKING Imports

Imports inside `if TYPE_CHECKING:` blocks are handled specially:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from heavy_module import HeavyClass  # No warning - used for type hints only

def process(obj: HeavyClass) -> None:
    pass
```

## Suppressing the Diagnostic

### For Specific Imports

Use `# type: ignore` comment:

```python
import unused_module  # type: ignore
```

Or use `# noqa`:

```python
import unused_module  # noqa
```

### Configuration

In `pyrightconfig.json`:

```json
{
  "reportUnusedImport": "none"
}
```

> **Note**: Disabling this diagnostic globally is not recommended as it helps keep code clean.

## Auto-Fix

Most editors support auto-fixing unused imports:

1. **VS Code / Pylance**: Quick fix (Ctrl+.) → "Remove unused import"
2. **Pyright**: Similar quick fix support

### Fix All

You can configure automatic removal of unused imports on save:

```json
{
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Related Diagnostics

- [`reportUnusedVariable`](reportUnusedVariable.md) - Variable is assigned but never used
- [`reportUnusedFunction`](reportUnusedFunction.md) - Function is defined but never used
- [`reportUnusedClass`](reportUnusedClass.md) - Class is defined but never used
- [`reportUnusedExpression`](reportUnusedExpression.md) - Expression value is never used

## See Also

- [PEP 8 - Imports](https://pep8.org/#imports)
- [Python typing.TYPE_CHECKING](https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING)
- [Organize Imports in VS Code](https://code.visualstudio.com/docs/python/editing#_formatting)