import logging
import string
from pathlib import Path
from random import choices
from types import NoneType
from typing import Iterable, Optional, Self, Union

from ..properpath import ProperPath
from .base import ValidationError, Validator


class PathValidationError(ValidationError):
    """
    Represents a specialized exception raised for path validation errors.

    PathValidationError is raised when a path validator (Validator subclass) fails to validate
    a given path(s). Unlike in `OSError`, the errno is defined as an instance attribute rather
    than a class attribute. This is to indicate that each path validation is tied to that path only.

    Attributes:
        errno (Optional[int]): The erOSError number associated with the path validation error.
    """

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.errno: Optional[int] = None
        # Unlike OSError, errno here is an instance attribute
        # instead of being a class attribute.
        # This will ensure broad use of errno with PathValidationError in the future.

    def __call__(self, *args) -> Self:
        super().__init__(*args)
        return self


class PathWriteValidator(Validator):
    """
    Performs validation for given paths to ensure they are writable.

    PathWriteValidator constructor accepts a single path instance or an iterable of path instances.
    If the given path is a file (`kind == "file"`), PathWriteValidator will create the file
    (if it doesn't already exist), then write a control character to the file and delete the character immediately after.
    If all this passes without errors, the file is considered to be successfully validated and is returned.
    If a directory is given, a temporary file is created inside the directory to validate write
    permissions. If an iterable of paths is given, the first path that passes validation is returned.

    Example:
        ```python
        user_download_paths = ["/mnt/usb/Downloads", "~/Downloads"]
        try:
            path = PathWriteValidator(user_download_paths).validate()
        except PathValidationError as e:
            raise e("All paths are not writable!")
        else:
            # Do something with the validated path.
            path.write_text("...")
        ```
    """

    def __init__(
        self,
        path: Union[Iterable[str | ProperPath | Path], Union[str, ProperPath, Path]],
        retain_created_file: bool = True,
        err_logger: Optional[logging.Logger] = None,
    ):
        """
        Initializes the class with the provided paths, an option to retain the created
        temporary files, and an optional error logger. The instance maintains these
        parameters throughout its lifecycle.

        Args:
            path (Union[Iterable[str | ProperPath | Path], Union[str, ProperPath, Path]]): An iterable or individual value representing paths. It can include
                strings, ProperPath objects, or Path objects.

        Keyword Args:
            retain_created_file (bool): Flag indicating whether created files (if the given file path already
                doesn't exist) during validation should be retained. Defaults to `True`.
            err_logger (Optional[logging.Logger]): An optional Logger object used for logging errors. If not
                provided, a default error logger will be set.
        """
        self.path = path
        self.err_logger = err_logger or ProperPath.default_err_logger
        self._tmp_file = (
            f".tmp_{''.join(choices(string.ascii_lowercase + string.digits, k=16))}"
        )
        self.retain_created_file = retain_created_file
        self.__self_created_files: list = []

    @property
    def path(self) -> Iterable[str | ProperPath | Path]:
        return self._path

    @path.setter
    def path(self, value):
        if not isinstance(value, (str, NoneType, ProperPath, Path, Iterable)):
            raise ValueError(
                f"{value} must be an instance (or iterable of "
                f"instances) of str, ProperPath, Path"
            )
        try:
            iter(value)
        except TypeError:
            self._path = (value,)
        else:
            self._path = (value,) if isinstance(value, str) else value

    @property
    def _self_created_files(self):
        return self.__self_created_files

    def validate(self) -> ProperPath:
        """
        Returns:
            ProperPath: A validated `ProperPath` instance.
        Raises:
            (PathValidationError): If no valid path can be confirmed from the
            provided list of paths.
        """
        errno: Optional[int] = None
        _self_created_file: bool = False
        for p in self.path:
            if not isinstance(p, ProperPath):
                try:
                    p = ProperPath(p, err_logger=self.err_logger)
                except (ValueError, TypeError):
                    continue
            p_child = (
                ProperPath(p / self._tmp_file, kind="file", err_logger=self.err_logger)
                if p.kind == "dir"
                else p
            )
            try:
                if not p.exists():
                    p.create()
                    self._self_created_files.append(p)
                    _self_created_file = True
                with p_child.open(mode="ba+") as f:
                    f.write(
                        b"\x06"
                    )  # Throwback: \x06 is the ASCII "Acknowledge" character
                    f.seek(f.tell() - 1)
                    if (
                        not f.read(1) == b"\x06"
                    ):  # This checks for /dev/null-type special files!
                        continue  # It'd not be possible to read from those files.
                    f.seek(f.tell() - 1)
                    f.truncate()
            except (
                p.PathException,
                p_child.PathException,
                ValueError,
                AttributeError,
            ) as e:
                errno = getattr(e, "errno", None)
                continue
            else:
                if p.kind == "dir":
                    p_child.remove(verbose=False)
                if (
                    not self.retain_created_file
                    and _self_created_file
                    and p.kind == "file"
                    and p.stat().st_size == 0
                ):
                    p.remove()
                return p
        validation_error = PathValidationError()
        validation_error.errno = errno
        raise validation_error("Given path(s) could not be validated!")
