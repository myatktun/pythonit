# About

Just learning python by solving my own real world problems.

## Pyenv and Python LSP Server

For pylsp to work with pyenv virtual environment, just set local pyenv version to both virtual
environment version and global version, by editing `.python-version` file or

```
pyenv local <venv_version> <global_version>
```

Need to specify <venv_version> first, otherwise pyenv will default to global_version and
require to activate virtual environment manually.
