# CS336 Assignment 1 Learning Notes

This document records the concepts, commands, code patterns, and debugging lessons learned while completing Stanford CS336 Assignment 1. It is intended to be both a study reference and a clear account of the reasoning developed throughout the assignment.

## 1. Python Environments and `uv`

### Why projects use isolated environments

A computer can have several Python installations at the same time. Each installation can use a different Python version and a different set of packages. An isolated project environment prevents one project's dependencies from changing or breaking another project's dependencies.

On this machine, the following Python environments are available:

- The system-level `python3` command currently runs Python 3.14.
- The Anaconda `base` environment runs Python 3.10.
- The CS336 project environment runs Python 3.13 from `.venv`.

The CS336 environment should be used for this assignment because its Python and package versions satisfy the requirements in `pyproject.toml` and `uv.lock`.

### The environment files

- `pyproject.toml` is the human-readable project configuration. It declares the supported Python versions and direct dependencies.
- `uv.lock` records exact resolved dependency versions so the environment can be reproduced.
- `.venv/` is the local environment created by `uv sync`. It contains the project-specific Python executable and installed packages.

The course repository provides the environment specification. The `.venv` directory is generated locally and should not be edited manually.

### Creating or synchronizing the project environment

Run the following command from the directory containing `pyproject.toml`:

```sh
uv sync
```

Running it from the parent directory fails because `uv` cannot find the project configuration.

### Running one command in the project environment

The preferred approach is to prefix a command with `uv run`:

```sh
uv run python
uv run python --version
uv run pytest
```

`uv run` uses the project environment only for that command. It does not permanently change the current shell.

When `uv run python` opens the Python interactive interpreter, the prompt changes to `>>>`. Exit the interpreter with:

```python
exit()
```

### Activating the project environment for the current shell

The environment can also be activated explicitly:

```sh
source .venv/bin/activate
```

After activation, the shell prompt includes `(cs336-basics)`, and commands such as `python` and `pytest` use the project environment directly:

```sh
python --version
pytest
```

Leave the activated environment with:

```sh
deactivate
```

The distinction is important:

- `exit()` leaves the Python interactive interpreter.
- `deactivate` leaves an environment that was activated in the current shell.

### Using Anaconda

Anaconda is a separate Python distribution and environment manager. Its default environment is named `base`.

Activate it with:

```sh
conda activate base
```

Leave it with:

```sh
conda deactivate
```

When `base` is active on this machine, both `python` and `python3` resolve to Anaconda's Python 3.10. When it is inactive, `python3` resolves to the separately installed Python 3.14, while `python` may not exist.

### Checking which Python is active

Use version and path checks together:

```sh
python --version
which python
python3 --version
which python3
uv run python --version
uv run which python
```

The version reports what interpreter is running. The path explains where that interpreter comes from.

### Recommended workflow for this assignment

Remain in the `SC336-Assignment1` directory and run assignment commands through `uv`:

```sh
uv run python
uv run pytest
```

This is clearer than relying on whichever global or Conda environment happens to be active. The same commands work in both the macOS Terminal and the integrated VS Code Terminal because both are local shell sessions.

### Common mistakes

- Running `uv sync` outside the directory containing `pyproject.toml`.
- Assuming `python`, `python3`, and `uv run python` always refer to the same interpreter.
- Confusing the Python `>>>` prompt with the shell prompt.
- Using `deactivate` to leave the Python interpreter instead of using `exit()`.
- Manually editing `.venv` instead of changing project configuration and rebuilding the environment.
