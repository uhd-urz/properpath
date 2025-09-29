# ProperPath

<a href="https://pypi.org/project/properpath"><img alt="Package version" src="https://badge.fury.io/py/properpath.svg/?branch=main" /></a>
<img alt="Static Badge" src="https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-%230d7dbe"> <a href="https://github.com/uhd-urz/properpath/actions">
<img alt="GitHub Action test workflow" src="https://github.com/uhd-urz/properpath/actions/workflows/test.yml/badge.svg"></a>
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An opinionated OS-path module for people who take paths too seriously. `ProperPath`, as a subclass of Python's popular [
`pathlib.Path`](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path), is a drop-in replacement with some
extra features. The added features/APIs are mainly aimed at improving developer experience in building CLI
tools/applications. `ProperPath` was originally created for [elAPI](https://github.com/uhd-urz/elAPI).

<img height="312" width="670" src="https://heibox.uni-heidelberg.de/f/5f8e95d5a5954d3a88c8/?dl=1" alt="properpath on the road" />

## Main Features in a Nutshell

1. A drop-in `pathlib.Path` replacement with more descriptive REPL representation
2. Built-in error logging for raised exceptions
3. Simplified APIs for working with files and directories
4. Better [`platformfirs`](https://github.com/tox-dev/platformdirs) integration
5. Validation for file/directory write permission

## Installation

Make sure your Python virtual environment is activated. `properpath` requires Python 3.12 and above. Install
`properpath` with `pip`.

```shell
pip install properpath
```

You can install with `uv` as well.

```shell
uv add properpath
```

## Quickstart

Open a Python REPL and try the following:

```pycon
>>> from properpath import P # "P" is a shorthand for "ProperPath"

>>> P("~")
ProperPath(path=/Users/username, actual=('~',), kind=dir, exists=True, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
```

If you already have a script or a project where you've used `from pathlib import Path`, and if you're feeling
adventurous (!), you can try the following:

```python
from properpath import P as Path
```

## Usage

> [!TIP]
> In the examples below, we will use the shorthand `P`: `from properpath import P`, instead of
`from properpath import ProperPath`, where `P == ProperPath`.
> That is because `P` is much shorter and easier to type, and makes working with paths on the REPL
> more enjoyable.

### Drop-in `pathlib.Path` replacement

Since `ProperPath` is a subclass of `pathlib.Path` it
supports [all the methods and attributes](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path) supported by
`pathlib.Path`. We can pass a `pathlib.Path` instance or a string path or multiple path segments or `os.path` values to
`ProperPath`.

```pycon

>>> from properpath import P
>>> p = P("~/foo")
>>> p
ProperPath(path=/Users/username/foo, actual=('~/foo',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> isinstance(p, pathlib.Path)
True
>>> P.home()  # pathlib.Path's method
ProperPath(path=/Users/username, actual=('/Users/username',), kind=dir, exists=True, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
```

`ProperPath` shows more information about the path on the REPL (or a [
`repr` call](https://docs.python.org/3/library/functions.html#repr) from inside a script). Notice, how `ProperPath`
**always expands the username** (`~`) segment by default.
A `ProperPath` instance can also be passed to `pathlib.Path` or `os.path` methods.

### Is a `file` or a `dir`?

A `ProperPath` instance stores whether the path is a file or a directory in the `kind` attribute. If the path doesn't
exist beforehand, `PropePath` will try to assume it from the path's extension.
`ProperPath` also knows how to handle special files like `/dev/null`.

```pycon
>>> p = P("~/foo.txt")
>>> p.exists()
False
>>> p.kind  # Kind is determined from the file extension.
'file'
>>> p = P("~/foo")
>>> p.exists()
True
>>> p.kind
'dir'
```

In this code block though we could just use `is_dir()`. The real power of `kind` comes when we're working with
files/directories that aren't strictly created or handled by us, but we know what `kind` we are expecting. When `kind`
attribute is modified by the developer,
the `kind` is treated as the developer-expected `kind`. When `kind` is not modified, `ProperPath` determines the
appropriate `kind`.
We can modify `kind` by passing it as an argument to the
constructor during the path instance creation, or later on by simply updating the value of the attribute
`p.kind = "<file or dir>"`.
Pure `ProperPath` operations will expect that `kind` for all
future operations. This can help catch unexpected errors or even prevent unexpected file operation.
An example: Let's consider a situation where we expect a
**file** named `foo` to exist in user's `~/Downloads` folder. But for whatever reason, a directory with the exact the
same name already exists in `~/Downloads`. If we want to create the file with
`pathlib.Path("~/Downloads/foo").expanduser().touch(exist_ok=True)`, the method will succeed, and we will have assumed a
_file_ was indeed created! `ProperPath`'s `create` method will use `kind` to find out the mismatch in expectation, and
throw an error.

```pycon
>>> q = P("~/Downloads", "foo", kind="file")
ProperPath(path=/Users/username/Downloads/foo, actual=('/Users/username/Downloads/foo',), kind=file, exists=True, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> q.create()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/username/Workshop/properpath/src/properpath/properpath.py", line 441, in create
    raise e
  File "/Users/username/Workshop/properpath/src/properpath/properpath.py", line 421, in create
    raise is_a_dir_exception(message)
IsADirectoryError: File was expected but a directory with the same name was found: PATH=/Users/username/Downloads from SOURCE=('~/Downloads', 'foo').
```

> [!TIP]
> In short, when we don't modify the `kind` attribute, `kind` simply gives the path's [
`is_file()`](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.is_file) or [
`is_dir()`](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.is_dir) status. When
> we do modify the attribute, our modified `kind` is cached, and is treated as the _expected `kind`_ for all future
> operations. When this expected `kind` doesn't match the actual `kind` of the path in the system for whatever reason,
`ProperPath` will attempt to throw an error before irrecoverable operations like deleting files.

### Built-in error logging

A custom logger can be passed to `ProperPath` instance. This logger will be used throughout path operations for that
path instance. If no
logger is passed, `ProperPath` will use `ProperPath.default_err_logger` class attribute (which by default is the Python
root logger).

```pycon
>>> import logging
>>> logging.basicConfig(level=logging.DEBUG)
>>> p = P("/var/log/my_app.log")
>>> with p.open("w") as f:
...     f.write("Hello, world!")
...
DEBUG:root:Could not open file PATH=/private/var/log/my_app.log from SOURCE=('/var/log/my_app.log',). 
Exception: PermissionError(13, 'Permission denied')
Traceback (most recent call last):
  File "<python-input-4>", line 1, in <module>
    with p.open("w") as f:
         ~~~~~~^^^^^
# Any exception raised during path operations will be logged to the new_logger, 
# before being raised.
```

> [!NOTE]
> All log messages are logged as `DEBUG` messages. So the default logging level or handler level should be set
> to `DEBUG`. This is so that path logs don't overwhelm the regular users, and the `DEBUG` level is only set for
> debugging/development. We can also pass our own custom logger to
`P("/var/log/my_app.log", err_logger=logging.getLogger("my_logger"))`, or modify the `err_logger` attribute at
> runtime. Each logger is tied to the instance it was passed to. If we want to have a single logger to be shared with
> all instances of `ProperPath`, we just set the class attribute
`P.default_err_logger = logging.getLogger("my_logger")`.

### `create` and `remove` paths

To create a new file or directory, `pathlib.Path` would require a boilerplate `if path.is_file():` or
`if path.is_dir():` block if the path is unknown. `ProperPath` provides the `create` method that simplifies this step.
Just call `create` on any path to create it. If the path already exists, nothing happens.

```python
P("/etc/my_app/config.toml").create()
```

Similarly, the `remove` removes the need to boilerplate check for if the path is a file or a directory, or if it is
empty
or not. If the path is a directory, everything inside it will be removed recursively by default. `remove` method accepts
a `parent_only` argument, which if `True`, will only remove the top-level contents only (i.e., will remove only the
files,
will not do a recursion into other directories).

```text
.local/
├─ share/
│  ├─ my_app/
│  │  ├─ custom/
│  │  │  ├─ plugins/
│  │  ├─ config.toml
```

```python
P("~/.local/share/my_app/").remove(parent_only=True)
```

The code above will only `~/.local/share/my_app/config.toml`, and leave `custom/` and `plugins/` directories as is. If
`parents_only=False` is passed (the default), everything inside `my_app` directory will be deleted recursively. Under
the hood both `create` and `remove` methods take advantage of the `kind` attribute.

### Better Platformdirs

`ProperPath` comes integrated with a popular library used for managing common application
paths: [platformdirs](https://github.com/tox-dev/platformdirs). E.g., to get OS-standard locations for configuration
files, logs, caches, etc. See
platformdirs [documentation](https://github.com/tox-dev/platformdirs?tab=readme-ov-file#platformdirs-for-convenience)
for more details and examples for **other operating systems**. Values from `platformdirs` by default are strings. But
with `ProperPath.platformdirs`, you can get
`ProperPath` instances instead.

```pycon
>>> from properpath import P
>>> app_dirs = P.platformdirs("my_app", "my_org")
>>> app_dirs.user_config_dir
ProperPath(path=/Users/username/Library/Application Support/my_app, actual=('/Users/username/Library/Application Support/my_app',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_data_dir
ProperPath(path=/Users/username/Library/Application Support/my_app, actual=('/Users/username/Library/Application Support/my_app',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_cache_dir
ProperPath(path=/Users/username/Library/Caches/my_app, actual=('/Users/username/Library/Caches/my_app',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_data_dir
ProperPath(path=/Library/Application Support/my_app, actual=('/Library/Application Support/my_app',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_config_dir
ProperPath(path=/Library/Application Support/my_app, actual=('/Library/Application Support/my_app',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_documents_dir
ProperPath(path=/Users/username/Documents, actual=('/Users/username/Documents',), kind=dir, exists=True, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_downloads_dir
ProperPath(path=/Users/username/Downloads, actual=('/Users/username/Downloads',), kind=dir, exists=True, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>>  # Etc. See whole list: https://github.com/tox-dev/platformdirs?tab=readme-ov-file#platformdirs-for-convenience
```

Platformdirs enforces a strict directory structure for macOS, but many tools out there follow the Unix-style directory
structures on macOS as well. `ProperPath` provides an additional `follow_unix` argument to `ProperPath.platformdirs`
that will enforce Unix-style directory structure on macOS, but will leave Windows as is.

```pycon
>>> app_dirs = P.platformdirs("my_app", "my_org", follow_unix=True)
>>> app_dirs.user_config_dir
ProperPath(path=/Users/username/.config/my_app, actual=('/Users/username/.config/my_app',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_data_dir
ProperPath(path=/Users/username/.local/share/my_app, actual=('/Users/username/.local/share/my_app',), kind=dir, is_symlink=False, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_cache_dir
ProperPath(path=/Users/username/.cache/my_app, actual=('/Users/username/.cache/my_app',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_data_dir
ProperPath(path=/usr/local/share/my_app, actual=('/usr/local/share/my_app',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_config_dir
ProperPath(path=/etc/xdg/my_app, actual=('/etc/xdg/my_app',), kind=dir, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_documents_dir
ProperPath(path=/Users/username/Documents, actual=('/Users/username/Documents',), kind=dir, exists=True, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_downloads_dir
ProperPath(path=/Users/username/Downloads, actual=('/Users/username/Downloads',), kind=dir, exists=True, is_symlink=False, err_logger=<RootLogger root (WARNING)>)
```

### Path validation

We often write to files, so we need to make sure if the file we're writing to is even _writable_; i.e., if the file
exists, if there is enough storage space, if there is sufficient permission, etc. `ProperPath` comes with a
`PathWriteValidator` class that can be used to do exactly that. Example: we want to write to a file from a list of
fallback files, and we want to write to the first one that works.

```python
from properpath.validators import PathValidationError, PathWriteValidator

user_desired_paths = ["/usr/usb/Downloads/", "~/Downloads"]
# PathWriteValidator will convert the strings to ProperPath instances during validation.
try:
    validated_path = PathWriteValidator(user_desired_paths).validate()
except PathValidationError as e:
    # PathValidationError is raised when all paths fail validation.
    raise e("None of the paths are writable.")
else:
    validated_path.write_text("Hooray!")
```

Of course, a single path can also be passed to `PathWriteValidator`.

`ProperPath` comes with a `PathException` attribute that stores any exception raised during any path operation. In other
words, an error raised for a path is tied to that path only. We can use this `PathException` to implement a fallback
mechanism. I.e., if we want to just forget about the error from one path, and move onto the next path. From one of our
previous examples:

```python
p = P("~/Downloads/metadata.txt")

try:
    with p.open("w") as f:
        f.write("Hello, world!")
except p.PathException as e:
    # try a different path
    p.err_logger.warning(f"Failed to write to {p}. Exception: {e!r}")
    p.err_logger.info("Trying another path...")
    P("~/metadata.txt").write_text("Hello, world!")
```

In some ways, `PathException` treats errors as values.

## Why is the Python compatibility 3.12 and above?

Before Python 3.12, subclassing `pathlib.Path` was tricky and riddled with odd bugs even when done so carefully. In
fact, composition, and not inheritance, was the best option to extend `pathlib.Path` until Python 3.12.
Python 3.12 addressed this issue
and [fixed subclassing](https://docs.python.org/3/whatsnew/3.12.html#summary-release-highlights) for `pathlib.Path`.

## Credits

The banner art was taken from
this [stock photo](https://www.pexels.com/photo/aerial-view-of-road-in-the-middle-of-trees-1173777/), and was
transformed into a pixel art with AI.
