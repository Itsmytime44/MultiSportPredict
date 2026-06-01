# How to Use Pylance in Remote Development Environments

A comprehensive guide to configuring Pylance across various remote development setups including Dev Containers, WSL, Remote SSH, and GitHub Codespaces.

## Overview

Pylance works seamlessly in remote development environments, but there are some configuration considerations to ensure optimal performance and functionality.

## Dev Containers

### Basic Configuration

Create a `devcontainer.json` in `.devcontainer/`:

```json
{
  "name": "Python Development Container",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.analysis.autoSearchPaths": true,
        "python.analysis.extraPaths": ["src"]
      }
    }
  },
  "postCreateCommand": "pip install -r requirements.txt"
}
```

### Configuration File Location

In Dev Containers, configuration files should be in the workspace root inside the container:

```
/workspace/project/
├── pyrightconfig.json      # Pylance/Pyright config
├── .devcontainer/
│   └── devcontainer.json   # Container config
└── src/
    └── main.py
```

### Multi-Stage Containers

For complex setups with multiple containers:

```json
{
  "name": "Multi-Container Dev Environment",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ],
      "settings": {
        "python.analysis.useNearestConfiguration": true
      }
    }
  }
}
```

## WSL (Windows Subsystem for Linux)

### Basic Setup

1. Install VS Code in Windows
2. Install WSL extension (`ms-vscode-remote.wsl`)
3. Open WSL terminal and navigate to project
4. Run `code .` to open in VS Code

### Configuration Location

Configuration files should be in the WSL filesystem:

```
\\wsl$\Ubuntu\home\user\project\
├── pyrightconfig.json
└── src/
    └── main.py
```

**Important**: Do NOT place configuration files in the Windows filesystem (`/mnt/c/`) when working in WSL, as this can cause performance issues.

### Python Interpreter

Ensure the correct WSL Python interpreter is selected:

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run: `Python: Select Interpreter`
3. Choose the WSL Python (e.g., `/usr/bin/python3`)

### Virtual Environments in WSL

Create virtual environments in WSL:

```bash
# In WSL terminal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Performance Tips

1. **Store files in WSL filesystem**: Avoid `/mnt/c/` for project files
2. **Use WSL-native tools**: Run pip, git, etc. in WSL terminal
3. **Exclude Windows paths**: Don't add `/mnt/c/` paths to extraPaths

## Remote SSH

### Basic Setup

1. Install Remote - SSH extension (`ms-vscode-remote.remote-ssh`)
2. Configure SSH connection in settings
3. Connect to remote machine
4. Open project folder

### Configuration Location

Configuration files should be on the remote machine:

```
/home/user/project/
├── pyrightconfig.json
└── src/
    └── main.py
```

### Python Interpreter

Select the remote Python interpreter:

1. Open Command Palette
2. Run: `Python: Select Interpreter`
3. Choose the remote Python (e.g., `/usr/bin/python3`)

### Virtual Environments

Create virtual environments on the remote machine:

```bash
# On remote machine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Performance Considerations

1. **Network latency**: Analysis may be slower over slow connections
2. **Large codebases**: Consider using workspace mode:
```json
{
  "python.analysis.languageServerMode": "workspace"
}
```

## GitHub Codespaces

### Basic Configuration

Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "Python Codespace",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.analysis.autoSearchPaths": true
      }
    }
  }
}
```

### Configuration Inheritance

Codespaces automatically uses the same configuration as Dev Containers, making it easy to maintain consistency.

### Prebuilding

For faster Codespace startup, enable prebuilds in your repository settings.

## Common Issues and Solutions

### Issue: Extensions Not Installed

**Symptom**: Pylance features not available in remote environment.

**Solution**:
1. Check `devcontainer.json` includes extensions
2. Rebuild container: `Dev Containers: Rebuild Container`
3. Verify extensions are installed in remote

### Issue: Wrong Python Interpreter

**Symptom**: Import errors, wrong Python version.

**Solution**:
1. Run `Python: Select Interpreter`
2. Choose the correct interpreter for the environment
3. Reload window if needed

### Issue: Configuration Not Applied

**Symptom**: Settings not taking effect.

**Solution**:
1. Check configuration file location (should be in workspace root)
2. Verify JSON syntax is valid
3. Restart language server: `Python: Restart Language Server`
4. Check `useNearestConfiguration` setting

### Issue: Slow Performance

**Symptom**: Analysis is slow, high latency.

**Solutions**:

1. **Use workspace mode**:
```json
{
  "python.analysis.languageServerMode": "workspace"
}
```

2. **Reduce indexing**:
```json
{
  "python.analysis.indexing": "off"
}
```

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

### Issue: File Sync Problems

**Symptom**: Files not syncing properly between local and remote.

**Solution**:
1. Check file permissions
2. Ensure proper line endings (LF for Linux, CRLF for Windows)
3. Use appropriate file sync settings

## Best Practices

### 1. Use Configuration Files

Always use `pyrightconfig.json` or `pyproject.toml` for project-specific settings:

```json
{
  "include": ["src/**/*.py"],
  "exclude": ["**/__pycache__/**", "**/.venv/**"],
  "typeCheckingMode": "basic"
}
```

### 2. Consistent Python Versions

Ensure Python version consistency across environments:

```json
{
  "python.analysis.pythonPlatform": "Linux"  // or "Windows", "Darwin"
}
```

### 3. Virtual Environment Management

Use consistent virtual environment naming:

```bash
# Standard naming
python -m venv .venv

# Or use virtualenvwrapper
mkvirtualenv myproject
```

### 4. Version Control

Add configuration files to version control:

```bash
git add pyrightconfig.json
git add .devcontainer/devcontainer.json
```

### 5. Documentation

Document environment setup in README:

```markdown
## Development Setup

### Local Development
1. Create virtual environment: `python -m venv .venv`
2. Activate: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`

### Remote Development
1. Open in Dev Container / WSL / Remote SSH
2. Extensions will install automatically
3. Follow local setup steps inside remote environment
```

## Environment-Specific Settings

### Using Environment-Specific Configs

Create environment-specific configuration files:

```
project/
├── pyrightconfig.json          # Default config
├── pyrightconfig.dev.json      # Development config
├── pyrightconfig.ci.json       # CI config
└── src/
```

Pylance will automatically use the appropriate config based on the environment.

### Conditional Settings

Use `useNearestConfiguration` to allow different configs in different parts of a monorepo:

```json
{
  "python.analysis.useNearestConfiguration": true
}
```

## See Also

- [Settings Troubleshooting](settings-troubleshooting.md)
- [useNearestConfiguration](../settings/python_analysis_useNearestConfiguration.md)
- [languageServerMode](../settings/python_analysis_languageServerMode.md)