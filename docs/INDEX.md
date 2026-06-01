# Pylance Documentation Index

Welcome to the comprehensive Pylance documentation. This guide covers settings, configuration, troubleshooting, and diagnostics for Pylance and Pyright.

## Settings Documentation

Configuration options for Pylance/Pyright analysis.

### Core Settings

| Setting | Description |
|---------|-------------|
| [`python.analysis.autoSearchPaths`](settings/python_analysis_autoSearchPaths.md) | Automatically add common search paths for imports |
| [`python.analysis.enablePytestSupport`](settings/python_analysis_enablePytestSupport.md) | Enable enhanced pytest fixture and marker support |
| [`python.analysis.includeExtraPathSymbolsInSymbolSearch`](settings/python_analysis_includeExtraPathSymbolsInSymbolSearch.md) | Include symbols from extra paths in workspace symbol search |
| [`python.analysis.includeVenvInWorkspaceSymbols`](settings/python_analysis_includeVenvInWorkspaceSymbols.md) | Include symbols from the active virtual environment's site-packages |
| [`python.analysis.useNearestConfiguration`](settings/python_analysis_useNearestConfiguration.md) | Automatically discover configuration files for virtual workspaces |
| [`python.analysis.nodeExecutable`](settings/python_analysis_nodeExecutable.md) | Manually specify the Node.js executable path |
| [`python.analysis.nodeArguments`](settings/python_analysis_nodeArguments.md) | Pass arguments to the Node.js process (e.g., heap limits) |

### File Inclusion/Exclusion

| Setting | Description |
|---------|-------------|
| [`python.analysis.include`](settings/python_analysis_include.md) | Include specific files/folders for analysis |
| [`python.analysis.exclude`](settings/python_analysis_ignore.md) | Exclude files/folders from analysis |
| [`python.analysis.ignore`](settings/python_analysis_ignore.md) | Ignore files (diagnostics suppressed but imports resolved) |

### Type Checking

| Setting | Description |
|---------|-------------|
| [`python.analysis.typeCheckingMode`](settings/python_analysis_typeCheckingMode.md) | Control the strictness of type checking |
| [`python.analysis.useLibraryCodeForTypes`](settings/python_analysis_useLibraryCodeForTypes.md) | Use library code to determine types when stubs unavailable |

### Indexing and Performance

| Setting | Description |
|---------|-------------|
| [`python.analysis.indexing`](settings/python_analysis_indexing.md) | Enable/disable library indexing |
| [`python.analysis.packageIndexDepths`](settings/python_analysis_packageIndexDepths.md) | Control indexing depth per package |
| [`python.analysis.persistAllIndices`](settings/python_analysis_persistAllIndices.md) | Persist all indices to disk for faster startup |
| [`python.analysis.userFileIndexingLimit`](settings/python_analysis_userFileIndexingLimit.md) | Limit on files to index in user code |
| [`python.analysis.languageServerMode`](settings/python_analysis_languageServerMode.md) | Optimize for document, workspace, or IDE mode |

### Paths and Stubs

| Setting | Description |
|---------|-------------|
| [`python.analysis.stubPath`](settings/python_analysis_stubPath.md) | Custom path for type stub files |
| [`python.analysis.typeshedPaths`](settings/python_analysis_typeshedPaths.md) | Additional paths for typeshed stubs |
| [`python.analysis.includeAliasesFromUserFiles`](settings/python_analysis_includeAliasesFromUserFiles.md) | Include type aliases from user files in analysis |

### Import Settings

| Setting | Description |
|---------|-------------|
| [`python.analysis.importFormat`](settings/python_analysis_importFormat.md) | Control import style (relative vs absolute) |

## How-To Guides

Practical guides for common tasks and troubleshooting.

| Guide | Description |
|-------|-------------|
| [Remote Development](howto/remote-development.md) | Configure Pylance in Dev Containers, WSL, Remote SSH, and GitHub Codespaces |
| [Settings Troubleshooting](howto/settings-troubleshooting.md) | Resolve configuration conflicts and precedence issues |
| [Fix Unresolved Imports](howto/fix-unresolved-imports.md) | Diagnose and fix import resolution errors |
| [Type Narrowing](howto/type-narrowing.md) | Master type narrowing techniques with isinstance, TypeGuard, and discriminated unions |

## Diagnostics Reference

Detailed documentation for each diagnostic warning/error.

### Type-Related Diagnostics

