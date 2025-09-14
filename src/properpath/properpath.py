import logging
import sys
from copy import deepcopy
from pathlib import Path
from shutil import rmtree
from typing import Literal, Optional, Self, Union

from .platformdirs_ import ProperPlatformDirs, ProperUnix


class NoException(Exception):
    """
    NoException works as an exception placeholder only.
    It is used as the default value of PathException.
    """


class ProperPath(Path):
    """
    A pathlib.Path subclass that offers some additional app-development-friendly features like
    custom logging for errors, automatic user expansion, information-rich repr,
    create and remove files/directories without having to know if the path is a
    directory or a file, etc. Example::

        from properpath import ProperPath

        path1 = ProperPath("~/Downloads")
        repr(path1)
        # Prints: ProperPath(path=/Users/culdesac/Downloads, actual=('~/Downloads',),
        kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)

    :cvar default_err_logger: The default logger instance is used when no custom
        logger is provided to an instance.
    :type default_err_logger: logging.Logger
    """

    default_err_logger: logging.Logger = logging.getLogger()

    def __init__(
        self,
        *actual: Union[str, Path, "ProperPath"],
        kind: Optional[str] = None,  # Here, None => Undefined/unknown
        err_logger: Optional[logging.Logger] = None,
    ):
        """
        Initializes a ProperPath instance. A ProperPath instance can be passed to pathlib.Path and vice versa.

        :param actual: A collection of paths provided as strings, `Path` objects,
            or `ProperPath` objects that represent the input paths to be processed.
            This acts just like the first argument passed to pathlib.Path.  E.g., ProperPath("~", "foo")
        :type actual: Union[str, Path, ProperPath]

        :param kind: An optional string to indicate if the path is a file or a directory. If it is None (the default),
            ProperPath will try to determine the kind automatically based on file suffixes and various other patterns.
        :type kind: Optional[str]

        :param err_logger: An optional `Logger` object for handling error logging.
            If None, the class instance default_err_logger is used.
        :type err_logger: Optional[logging.Logger]
        """

        self._kind: Literal["file", "dir"]
        self.actual = actual
        super().__init__(self._expanded)
        self.kind = kind
        self.err_logger = err_logger or ProperPath.default_err_logger
        self.PathException = NoException

    @classmethod
    def platformdirs(
        cls,
        appname: Optional[str] = None,
        appauthor: str | Literal[False] | None = None,
        version: Optional[str] = None,
        roaming: bool = False,
        multipath: bool = False,
        opinion: bool = True,
        ensure_exists: bool = False,
        follow_unix: bool = False,
    ) -> ProperPlatformDirs:
        """
        Initializes and returns a "platformdirs.PlatformDirs" instance that offers
        appropriate platform-specific application directories. E.g., OS-standard location for configuration files, logs, shared files, caches, etc.
        See platformdirs documentation for more details: https://github.com/tox-dev/platformdirs

        platformdirs doesn't offer a way to get Unix-like directories on macOS which may not be always desired. So,
        ProperPath.platformdirs offers an additional argument "follow_unix" which is False by default. If "follow_unix" is True,
        ProperPath.platformdirs will return an instance that follows Unix-like directory structure for both macOS and
        Linux-based operating systems. Windows paths will not be altered.

        Any other arguments and keyword arguments passed to this method will be passed to the
        platformdirs.PlatformDirs as is. Examples::

            app_dirs = ProperPath.platformdirs("MyApp", "MyOrg")
            app_dirs.user_data_dir
            # Returns ProperPath('/Users/user/Library/Application Support/MyApp')

            # Use Unix-like paths on macOS
            app_dirs = ProperPath.platformdirs("MyApp", follow_unix=True)
            app_dirs.user_data_dir
            # Returns a Unix-style path even on macOS: ProperPath('/home/user/.local/share/MyApp

            # With additional arguments for platformdirs.PlatformDirs
            dirs = ProperPath.platformdirs("MyApp", version="1.0", roaming=True)
            dirs.user_config_dir
            # Returns ProperPath('/Users/user/Library/Application Support/MyApp/1.0')


        :param follow_unix: Specifies whether to enforce a Unix-like directory structure
            for both macOS and Linux. Defaults to False.

        :param appname: The name of the app author or distributing body for this application.
        :type appname: Optional[str]

        :param appauthor: Typically, it is the owning company name. Defaults to `appname`.
            You may pass ``False`` to disable it.
        :type appauthor: str | Literal[False] | None

        :param version: An optional version path element to append to the path.
        You might want to use this if you want multiple versions of your app to be able to run independently. If used,
        this would typically be ``<major>.<minor>``.
        :type version: Optional[str]

        :param roaming: Whether to use the roaming appdata directory on Windows.
        That means that for users on a Windows network setup for roaming profiles, this user data will be synced on
        login (see `here <https://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx>`_).
        :type roaming: bool

        :param multipath: An optional parameter which indicates that the entire list of data dirs should be returned.
            By default, the first item would only be returned.
        :type multipath: bool

        :param opinion: A flag to indicating to use opinionated values.
        :type opinion: bool

        :param ensure_exists: Optionally create the directory (and any missing parents) upon access if it does not exist.
            By default, no directories are created.
        :type ensure_exists: bool

        :return: An instance of the appropriate platform directory handler (PlatformDirs)
        :rtype: ProperPlatformDirs
        """

        dirs: ProperPlatformDirs | ProperUnix
        if follow_unix is True:
            if sys.platform == "darwin":
                dirs = ProperUnix(
                    appname,
                    appauthor,
                    version,
                    roaming,
                    multipath,
                    opinion,
                    ensure_exists,
                    path_cls=cls,
                )
            else:
                dirs = ProperPlatformDirs(
                    appname,
                    appauthor,
                    version,
                    roaming,
                    multipath,
                    opinion,
                    ensure_exists,
                    path_cls=cls,
                )
        else:
            dirs = ProperPlatformDirs(
                appname,
                appauthor,
                version,
                roaming,
                multipath,
                opinion,
                ensure_exists,
                path_cls=cls,
            )
        return dirs

    def __str__(self):
        return str(self._expanded)

    def __repr__(self):
        """
        :return: An information-rich representation of the ProperPath instance.
        """
        return (
            f"{self.__class__.__name__}(path={self}, actual={self.actual}, "
            f"kind={self.kind}, exists={self.exists()}, "
            f"err_logger={self.err_logger})"
        )

    def __hash__(self):
        return super().__hash__()

    def __deepcopy__(self, memo):
        """
        ProperPath, likely due to being a victim of inheritance hell, can throw odd errors when it is deepcopied
        as a namedtuple. The __deepcopy__ method is overridden to avoid that. Notice, only instance attributes are
        deepcopied, not properties.

        :param memo:
        :return:
        """
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
        """
        Provides access to the user-given path (or path segments) that was passed to the constructor of the
        ProperPath instance. ProperPath by default expands any user indicator "~"
        automatically and uses the expanded path internally. The actual will show the non-expanded value.
        E.g.::

            ProperPath("~", "foo").actual
            # Returns ("~", "foo")

        :return: The path value
        :rtype: str
        """
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
        """
        Provides access to the error logger that is used for logging exceptions.
        The default logger is ProperPath.default_err_logger.

        :return: The error logger instance.
        :rtype: Logger
        """
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
    def PathException(self) -> type[Exception] | type[BaseException]:
        """
        PathException property stores an exception (like OSException) raised for the working path instance,
        before the exception is raised normally. In some ways, PathException treats
        errors/exceptions as values. PathException can be used to create design patterns where one path failing,
        doesn't matter, but any path from a list of available paths can be used for the user. Example::

            # Storing data to a file of from a list of fallback file paths:
            path_exceptions = []

            for path in [ProperPath("/media/usb/file.txt"), ProperPath("~/Downloads/file.txt")]:
                try:
                    path.write_text("Hello, World!")
                except path.PathException as e:
                    # Ignore exception, just try the next path.
                    # Exception is automatically logged by path.err_logger
                    path_exceptions.append(e)
                    continue
                else:
                    # Write is successful without any error, we exit the loop.
                    break
            else:
                # When all paths failed, raise the last exception (or all exceptions).
                path.err_logger.error(f"Couldn't write to any of the fallback paths. Exceptions: {path_exceptions}")
                raise path.PathException


        :return: The exception thrown for the working path instance.
        :rtype: type[Exception] | type[BaseException]
        """
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
    def kind(self) -> Literal["file", "dir"]:
        """
        Retrieves the path kind: a "file" or a "dir".
        If the path exists, kind already knows what kind it is. If the path doesn't exist, kind tries to assume the kind from
        file suffixes. Kind can also handle special files like /dev/null. kind is set during instance creation.

        :return: "file" or "dir" depending on the path.
        :rtype: Literal["file", "dir"]
        """

        # noinspection PyTypeChecker
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
        """
        Creates a file or directory based on the specified kind (file or dir). Thanks to property "kind",
        the "create" method helps to avoid writing boilerplate code like "if path.is_file()"
        or "path.is_dir()". For files and directories, it ensures the parent directory exists
        before creating the file. Logs operations and exceptions for debugging.

        :param verbose: If True, debug logs will be generated to trace creation
            attempts for files and directories.
        :type verbose: bool
        :return: None
        :raises PermissionError: If the operation lacks permission to create the file
            or directory.
        :raises NotADirectoryError: If the operation attempts to create a directory
            under a path that is incorrectly treated as a non-directory.
        :raises OSError: If an OS-level error (all others excluding PermissionError and
            NotADirectoryError) occurs during the creation process.
        """
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
        """
        Removes the ProperPath file or directory based on the specified parameters. The method
        removes either all contents of a directory path or a single file, depending on the type of
        the path (file or directory). If `parent_only` is True, only top-level contents are removed
        while keeping the parent directory intact. If `parent_only` is False, all contents are
        removed recursively. Verbose can be set to True (default) to log the removal.

        :param parent_only: A boolean flag indicating whether only the immediate children of the
            directory should be removed, leaving the parent directory intact. Defaults to False.
        :param verbose: A boolean flag indicating whether detailed logs of the removal operations
            should be printed or logged. Defaults to True.
        :return: None
        """
        # removes everything (if parent_only is False) found inside a ProperPath except the parent directory of the path
        # if the ProperPath isn't a directory, then it just removes the file
        if self.kind == "file":
            self._remove_file(verbose=verbose)
        elif self.kind == "dir":
            ls_ref = super().glob(r"**/*") if not parent_only else super().glob(r"*")
            for ref in ls_ref:
                match ProperPath(ref).kind:
                    case "file":
                        self._remove_file(_file=ref, verbose=verbose)
                        # Either FileNotFoundError and PermissionError occurring can mean that
                        # a dir path was passed when its kind is set as "file"
                    case "dir" if not parent_only:
                        rmtree(ref)
                        self.err_logger.debug(
                            f"Deleted directory (recursively): {ref}"
                        ) if verbose else ...
                        # rmtree deletes files and directories recursively.
                        # So in case of permission error with rmtree(ref),
                        # shutil.rmtree() might give better
                        # traceback message. I.e., which file or directory exactly

    def open(self, mode="r", encoding=None, *args, **kwargs):
        """
        ProperPath open instance method simply returns pathlib.Path.open.
        open() resolves the whole path first before opening.
        """
        file = super().resolve()
        try:
            return Path(file).open(
                mode=mode,
                encoding=encoding,
                *args,
                **kwargs,
            )
        except (os_exception := OSError) as e:
            self.err_logger.warning(
                f"Could not open file {self._error_helper_compare_path_source(self.actual, file)}. "
                f"Exception: {e!r}"
            )
            self.PathException = os_exception
            raise e
