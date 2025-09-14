import logging
import sys
from copy import deepcopy
from pathlib import Path
from shutil import rmtree
from typing import Optional, Self, Union

from .platformdirs_ import ProperPlatformDirs, ProperUnix


class NoException(Exception): ...


class ProperPath(Path):
    default_err_logger: logging.Logger = logging.getLogger()

    def __init__(
        self,
        *actual: Union[str, Path, "ProperPath"],
        kind: Optional[str] = None,  # Here, None => Undefined/unknown
        err_logger: Optional[logging.Logger] = None,
    ):
        self.actual = actual
        super().__init__(self._expanded)
        self.kind = kind
        self.err_logger = err_logger or ProperPath.default_err_logger
        self.PathException = NoException

    @classmethod
    def platformdirs(
        cls, *args, follow_unix: bool = False, **kwargs
    ) -> ProperPlatformDirs:
        dirs: ProperPlatformDirs | ProperUnix
        if follow_unix is True:
            if sys.platform == "darwin":
                dirs = ProperUnix(
                    *args,
                    path_cls=cls,
                    **kwargs,
                )
            else:
                dirs = ProperPlatformDirs(
                    *args,
                    path_cls=cls,
                    **kwargs,
                )
        else:
            dirs = ProperPlatformDirs(
                *args,
                path_cls=cls,
                **kwargs,
            )
        return dirs

    def __str__(self):
        return str(self._expanded)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(path={self}, actual={self.actual}, "
            f"kind={self.kind}, exists={self.exists()}, "
            f"err_logger={self.err_logger})"
        )

    def __hash__(self):
        return super().__hash__()

    def __deepcopy__(self, memo):
        memo[id(self)] = result = type(self).__new__(type(self))
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __eq__(self, to):
        return super().__eq__(to)

    def __truediv__(self, other) -> "ProperPath":
        return ProperPath(self._expanded / other, err_logger=self.err_logger)

    @property
    def actual(self) -> str:
        return self._actual

    @actual.setter
    def actual(self, value) -> None:
        segments = []
        for segment in value:
            if isinstance(
                segment, ProperPath
            ):  # We want to be able to pass a ProperPath() to ProperPath()
                value = segment.actual
            if isinstance(value, Path):
                value = str(segment)
                # If this isn't handled this way for Path instances,
                # weird issues like "AttributeError: object has
                # no attribute '_raw_paths'. Did you mean: '_raw_path'?" can happen.
            segments.append(value)
        self._actual = value

    @property
    def err_logger(self):
        return self._err_logger

    @err_logger.setter
    def err_logger(self, value):
        if not isinstance(value, logging.Logger):
            raise ValueError(
                f"'err_logger' must be a {logging.Logger.__name__} instance!"
            )
        self._err_logger = value

    # noinspection PyPep8Naming
    @property
    def PathException(self) -> Union[type[Exception], type[BaseException]]:
        return self._PathException

    # noinspection PyPep8Naming
    @PathException.setter
    def PathException(self, value) -> None:
        if not issubclass(value, (Exception, BaseException)):
            raise ValueError(
                "Only an instance of Exception or BaseException can be "
                "assigned to descriptor PathException."
            )
        self._PathException = value

    # noinspection PyPep8Naming
    @PathException.deleter
    def PathException(self):
        raise AttributeError("PathException cannot be deleted!")

    @property
    def _expanded(self) -> Path:
        return Path(*self.actual).expanduser()

    @_expanded.setter
    def _expanded(self, value) -> None:
        raise AttributeError("Expanded is not meant to be modified.")

    @property
    def kind(self) -> str:
        return self._kind

    @kind.setter
    def kind(self, value) -> None:
        if value is None:
            self._kind = (
                "dir"
                if super().is_dir()
                else "file"
                if (super().is_file() or super().suffix or super().exists())
                # self.exists() for special files like /dev/null
                # since is_file() doesn't consider /dev/null to be a file!
                else "dir"
            )
        else:
            match value.lower():
                case "file":
                    self._kind = "file"
                case "dir":
                    self._kind = "dir"
                case _:
                    raise ValueError(
                        f"Invalid value '{value}' for parameter 'kind'. The following values "
                        "for 'kind' are allowed: file, dir."
                    )

    @staticmethod
    def _error_helper_compare_path_source(
        source: Union[Path, str], target: Union[Path, str]
    ) -> str:
        return (
            f"PATH={target} from SOURCE={source}"
            if str(source) != str(target)
            else f"PATH={target}"
        )

    def create(self, verbose: bool = True) -> None:
        path = super().resolve(strict=False)
        try:
            match self.kind:
                case "file":
                    path_parent, path_file = path.parent, path.name
                    if not path_parent.exists() and verbose:
                        self.err_logger.debug(
                            f"File {self._error_helper_compare_path_source(self.actual, path_parent)} "
                            f"could not be found. An attempt to create file "
                            f"{path_parent} will be made."
                        )
                    path_parent.mkdir(parents=True, exist_ok=True)
                    (path_parent / path_file).touch(exist_ok=True)
                case "dir":
                    if not path.exists() and verbose:
                        self.err_logger.debug(
                            f"Directory {self._error_helper_compare_path_source(self.actual, path)} "
                            f"could not be found. An attempt to create directory "
                            f"{path} will be made."
                        )
                    path.mkdir(parents=True, exist_ok=True)
        except (permission_exception := PermissionError) as e:
            message = f"Permission to create {self._error_helper_compare_path_source(self.actual, path)} is denied."
            self.err_logger.debug(message)
            self.PathException = permission_exception
            raise e
        except (not_a_dir_exception := NotADirectoryError) as e:
            # Both "file" and "dir" cases are handled, but when the path is under special files like
            # /dev/null/<directory name>, os.mkdir() will throw NotADirectoryError.
            message = f"Couldn't create {self._error_helper_compare_path_source(self.actual, path)}."
            self.err_logger.debug(message)
            self.PathException = not_a_dir_exception
            raise e
        except (os_exception := OSError) as os_err:
            # When an attempt to create a file or directory inside root (e.g., '/foo')
            # is made, OS can throw OSError with error no. 30 instead of PermissionError.
            self.err_logger.debug(os_err)
            self.PathException = os_exception
            raise os_err

    def _remove_file(
        self, _file: Union[Path, Self, None] = None, verbose: bool = True
    ) -> None:
        file = _file or self._expanded
        if not isinstance(file, Path):
            raise ValueError(
                f"PATH={file} is empty or isn't a valid pathlib.Path instance! "
                f"Check instance attribute 'expanded'."
            )
        try:
            file.unlink()
        except (file_not_found_exception := FileNotFoundError) as e:
            # unlink() throws FileNotFoundError when a directory is passed as it expects files only
            self.err_logger.error(
                f"Could not remove {self._error_helper_compare_path_source(self.actual, file)}. "
                f"Exception: {e!r}"
            )
            self.PathException = file_not_found_exception
            raise e
        except (permission_exception := PermissionError) as e:
            message = (
                f"Permission to remove {self._error_helper_compare_path_source(self.actual, file)} "
                f"as a file is denied."
            )
            self.err_logger.debug(message)
            self.PathException = permission_exception
            raise e
        if verbose:
            self.err_logger.debug(f"Removed file: {file}")

    def remove(self, parent_only: bool = False, verbose: bool = True) -> None:
        # removes everything (if parent_only is False) found inside a ProperPath except the parent directory of the path
        # if the ProperPath isn't a directory, then it just removes the file
        if self.kind == "file":
            self._remove_file(verbose=verbose)
        elif self.kind == "dir":
            ls_ref = super().glob(r"**/*") if not parent_only else super().glob(r"*.*")
            for ref in ls_ref:
                match ProperPath(ref).kind:
                    case "file":
                        self._remove_file(_file=ref, verbose=verbose)
                        # Either FileNotFoundError and PermissionError occurring can mean that
                        # a dir path was passed when its kind is set as "file"
                    case "dir":
                        rmtree(ref)
                        self.err_logger.debug(
                            f"Deleted directory (recursively): {ref}"
                        ) if verbose else ...
                        # rmtree deletes files and directories recursively.
                        # So in case of permission error with rmtree(ref),
                        # shutil.rmtree() might give better
                        # traceback message. I.e., which file or directory exactly

    def open(self, mode="r", encoding=None, *args):
        file = super().resolve()
        try:
            return Path(file).open(
                mode=mode,
                encoding=encoding,
                *args,
            )
        except OSError as e:
            self.err_logger.warning(
                f"Could not open file {self._error_helper_compare_path_source(self.actual, file)}. "
                f"Exception: {e!r}"
            )
            self.PathException = e
            raise e
