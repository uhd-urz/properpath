"""
The test suite here is derived from https://github.com/python/cpython/blob/3.12/Lib/test/test_pathlib.py.
These tests were written for pathlib.Path objects. Here, we only use the tests relevant for
the ProperPath class.
"""

import errno
import os
import pathlib
import stat
import unittest
from unittest import mock

import properpath
from test.support import (
    is_emscripten,
    os_helper,
    set_recursion_limit,
)
from extra_test.support.os_helper import TESTFN, FakePath

try:
    import grp
    import pwd
except ImportError:
    grp = pwd = None


#
# Tests for the pure classes.
#


class _BasePurePathSubclass(object):
    def __init__(self, *pathsegments, session_id):
        super().__init__(*pathsegments)
        self.session_id = session_id

    def with_segments(self, *pathsegments):
        return type(self)(*pathsegments, session_id=self.session_id)


# Tests for the concrete classes.
#

# Make sure any symbolic links in the base test path are resolved.
BASE = os.path.realpath(TESTFN)
join = lambda *x: os.path.join(BASE, *x)
rel_join = lambda *x: os.path.join(TESTFN, *x)

only_nt = unittest.skipIf(os.name != "nt", "test requires a Windows-compatible system")
only_posix = unittest.skipIf(os.name == "nt", "test requires a POSIX-compatible system")


class _BasePathTest(object):
    """Tests for the FS-accessing functionalities of the Path classes."""

    # (BASE)
    #  |
    #  |-- brokenLink -> non-existing
    #  |-- dirA
    #  |   `-- linkC -> ../dirB
    #  |-- dirB
    #  |   |-- fileB
    #  |   `-- linkD -> ../dirB
    #  |-- dirC
    #  |   |-- dirD
    #  |   |   `-- fileD
    #  |   `-- fileC
    #  |   `-- novel.txt
    #  |-- dirE  # No permissions
    #  |-- fileA
    #  |-- linkA -> fileA
    #  |-- linkB -> dirB
    #  `-- brokenLinkLoop -> brokenLinkLoop
    #

    def setUp(self):
        def cleanup():
            os.chmod(join("dirE"), 0o777)
            os_helper.rmtree(BASE)

        self.addCleanup(cleanup)
        os.mkdir(BASE)
        os.mkdir(join("dirA"))
        os.mkdir(join("dirB"))
        os.mkdir(join("dirC"))
        os.mkdir(join("dirC", "dirD"))
        os.mkdir(join("dirE"))
        with open(join("fileA"), "wb") as f:
            f.write(b"this is file A\n")
        with open(join("dirB", "fileB"), "wb") as f:
            f.write(b"this is file B\n")
        with open(join("dirC", "fileC"), "wb") as f:
            f.write(b"this is file C\n")
        with open(join("dirC", "novel.txt"), "wb") as f:
            f.write(b"this is a novel\n")
        with open(join("dirC", "dirD", "fileD"), "wb") as f:
            f.write(b"this is file D\n")
        os.chmod(join("dirE"), 0)
        if os_helper.can_symlink():
            # Relative symlinks.
            os.symlink("fileA", join("linkA"))
            os.symlink("non-existing", join("brokenLink"))
            self.dirlink("dirB", join("linkB"))
            self.dirlink(os.path.join("..", "dirB"), join("dirA", "linkC"))
            # This one goes upwards, creating a loop.
            self.dirlink(os.path.join("..", "dirB"), join("dirB", "linkD"))
            # Broken symlink (pointing to itself).
            os.symlink("brokenLinkLoop", join("brokenLinkLoop"))

    if os.name == "nt":
        # Workaround for http://bugs.python.org/issue13772.
        def dirlink(self, src, dest):
            os.symlink(src, dest, target_is_directory=True)
    else:

        def dirlink(self, src, dest):
            os.symlink(src, dest)

    def assertSame(self, path_a, path_b):
        self.assertTrue(
            os.path.samefile(str(path_a), str(path_b)),
            "%r and %r don't point to the same file" % (path_a, path_b),
        )

    def assertFileNotFound(self, func, *args, **kwargs):
        with self.assertRaises(FileNotFoundError) as cm:
            func(*args, **kwargs)
        self.assertEqual(cm.exception.errno, errno.ENOENT)

    def assertEqualNormCase(self, path_a, path_b):
        self.assertEqual(os.path.normcase(path_a), os.path.normcase(path_b))

    def _test_cwd(self, p):
        q = self.cls(os.getcwd())
        self.assertEqual(p, q)
        self.assertEqualNormCase(str(p), str(q))
        self.assertIs(type(p), type(q))
        self.assertTrue(p.is_absolute())

    def test_cwd(self):
        p = self.cls.cwd()
        self._test_cwd(p)

    def test_absolute_common(self):
        P = self.cls

        with mock.patch("os.getcwd") as getcwd:
            getcwd.return_value = BASE

            # Simple relative paths.
            self.assertEqual(str(P().absolute()), BASE)
            self.assertEqual(str(P(".").absolute()), BASE)
            self.assertEqual(str(P("a").absolute()), os.path.join(BASE, "a"))
            self.assertEqual(
                str(P("a", "b", "c").absolute()), os.path.join(BASE, "a", "b", "c")
            )

            # Symlinks should not be resolved.
            self.assertEqual(
                str(P("linkB", "fileB").absolute()),
                os.path.join(BASE, "linkB", "fileB"),
            )
            self.assertEqual(
                str(P("brokenLink").absolute()), os.path.join(BASE, "brokenLink")
            )
            self.assertEqual(
                str(P("brokenLinkLoop").absolute()),
                os.path.join(BASE, "brokenLinkLoop"),
            )

            # '..' entries should be preserved and not normalised.
            self.assertEqual(str(P("..").absolute()), os.path.join(BASE, ".."))
            self.assertEqual(
                str(P("a", "..").absolute()), os.path.join(BASE, "a", "..")
            )
            self.assertEqual(
                str(P("..", "b").absolute()), os.path.join(BASE, "..", "b")
            )

    def test_glob_above_recursion_limit(self):
        recursion_limit = 50
        # directory_depth > recursion_limit
        directory_depth = recursion_limit + 10
        base = properpath.ProperPath(os_helper.TESTFN, "deep")
        path = properpath.ProperPath(base, *(["d"] * directory_depth))
        path.mkdir(parents=True)

        with set_recursion_limit(recursion_limit):
            list(base.glob("**"))


class WalkTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(os_helper.rmtree, os_helper.TESTFN)

        # Build:
        #     TESTFN/
        #       TEST1/              a file kid and two directory kids
        #         tmp1
        #         SUB1/             a file kid and a directory kid
        #           tmp2
        #           SUB11/          no kids
        #         SUB2/             a file kid and a dirsymlink kid
        #           tmp3
        #           SUB21/          not readable
        #             tmp5
        #           link/           a symlink to TEST2
        #           broken_link
        #           broken_link2
        #           broken_link3
        #       TEST2/
        #         tmp4              a lone file
        self.walk_path = properpath.ProperPath(os_helper.TESTFN, "TEST1")
        self.sub1_path = self.walk_path / "SUB1"
        self.sub11_path = self.sub1_path / "SUB11"
        self.sub2_path = self.walk_path / "SUB2"
        sub21_path = self.sub2_path / "SUB21"
        tmp1_path = self.walk_path / "tmp1"
        tmp2_path = self.sub1_path / "tmp2"
        tmp3_path = self.sub2_path / "tmp3"
        tmp5_path = sub21_path / "tmp3"
        self.link_path = self.sub2_path / "link"
        t2_path = properpath.ProperPath(os_helper.TESTFN, "TEST2")
        tmp4_path = properpath.ProperPath(os_helper.TESTFN, "TEST2", "tmp4")
        broken_link_path = self.sub2_path / "broken_link"
        broken_link2_path = self.sub2_path / "broken_link2"
        broken_link3_path = self.sub2_path / "broken_link3"

        os.makedirs(self.sub11_path)
        os.makedirs(self.sub2_path)
        os.makedirs(sub21_path)
        os.makedirs(t2_path)

        for path in tmp1_path, tmp2_path, tmp3_path, tmp4_path, tmp5_path:
            with open(path, "x", encoding="utf-8") as f:
                f.write(f"I'm {path} and proud of it.  Blame test_pathlib.\n")

        if os_helper.can_symlink():
            os.symlink(os.path.abspath(t2_path), self.link_path)
            os.symlink("broken", broken_link_path, True)
            os.symlink(properpath.ProperPath("tmp3", "broken"), broken_link2_path, True)
            os.symlink(properpath.ProperPath("SUB21", "tmp5"), broken_link3_path, True)
            self.sub2_tree = (
                self.sub2_path,
                ["SUB21"],
                ["broken_link", "broken_link2", "broken_link3", "link", "tmp3"],
            )
        else:
            self.sub2_tree = (self.sub2_path, ["SUB21"], ["tmp3"])

        if not is_emscripten:
            # Emscripten fails with inaccessible directories.
            os.chmod(sub21_path, 0)
        try:
            os.listdir(sub21_path)
        except PermissionError:
            self.addCleanup(os.chmod, sub21_path, stat.S_IRWXU)
        else:
            os.chmod(sub21_path, stat.S_IRWXU)
            os.unlink(tmp5_path)
            os.rmdir(sub21_path)
            del self.sub2_tree[1][:1]

    def test_walk_topdown(self):
        walker = self.walk_path.walk()
        entry = next(walker)
        entry[1].sort()  # Ensure we visit SUB1 before SUB2
        self.assertEqual(entry, (self.walk_path, ["SUB1", "SUB2"], ["tmp1"]))
        entry = next(walker)
        self.assertEqual(entry, (self.sub1_path, ["SUB11"], ["tmp2"]))
        entry = next(walker)
        self.assertEqual(entry, (self.sub11_path, [], []))
        entry = next(walker)
        entry[1].sort()
        entry[2].sort()
        self.assertEqual(entry, self.sub2_tree)
        with self.assertRaises(StopIteration):
            next(walker)

    def test_walk_prune(self, walk_path=None):
        if walk_path is None:
            walk_path = self.walk_path
        # Prune the search.
        all = []
        for root, dirs, files in walk_path.walk():
            all.append((root, dirs, files))
            if "SUB1" in dirs:
                # Note that this also mutates the dirs we appended to all!
                dirs.remove("SUB1")

        self.assertEqual(len(all), 2)
        self.assertEqual(all[0], (self.walk_path, ["SUB2"], ["tmp1"]))

        all[1][-1].sort()
        all[1][1].sort()
        self.assertEqual(all[1], self.sub2_tree)

    def test_file_like_path(self):
        self.test_walk_prune(FakePath(self.walk_path).__fspath__())

    def test_walk_bottom_up(self):
        seen_testfn = seen_sub1 = seen_sub11 = seen_sub2 = False
        for path, dirnames, filenames in self.walk_path.walk(top_down=False):
            if path == self.walk_path:
                self.assertFalse(seen_testfn)
                self.assertTrue(seen_sub1)
                self.assertTrue(seen_sub2)
                self.assertEqual(sorted(dirnames), ["SUB1", "SUB2"])
                self.assertEqual(filenames, ["tmp1"])
                seen_testfn = True
            elif path == self.sub1_path:
                self.assertFalse(seen_testfn)
                self.assertFalse(seen_sub1)
                self.assertTrue(seen_sub11)
                self.assertEqual(dirnames, ["SUB11"])
                self.assertEqual(filenames, ["tmp2"])
                seen_sub1 = True
            elif path == self.sub11_path:
                self.assertFalse(seen_sub1)
                self.assertFalse(seen_sub11)
                self.assertEqual(dirnames, [])
                self.assertEqual(filenames, [])
                seen_sub11 = True
            elif path == self.sub2_path:
                self.assertFalse(seen_testfn)
                self.assertFalse(seen_sub2)
                self.assertEqual(sorted(dirnames), sorted(self.sub2_tree[1]))
                self.assertEqual(sorted(filenames), sorted(self.sub2_tree[2]))
                seen_sub2 = True
            else:
                raise AssertionError(f"Unexpected path: {path}")
        self.assertTrue(seen_testfn)

    @os_helper.skip_unless_symlink
    def test_walk_follow_symlinks(self):
        walk_it = self.walk_path.walk(follow_symlinks=True)
        for root, dirs, files in walk_it:
            if root == self.link_path:
                self.assertEqual(dirs, [])
                self.assertEqual(files, ["tmp4"])
                break
        else:
            self.fail("Didn't follow symlink with follow_symlinks=True")

    @os_helper.skip_unless_symlink
    def test_walk_symlink_location(self):
        # Tests whether symlinks end up in filenames or dirnames depending
        # on the `follow_symlinks` argument.
        walk_it = self.walk_path.walk(follow_symlinks=False)
        for root, dirs, files in walk_it:
            if root == self.sub2_path:
                self.assertIn("link", files)
                break
        else:
            self.fail("symlink not found")

        walk_it = self.walk_path.walk(follow_symlinks=True)
        for root, dirs, files in walk_it:
            if root == self.sub2_path:
                self.assertIn("link", dirs)
                break

    def test_walk_bad_dir(self):
        errors = []
        walk_it = self.walk_path.walk(on_error=errors.append)
        root, dirs, files = next(walk_it)
        self.assertEqual(errors, [])
        dir1 = "SUB1"
        path1 = root / dir1
        path1new = (root / dir1).with_suffix(".new")
        path1.rename(path1new)
        try:
            roots = [r for r, _, _ in walk_it]
            self.assertTrue(errors)
            self.assertNotIn(path1, roots)
            self.assertNotIn(path1new, roots)
            for dir2 in dirs:
                if dir2 != dir1:
                    self.assertIn(root / dir2, roots)
        finally:
            path1new.rename(path1)

    def test_walk_many_open_files(self):
        depth = 30
        base = properpath.ProperPath(os_helper.TESTFN, "deep")
        path = properpath.ProperPath(base, *(["d"] * depth))
        path.mkdir(parents=True)

        iters = [base.walk(top_down=False) for _ in range(100)]
        for i in range(depth + 1):
            expected = (path, ["d"] if i else [], [])
            for it in iters:
                self.assertEqual(next(it), expected)
            path = path.parent

        iters = [base.walk(top_down=True) for _ in range(100)]
        path = base
        for i in range(depth + 1):
            expected = (path, ["d"] if i < depth else [], [])
            for it in iters:
                self.assertEqual(next(it), expected)
            path = path / "d"

    def test_walk_above_recursion_limit(self):
        recursion_limit = 40
        # directory_depth > recursion_limit
        directory_depth = recursion_limit + 10
        base = properpath.ProperPath(os_helper.TESTFN, "deep")
        path = properpath.ProperPath(base, *(["d"] * directory_depth))
        path.mkdir(parents=True)

        with set_recursion_limit(recursion_limit):
            list(base.walk())
            list(base.walk(top_down=False))


class PathTest(_BasePathTest, unittest.TestCase):
    cls = properpath.ProperPath

    def test_concrete_class(self):
        p = self.cls("a")
        self.assertIs(type(p), properpath.ProperPath)

    def test_unsupported_flavour(self):
        if os.name == "nt":
            self.assertRaises(NotImplementedError, pathlib.PosixPath)
        else:
            self.assertRaises(NotImplementedError, pathlib.WindowsPath)

    def test_glob_empty_pattern(self):
        p = self.cls()
        with self.assertRaisesRegex(ValueError, "Unacceptable pattern"):
            list(p.glob(""))


class PathSubclassTest(_BasePathTest, unittest.TestCase):
    class cls(properpath.ProperPath):
        pass

    # repr() roundtripping is not supported in custom subclass.
    test_repr_roundtrips = None


if __name__ == "__main__":
    unittest.main()