| Diagnostic | Description |
|------------|-------------|
| [`reportUnknownVariableType`](diagnostics/reportUnknownVariableType.md) | Variable type cannot be inferred |
| [`reportUnknownParameterType`](diagnostics/reportUnknownParameterType.md) | Parameter type is unknown |
| [`reportUnknownArgumentType`](diagnostics/reportUnknownArgumentType.md) | Argument type cannot be determined |
| [`reportUnknownMemberType`](diagnostics/reportUnknownMemberType.md) | Member type is unknown |
| [`reportUnknownLambdaType`](diagnostics/reportUnknownLambdaType.md) | Lambda expression type is unknown |

### Optional/None Handling

| Diagnostic | Description |
|------------|-------------|
| [`reportOptionalSubscript`](diagnostics/reportOptionalSubscript.md) | Possibly None value used with subscript |
| [`reportOptionalMemberAccess`](diagnostics/reportOptionalMemberAccess.md) | Possibly None value member access |
| [`reportOptionalCall`](diagnostics/reportOptionalCall.md) | Possibly None value called as function |
| [`reportOptionalIterable`](diagnostics/reportOptionalIterable.md) | Possibly None value used in iteration |
| [`reportOptionalContextManager`](diagnostics/reportOptionalContextManager.md) | Possibly None value used as context manager |
| [`reportOptionalOperand`](diagnostics/reportOptionalOperand.md) | Possibly None value used with operator |

### Unused Code

| Diagnostic | Description |
|------------|-------------|
| [`reportUnusedVariable`](diagnostics/reportUnusedVariable.md) | Variable is assigned but never used |
| [`reportUnusedFunction`](diagnostics/reportUnusedFunction.md) | Function is defined but never used |
| [`reportUnusedClass`](diagnostics/reportUnusedClass.md) | Class is defined but never used |
| [`reportUnusedImport`](diagnostics/reportUnusedImport.md) | Import is never used |
| [`reportUnusedExpression`](diagnostics/reportUnusedExpression.md) | Expression value is never used |
| [`reportUnusedCallResult`](diagnostics/reportUnusedCallResult.md) | Function return value is never used |
| [`reportUnusedCoroutine`](diagnostics/reportUnusedCoroutine.md) | Coroutine is not awaited |

### Type Safety

| Diagnostic | Description |
|------------|-------------|
| [`reportUnnecessaryCast`](diagnostics/reportUnnecessaryCast.md) | Cast is unnecessary or always fails |
| [`reportUnnecessaryComparison`](diagnostics/reportUnnecessaryComparison.md) | Comparison is always True or False |
| [`reportUnnecessaryContains`](diagnostics/reportUnnecessaryContains.md) | Contains check is always True or False |
| [`reportUnnecessaryIsInstance`](diagnostics/reportUnnecessaryIsInstance.md) | isinstance check is always True or False |
| [`reportUnnecessaryTypeIgnoreComment`](diagnostics/reportUnnecessaryTypeIgnoreComment.md) | Type ignore comment is unnecessary |

### Untyped Code

| Diagnostic | Description |
|------------|-------------|
| [`reportUntypedBaseClass`](diagnostics/reportUntypedBaseClass.md) | Base class has no type information |
| [`reportUntypedClassDecorator`](diagnostics/reportUntypedClassDecorator.md) | Class decorator lacks type information |
| [`reportUntypedFunctionDecorator`](diagnostics/reportUntypedFunctionDecorator.md) | Function decorator lacks type information |
| [`reportUntypedNamedTuple`](diagnostics/reportUntypedNamedTuple.md) | NamedTuple has no type information |

### Other Diagnostics

| Diagnostic | Description |
|------------|-------------|
| [`reportUndefinedVariable`](diagnostics/reportUndefinedVariable.md) | Variable is not defined |
| [`reportUnhashable`](diagnostics/reportUnhashable.md) | Value is used in context requiring hashable type |
| [`reportUninitializedInstanceVariable`](diagnostics/reportUninitializedInstanceVariable.md) | Instance variable not initialized in __init__ |
| [`reportUnsupportedDunderAll`](diagnostics/reportUnsupportedDunderAll.md) | __all__ has unsupported form |
| [`reportUntypedClassDecorator`](diagnostics/reportUntypedClassDecorator.md) | Class decorator lacks type information |

## Quick Links

- [Settings Troubleshooting Guide](howto/settings-troubleshooting.md) - Resolve configuration issues
- [Fix Unresolved Imports](howto/fix-unresolved-imports.md) - Common import errors
- [Type Narrowing Guide](howto/type-narrowing.md) - Master type narrowing
- [Remote Development Setup](howto/remote-development.md) - WSL, Dev Containers, SSH

## External Resources

- [Pylance Official Documentation](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [Pyright Documentation](https://microsoft.github.io/pyright/)
- [Python Type Spec](https://typing.python.org/)