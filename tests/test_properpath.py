import logging
import os
import stat
from pathlib import Path

import pytest

from properpath import NoException, ProperPath

logging.getLogger().setLevel(logging.DEBUG)


def test_properpath_initialization(tmp_path):
    """Tests ProperPath initialization with various input types."""
    # Test with a string
    p_str = ProperPath(str(tmp_path / "test.txt"))
    assert isinstance(p_str, ProperPath)
    assert p_str.name == "test.txt"

    # Test with a pathlib.Path object
    path_obj = tmp_path / "test_dir"
    p_path = ProperPath(path_obj)
    assert p_path.name == "test_dir"

    # Test with another ProperPath object
    p_proper = ProperPath(p_str)
    assert p_proper.actual == p_str.actual

    # Test user expansion ('~')
    home_dir = Path.home()
    p_home = ProperPath("~")
    assert str(p_home) == str(home_dir)
    assert p_home.actual == ("~",)

    # Test multiple segments
    p_multi = ProperPath("~", "Downloads")
    assert str(p_multi) == str(home_dir / "Downloads")
    assert p_multi.actual == ("~", "Downloads")


def test_pathlib_compatibility(tmp_path):
    """Tests that ProperPath instances behave like pathlib.Path instances."""
    p = ProperPath(tmp_path / "a" / "b" / "c.txt")

    assert p.name == "c.txt"
    assert p.stem == "c"
    assert p.suffix == ".txt"
    # __truediv__ returns a ProperPath, so parent is also a ProperPath
    assert p.parent == ProperPath(tmp_path / "a" / "b")
    assert isinstance(p.parent, ProperPath)
    assert p.parts[-3:] == ("a", "b", "c.txt")


def test_truediv_operator(tmp_path):
    """Tests the / (__truediv__) operator."""
    p1 = ProperPath(tmp_path)
    p2 = p1 / "a" / "b"
    assert isinstance(p2, ProperPath)
    assert str(p2) == str(tmp_path / "a" / "b")


def test_kind_detection(tmp_path):
    """Tests the 'kind' property for various scenarios."""
    # Kind detection for a file with a suffix (non-existent)
    file_path = ProperPath(tmp_path / "some_file.txt")
    assert file_path.kind == "file"

    # Kind detection for a path without a suffix (non-existent)
    dir_path = ProperPath(tmp_path / "some_dir")
    assert dir_path.kind == "dir"  # Assumes 'dir' if no suffix and not existing

    # Kind detection for an existing file
    existing_file = tmp_path / "existing.txt"
    existing_file.touch()
    p_existing_file = ProperPath(existing_file)
    assert p_existing_file.kind == "file"
    assert p_existing_file.exists()

    # Kind detection for an existing directory
    existing_dir = tmp_path / "existing_dir"
    existing_dir.mkdir()
    p_existing_dir = ProperPath(existing_dir)
    assert p_existing_dir.kind == "dir"
    assert p_existing_dir.exists()

    # Explicitly setting kind
    explicit_file = ProperPath(tmp_path / "no_suffix_as_file", kind="file")
    assert explicit_file.kind == "file"

    explicit_dir = ProperPath(tmp_path / "file.with.suffix.as.dir", kind="dir")
    assert explicit_dir.kind == "dir"

    with pytest.raises(ValueError):
        ProperPath("test", kind="invalid_kind")


def test_create_and_remove_file(tmp_path):
    """Tests creating and removing a file."""
    file_path = ProperPath(tmp_path / "new_dir" / "new_file.txt", kind="file")
    assert not file_path.exists()
    assert not file_path.parent.exists()

    # Create file and its parent directory
    file_path.create()
    assert file_path.exists()
    assert file_path.is_file()
    assert file_path.parent.exists()

    # Remove file
    file_path.remove()
    assert not file_path.exists()


def test_create_and_remove_dir(tmp_path):
    """Tests creating and removing a directory and its contents."""
    base_dir = ProperPath(tmp_path / "base_dir", kind="dir")
    sub_dir = ProperPath(base_dir / "sub_dir", kind="dir")
    file_in_sub_dir = ProperPath(sub_dir / "file.txt", kind="file")

    # Create nested structure
    file_in_sub_dir.create()
    assert base_dir.exists() and base_dir.is_dir()
    assert sub_dir.exists() and sub_dir.is_dir()
    assert file_in_sub_dir.exists() and file_in_sub_dir.is_file()

    # Remove contents of base_dir recursively
    base_dir.remove(parent_only=False)
    assert base_dir.exists()  # The directory itself should remain
    assert not list(base_dir.iterdir())  # But it should be empty
    assert not sub_dir.exists()
    assert not file_in_sub_dir.exists()


def test_remove_dir_parent_only(tmp_path):
    """
    Tests the bug in `remove(parent_only=True)` where it only removes
    files with extensions because of `glob('*.*')`.
    """
    base_dir = ProperPath(tmp_path / "base", kind="dir")
    base_dir.create()

    sub_dir = base_dir / "subdir"
    ProperPath(sub_dir, kind="dir").create()

    file_with_ext = base_dir / "file.txt"
    file_with_ext.touch()

    file_no_ext = base_dir / "file_no_ext"
    file_no_ext.touch()

    assert sub_dir.exists()
    assert file_with_ext.exists()
    assert file_no_ext.exists()

    base_dir.remove(parent_only=True)
    assert not file_with_ext.exists()
    assert sub_dir.exists(), "Directory should not have been removed"
    assert not file_no_ext.exists(), "File without extension should have been removed"


def test_path_exception_handling(tmp_path):
    """Tests that PathException property is set correctly on errors."""
    # Test on create()
    read_only_dir = tmp_path / "read_only"
    read_only_dir.mkdir()
    os.chmod(read_only_dir, stat.S_IREAD | stat.S_IXUSR)

    p_create = ProperPath(read_only_dir / "test.txt", kind="file")
    with pytest.raises(PermissionError):
        p_create.create()
    assert p_create.PathException is PermissionError
    os.chmod(read_only_dir, stat.S_IWRITE | stat.S_IREAD | stat.S_IXUSR)

    # Test on open()
    non_existent_file = ProperPath(tmp_path / "non_existent.txt")
    with pytest.raises(FileNotFoundError):
        non_existent_file.open()
    assert non_existent_file.PathException is FileNotFoundError

    # Test on remove()
    p_remove = ProperPath(tmp_path / "dir_as_file.txt", kind="dir")
    p_remove.create()
    p_remove.kind = "file"
    # noinspection PyTypeChecker
    with pytest.raises((IsADirectoryError, PermissionError)):
        # NotADirectoryError is the expected one. But sometimes,
        # depending on the OS, PermissionError can also be raised
        p_remove.remove()
    assert (
        p_remove.PathException is IsADirectoryError
        or p_remove.PathException is PermissionError
    )


def test_default_path_exception():
    """Tests that PathException defaults to NoException."""
    p = ProperPath(".")
    assert p.PathException is NoException
