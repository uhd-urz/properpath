# Tutorial

## Drop-in `pathlib.Path` replacement

Since `ProperPath` is a subclass of `pathlib.Path` it
supports [all the methods and attributes](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path) supported by
`pathlib.Path`. We can pass a `pathlib.Path` instance or a string path or multiple path segments or `os.path` values to
`ProperPath`.

```{ .python .no-copy title="Python REPL" }

>>> from properpath import ProperPath
>>> p = ProperPath("~/foo")
>>> p
ProperPath(path=/Users/username/foo, actual=~/foo, kind=dir, err_logger=<RootLogger
root(WARNING)>)
>>> isinstance(p, pathlib.Path)
True
>>> ProperPath.home()  # pathlib.Path's method
ProperPath(path=/Users/username, actual=('/Users/username',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
```

`ProperPath` shows more information about the path on the REPL (or a [
`repr` call](https://docs.python.org/3/library/functions.html#repr) from inside a script). A `ProperPath` instance can
also be passed to `pathlib.Path` or `os.path` methods.

```{ .python .no-copy title="Python REPL" }
>>> from pathlib import Path

>>> Path(ProperPath("~"))
PosixPath('/Users/username')
```

## Is a `file` or a `dir`?

A `ProperPath` instance will determine if the path is a file or a directory during instance creation, and store it in
`kind` attribute. If the path doesn't exist beforehand, `PropePath` will try to assume it from the path's extension.
`ProperPath` also knows how to handle special files like `/dev/null`.

```{ .python .no-copy title="Python REPL" }
>>> p = ProperPath("~/foo.txt")
>>> p.exists()
False
>>> p.kind  # Kind is determined from the file extension.
'file'
>>> p = ProperPath("~/foo")
>>> p.exists()
True
>>> p.kind
'dir'
```

## Built-in error logging

A custom logger can be passed to `ProperPath` instance. This logger will be used throughout path operations for that path instance. If no
logger is passed, `ProperPath` will use `ProperPath.default_err_logger` class attribute (which by default is the Python root logger).

```{ .python .no-copy title="Python REPL" hl_lines="7 8"}
>>> import logging
>>> logging.basicConfig(level=logging.DEBUG)
>>> p = ProperPath("/var/log/my_app.log")
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

**Note:** All log messages are logged as `DEBUG` messages. So the default logging level or handler level should be set
to `DEBUG`. This is so that path logs don't overwhelm the regular users, and the `DEBUG` level is only set for
debugging/development. We can also pass our own custom logger to
`ProperPath("/var/log/my_app.log", err_logger=logging.getLogger("my_logger"))`, or modify the `err_logger` attribute at
runtime. Each logger is tied to the instance it was passed to. If we want to have a single logger to be shared with all
instances of `ProperPath`, we just set the class attribute
`ProperPath.default_err_logger = logging.getLogger("my_logger")`.

## `create` and `remove` paths

To create a new file or directory, `pathlib.Path` would require a boilerplate `if path.is_file():` or
`if path.is_dir():` block if the path is unknown. `ProperPath` provides the `create` method that simplifies this step.
Just call `create` on any path to create it. If the path already exists, nothing happens.

```python
ProperPath("/etc/my_app/config.toml").create()
```

Similarly, the `remove` removes the need to boilerplate check for if the path is a file or a directory, or if it is empty
or not. If the path is a directory, everything inside it will be removed recursively by default. `remove` method accepts
a `parent_only` argument, which if `True`, will only remove the top-level contents only (i.e., will remove only the files,
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
ProperPath("~/.local/share/my_app/").remove(parent_only=True)
```

The code above will only `~/.local/share/my_app/config.toml`, and leave `custom/` and `plugins/` directories as is. If
`parents_only=False` is passed (the default), everything inside `my_app` directory will be deleted recursively. Under
the hood both `create` and `remove` methods take advantage of the `kind` attribute.

## Better Platformdirs

`ProperPath` comes integrated with a popular library used for managing common application
paths: [platformdirs](https://github.com/tox-dev/platformdirs). E.g., to get OS-standard locations for configuration
files, logs, caches, etc. See
platformdirs [documentation](https://github.com/tox-dev/platformdirs?tab=readme-ov-file#platformdirs-for-convenience)
for more details and examples for **other operating systems**. Values from `platformdirs` by default are strings. But with `ProperPath.platformdirs`, you can get
`ProperPath` instances instead.

```{ .python .no-copy title="Python REPL" }
>>> from properpath import ProperPath
>>> app_dirs = ProperPath.platformdirs("my_app", "my_org")
>>> app_dirs.user_config_dir
ProperPath(path=/Users/username/Library/Application Support/my_app, actual=('/Users/username/Library/Application Support/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_data_dir
ProperPath(path=/Users/username/Library/Application Support/my_app, actual=('/Users/username/Library/Application Support/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_cache_dir
ProperPath(path=/Users/username/Library/Caches/my_app, actual=('/Users/username/Library/Caches/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_data_dir
ProperPath(path=/Library/Application Support/my_app, actual=('/Library/Application Support/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_config_dir
ProperPath(path=/Library/Application Support/my_app, actual=('/Library/Application Support/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_documents_dir
ProperPath(path=/Users/username/Documents, actual=('/Users/username/Documents',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_downloads_dir
ProperPath(path=/Users/username/Downloads, actual=('/Users/username/Downloads',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
>>>  # Etc. See whole list: https://github.com/tox-dev/platformdirs?tab=readme-ov-file#platformdirs-for-convenience
```

Platformdirs enforces a strict directory structure for macOS, but many tools out there follow the Unix-style directory
structures on macOS as well. `ProperPath` provides an additional `follow_unix` argument to `ProperPath.platformdirs`
that will enforce Unix-style directory structure on macOS, but will leave Windows as is.

```{ .python .no-copy title="Python REPL" }
>>> app_dirs = ProperPath.platformdirs("my_app", "my_org", follow_unix=True)
>>> app_dirs.user_config_dir
ProperPath(path=/Users/username/.config/my_app, actual=('/Users/username/.config/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_data_dir
ProperPath(path=/Users/username/.local/share/my_app, actual=('/Users/username/.local/share/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_cache_dir
ProperPath(path=/Users/username/.cache/my_app, actual=('/Users/username/.cache/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_data_dir
ProperPath(path=/usr/local/share/my_app, actual=('/usr/local/share/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_config_dir
ProperPath(path=/etc/xdg/my_app, actual=('/etc/xdg/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_documents_dir
ProperPath(path=/Users/username/Documents, actual=('/Users/username/Documents',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_downloads_dir
ProperPath(path=/Users/username/Downloads, actual=('/Users/username/Downloads',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
```

## Path validation

We often write to files, so we need to make sure if the file we're writing to is even _writable_; i.e., if the file
exists, if there is enough storage space, if there is sufficient permission, etc. `ProperPath` comes with a
`PathWriteValidator` class that can be used to do exactly that. Example: we want to write to a file from a list of
fallback files, and we want to write to the first one that works.

```python title="validate.py"
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

```python title="try_path_exception.py"

p = ProperPath("~/Downloads/metadata.txt")

try:
    with p.open("w") as f:
        f.write("Hello, world!")
except p.PathException as e:
    # try a different path
    p.err_logger.warning(f"Failed to write to {p}. Exception: {e!r}")
    p.err_logger.info("Trying another path...")
    ProperPath("~/metadata.txt").write_text("Hello, world!")
```

In some ways, `PathException` treats errors as values.
