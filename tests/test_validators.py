import os
import stat

import pytest

from properpath import ProperPath
from properpath.validators import PathValidationError, PathWriteValidator


def test_pathwritevalidator_writable_dir(tmp_path):
    """Tests validation on a writable directory."""
    validator = PathWriteValidator(tmp_path)
    validated_path = validator.validate()
    assert validated_path == tmp_path
    assert isinstance(validated_path, ProperPath)


def test_pathwritevalidator_writable_new_file(tmp_path):
    """Tests validation on a non-existent file path that is writable."""
    file_path = tmp_path / "test_file.txt"
    assert not file_path.exists()

    validator = PathWriteValidator(file_path)
    validated_path = validator.validate()

    assert validated_path == file_path
    assert file_path.exists()
    assert file_path.is_file()


def test_pathwritevalidator_writable_existing_file(tmp_path):
    """Tests validation on an existing file that is writable."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("hello")

    validator = PathWriteValidator(file_path)
    validated_path = validator.validate()

    assert validated_path == file_path
    assert file_path.read_text() == "hello"


def test_pathwritevalidator_retain_created_file_false(tmp_path):
    """Tests the `retain_created_file=False` option."""
    file_path = tmp_path / "temp_file.txt"
    validator = PathWriteValidator(file_path, retain_created_file=False)
    validator.validate()
    assert not file_path.exists()


def test_pathwritevalidator_with_iterable_paths(tmp_path):
    """Tests validation with a list of paths, where one is valid."""
    writable_path = tmp_path / "writable"
    writable_path.mkdir()

    read_only_dir = tmp_path / "read_only"
    read_only_dir.mkdir()
    os.chmod(read_only_dir, stat.S_IREAD | stat.S_IXUSR)

    paths = [read_only_dir, writable_path]

    validator = PathWriteValidator(paths)
    validated_path = validator.validate()
    assert validated_path == writable_path

    # Clean up
    os.chmod(read_only_dir, stat.S_IWRITE | stat.S_IREAD | stat.S_IXUSR)


def test_pathwritevalidator_no_writable_path(tmp_path):
    """Tests that PathValidationError is raised when no paths are writable."""
    read_only_dir = tmp_path / "read_only"
    read_only_dir.mkdir()
    os.chmod(read_only_dir, stat.S_IREAD | stat.S_IXUSR)

    validator = PathWriteValidator(read_only_dir)
    with pytest.raises(PathValidationError) as excinfo:
        validator.validate()
    assert "Given path(s) could not be validated!" in str(excinfo.value)

    # Clean up
    os.chmod(read_only_dir, stat.S_IWRITE | stat.S_IREAD | stat.S_IXUSR)


def test_pathwritevalidator_with_uncreatable_file(tmp_path):
    """Tests validation with a file in a read-only directory."""
    read_only_dir = tmp_path / "ro_dir"
    read_only_dir.mkdir()
    os.chmod(read_only_dir, stat.S_IREAD | stat.S_IXUSR)

    file_in_ro_dir = read_only_dir / "file.txt"

    validator = PathWriteValidator(file_in_ro_dir)
    with pytest.raises(PathValidationError):
        validator.validate()

    # Clean up
    os.chmod(read_only_dir, stat.S_IWRITE | stat.S_IREAD | stat.S_IXUSR)
