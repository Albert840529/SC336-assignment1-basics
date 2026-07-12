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

## 2. Unicode Code Points

`chr()` is a Python built-in function that converts an integer Unicode code point into a one-character string:

```python
chr(65)  # 'A', U+0041
chr(48)  # '0', U+0030
chr(0)   # NUL, U+0000
```

NUL is an invisible control character, not the visible digit `"0"`. Python displays it as the hexadecimal escape `\x00`. `repr()` exposes this representation, while `print()` renders the invisible character itself.

Key idea: a character can exist in a string even when it has no visible glyph.

### Problem `unicode1`: Understanding Unicode (1 point)

**Deliverables**

1. `chr(0)` returns the Unicode NUL control character, `U+0000`.
2. `repr()` displays NUL using the visible escape sequence `'\x00'`, while `print()` renders the character itself, which has no visible glyph.
3. When NUL occurs in a Python string, it remains part of the string even though it is invisible, and UTF-8 encodes it as the byte `0x00`.

### Useful ASCII ranges

- `0-31`: mostly invisible ASCII control characters
  - `7`: bell
  - `8`: backspace
  - `9`: tab
  - `10`: newline
  - `13`: carriage return
- `32`: space
- `33-47`: punctuation such as `! " # $ % & ' ( ) * + , - . /`
- `48-57`: digits `0-9`
- `65-90`: uppercase letters `A-Z`
- `97-122`: lowercase letters `a-z`

Unicode preserves ASCII in its first 128 code points. The exact values do not need to be memorized; use `ord()` and `chr()` to convert in either direction:

```python
ord("A")  # 65
chr(65)   # 'A'
```

## 3. Unicode Encodings and UTF-8

Unicode assigns each character a code point. An encoding such as UTF-8 turns that code point into bytes.

Example:

```python
ord("A")                  # 65, U+0041
"A".encode("utf-8")       # b"A"
list("A".encode("utf-8")) # [65]

ord("你")                  # 20320, U+4F60
"你".encode("utf-8")       # b"\xe4\xbd\xa0"
list("你".encode("utf-8")) # [228, 189, 160]
```

Key distinction:

- Unicode is the character-to-code-point system.
- UTF-8 is a code-point-to-bytes encoding.
- A byte is an 8-bit value from `0` to `255`.

### UTF-8 byte patterns

UTF-8 uses the leading bits of each byte to show whether the byte is a complete one-byte character, the start of a multi-byte character, or a continuation byte.

- `0xxxxxxx`: one-byte ASCII character
- `110xxxxx 10xxxxxx`: two-byte character
- `1110xxxx 10xxxxxx 10xxxxxx`: three-byte character
- `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx`: four-byte character
- `10xxxxxx`: continuation byte, not valid by itself at the start of a character

For example, `"你"` is `U+4F60`, whose bits fit the three-byte UTF-8 pattern:

```text
U+4F60 -> 0100111101100000
       -> 11100100 10111101 10100000
       -> [228, 189, 160]
```

### Problem `unicode2`: Unicode Encodings (3 points)

**Deliverables**

1. UTF-8 is usually preferred over UTF-16 or UTF-32 for byte-level tokenization because it is space-efficient for common text, especially ASCII-heavy text, and it gives a fixed base vocabulary of 256 byte values that can represent any Unicode string.
2. The byte-by-byte decoder is incorrect because many UTF-8 characters require multiple bytes. For example, `"你".encode("utf-8")` is `b"\xe4\xbd\xa0"`, and decoding only `b"\xe4"` is invalid because it is an incomplete three-byte sequence.
3. `b"\xff\xff"` is an invalid UTF-8 byte sequence because `0xff` has the bit pattern `11111111`, which is not a legal UTF-8 start byte.
