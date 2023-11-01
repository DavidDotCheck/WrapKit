# tests/test_example_module/test_example.py
# Author: DavidDotCheck <contact@hardt.ai>

import os
import sys
import threading
import time
from unittest.mock import patch
import pytest

from wrapkit.file_system import Directory
import tempfile as tf
from ._util import create_file, create_directory, delete_file, delete_directory
from os.path import join


# 1. Initialization:
#     - Test creating a Directory instance with a valid path.
#     - Test creating a Directory instance with a non-existent path and create set to True.
#     - Test creating a Directory instance with a non-existent path and create set to False.
#     - Test creating a Directory instance with a path that is a file.
#     - Test creating a Directory instance with a symbolic link as a path.
#     - Test creating a Directory instance with a symbolic link as a path and resolve_links set to True.

# 2. Properties:
#     - Test accessing the path, root, name, parent, exists, permissions, owner, group, and size properties.

# 3. Special methods:
#     - Test the __enter__, __exit__, __repr__, __str__, __add__, __radd__, __truediv__, __rtruediv__, __floordiv__, __rfloordiv__, __getitem__, __setitem__, __delitem__, __iter__, __len__, __contains__, __hash__, __eq__, and __ne__ methods.

# 4. set_path method:
#     - Test setting a new valid path.
#     - Test setting a new non-existent path.
#     - Test setting a path that is a file.
#     - Test setting a symbolic link as a path.
#     - Test setting a symbolic link as a path with resolve_links set to True.

# 5. delete method:
#     - Test deleting a directory that exists.
#     - Test deleting a directory that does not exist.
#     - Test deleting a directory with force set to True.

# 6. delete_contents method:
#     - Test deleting contents of a directory with various combinations of match, delete_hidden, recursive, dirs, and files parameters.
#     - Test deleting hidden files in non hidden directory, hidden files in hidden directory, non hidden files in hidden directory, non hidden files in non hidden directory
#     - Test deleting files, dirs, files and dirs
#     - Test deleting with match and no match

# 7. list method:
#     - Test listing contents of a directory with various combinations of match, recursive, hidden, dirs, and files parameters.

# 8. list_files method:
#     - Test listing files of a directory with various combinations of match, hidden, and recursive parameters.

# 9. write_file method:
#     - Test writing a file to the directory.

# 10. list_dirs method:
#     - Test listing directories of a directory with various combinations of match, hidden, and recursive parameters.

# 11. create method:
#     - Test creating a directory that does not exist.
#     - Test creating a directory that already exists.

# 12. create_dir method:
#     - Test creating a new directory within the directory.

# 13. move method:
#     - Test moving the directory to a new path.

# 14. create_copy method:
#     - Test creating a copy of the directory at a new path.

# 15. rename method:
#     - Test renaming the directory.

# 16. change_permissions method:
#     - Test changing the permissions of the directory.

# 17. change_owner method:
#     - Test changing the owner of the directory.

# 18. change_group method:
#     - Test changing the group of the directory.

# 19. temporary_directory context manager:
#     - Test creating a temporary directory.
#     - Test changing the path of a temporary directory.
#     - Test deleting a temporary directory.'


def create_dir_and_file(path, filename, content="some_text"):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, filename), "w") as f:
        f.write(content)


@pytest.fixture()
def setup_data():
    with tf.TemporaryDirectory() as real_dir, tf.TemporaryDirectory() as symlink_dir_target, tf.TemporaryDirectory() as symlink_dir_origin, tf.TemporaryDirectory() as file_symlink_dir, tf.TemporaryDirectory() as mixed_dir:
        create_dir_and_file(real_dir, "real_file")

        fake_dir = join(real_dir, "fake_dir")
        fake_file = join(fake_dir, "fake_file")

        # Create dir symlinks
        symlink_dir_target = tf.TemporaryDirectory().name
        create_directory(symlink_dir_target)
        symlink_dir_origin = tf.TemporaryDirectory().name
        os.symlink(symlink_dir_target, symlink_dir_origin)

        # Create file symlinks
        file_symlink_dir = tf.TemporaryDirectory().name
        create_directory(file_symlink_dir)
        symlink_file_target = join(file_symlink_dir, "symlink_file_target")
        symlink_file_origin = join(file_symlink_dir, "symlink_file_origin")
        create_file(symlink_file_target, "some_text")
        os.symlink(symlink_file_target, symlink_file_origin)

        # Create a directory with a lot of different files and directories
        files_templates = [
            [f"file_{i}.txt" for i in range(10)],
            [f"random_1sujuf7AS6{i}" for i in range(10)],
            [f"file_{i}" for i in range(10)],
            [f".hidden_file_{i}" for i in range(10)],
        ]

        dirs_templates = [
            [f"dir_{i}" for i in range(10)],
            [f"random_1suasxc7AS6{i}" for i in range(10)],
            [f".hidden_dir_{i}" for i in range(10)],
        ]

        filled_dirs_templates = [[f"filled_dir_{i}" for i in range(10)]]

        # Create files
        for templates in files_templates:
            for filename in templates:
                create_file(join(mixed_dir, filename), "some_text")

        for templates in dirs_templates:
            for i, dirname in enumerate(templates):
                path = join(mixed_dir, dirname)
                create_directory(path)

        for templates in filled_dirs_templates:
            for i, dirname in enumerate(templates):
                path = join(mixed_dir, dirname)
                create_dir_and_file(path, f"file_{i}.txt", "some_text")

        dir_data = {
            "real": real_dir,
            "fake": fake_dir,
            "symlink": symlink_dir_origin,
            "symlink_target": symlink_dir_target,
            "mixed": mixed_dir,
        }
        file_data = {
            "real": os.path.join(real_dir, "real_file"),
            "fake": fake_file,
            "symlink": symlink_file_origin,
            "symlink_target": symlink_file_target,
        }

        yield dir_data, file_data


def verify_directory(dir: Directory, path: str):
    assert dir.path == path
    assert dir.root == path.split(os.sep)[0]
    assert dir.name == os.path.basename(path)
    assert dir.parent == os.path.dirname(path)


@pytest.mark.parametrize(
    "type_key, dir_key, result_key, should_exist, expected_exception, create, resolve",
    [
        ("dir", "real", "real", True, None, False, False),
        ("dir", "real", "real", True, None, True, False),
        ("dir", "fake", "fake", False, None, False, False),
        ("dir", "fake", "fake", True, None, True, False),
        ("dir", "symlink", "symlink", False, ValueError, False, False),
        ("dir", "symlink", "symlink_target", True, None, False, True),
        ("dir", "symlink", "symlink_target", True, None, False, True),
        ("dir", "symlink", "symlink_target", True, None, True, True),
        ("file", "real", "real", False, NotADirectoryError, False, False),
        ("file", "real", "real", False, NotADirectoryError, True, False),
        ("file", "fake", "fake", False, None, False, False),
        ("file", "symlink", "symlink_target", False, ValueError, False, False),
        ("file", "symlink", "symlink_target", False, NotADirectoryError, False, True),
        ("file", "symlink", "symlink_target", False, NotADirectoryError, True, True),
    ],
)
def test_initialization_set_path(
    setup_data,
    type_key,
    dir_key,
    result_key,
    should_exist,
    expected_exception,
    create,
    resolve,
):
    dirPaths, filePaths = setup_data
    selected_path = dirPaths[dir_key] if type_key == "dir" else filePaths[dir_key]
    expected_path = dirPaths[result_key] if type_key == "dir" else filePaths[result_key]
    start_path = tf.TemporaryDirectory().name
    if expected_exception:
        with pytest.raises(expected_exception):
            dir = Directory(selected_path, create=create, resolve=resolve)
        with pytest.raises(expected_exception):
            dir = Directory(start_path, resolve=resolve)
            dir.set_path(selected_path, create=create)
    else:
        dir = Directory(selected_path, create=create, resolve=resolve)
        verify_directory(dir, expected_path)
        msg = (
            f"Directory should "
            + ("exist" if should_exist else "not exist")
            + " but + "
            + ("does not." if dir.exists else "does.")
        )
        assert dir.exists == should_exist, msg

        dir = Directory(start_path, resolve=resolve)
        dir.set_path(selected_path, create=create)
        verify_directory(dir, expected_path)
        assert dir.exists == should_exist, msg


def test_enter_exit(setup_data):
    dirPaths, filePaths = setup_data
    # Test __enter__ and __exit__
    dir_instance = Directory(dirPaths["real"])
    with dir_instance as d:
        assert d is dir_instance, "__enter__ should return self."


def test_repr_str(setup_data):
    dirPaths, filePaths = setup_data
    # Test __repr__ and __str__
    dir_instance = Directory(dirPaths["real"])
    expected_repr = f"Directory({dirPaths['real']})"
    assert (
        repr(dir_instance) == expected_repr
    ), f"__repr__ does not match {expected_repr}"
    assert str(dir_instance) == dirPaths["real"], f"__str__ does not match the path."


def test_add(setup_data):
    dirPaths, filePaths = setup_data
    # Test __add__
    dir_instance = Directory(dirPaths["real"])
    new_dir = dir_instance + "new_folder"
    assert new_dir.path == join(
        dirPaths["real"], "new_folder"
    ), f"__add__ didn't join the paths correctly."


def test_truediv(setup_data):
    dirPaths, filePaths = setup_data
    # Test __truediv__
    dir_instance = Directory(dirPaths["real"])
    dir_instance.set_path(dirPaths["real"])
    new_dir = dir_instance / "new_folder"
    assert new_dir.path == join(
        dirPaths["real"], "new_folder"
    ), f"__truediv__ didn't join the paths correctly."


def test_floordiv(setup_data):
    dirPaths, filePaths = setup_data
    # Test __floordiv__
    dir_instance = Directory(dirPaths["real"])
    dir_instance.set_path(dirPaths["real"])
    new_dir = dir_instance // "new_folder"
    assert new_dir.path == join(
        dirPaths["real"], "new_folder"
    ), f"__floordiv__ didn't join the paths correctly."


# TODO: Test __getitem__, __setitem__, and __delitem__ after implementing 'File' class
def test_getitem(setup_data):
    pass


def test_setitem(setup_data):
    pass


def test_delitem(setup_data):
    pass


def test_iter_len(setup_data):
    dirPaths, filePaths = setup_data
    # Test __iter__ and __len__
    dir_instance = Directory(dirPaths["real"])
    assert len(dir_instance) == 1, f"__len__ should be 1 but is {len(dir_instance)}"
    excpected = [filePaths["real"].split(os.sep)[-1]]
    assert (
        list(dir_instance) == excpected
    ), f"__iter__ should return {excpected} but returned {list(dir_instance)}"


def test_contains(setup_data):
    dirPaths, filePaths = setup_data
    # Test __contains__
    dir = Directory(dirPaths["real"])
    excpected = filePaths["real"].split(os.sep)[-1]
    assert excpected in dir, f"{excpected} should be in {dir}"
    assert "new_file" not in dir, f"new_file should not be in {dir}"


def test_hash(setup_data):
    dirPaths, filePaths = setup_data
    # Test __hash__
    dir_instance = Directory(dirPaths["real"])
    assert hash(dir_instance) == hash(
        dirPaths["real"]
    ), f"__hash__ should return the hash of the path."


def test_eq_ne(setup_data):
    dirPaths, filePaths = setup_data
    # Test __eq__ and __ne__
    dir_instance = Directory(dirPaths["real"])
    another_dir_instance = Directory(dirPaths["real"])

    assert dir_instance == another_dir_instance
    assert dir_instance == dirPaths["real"]
    assert dir_instance != dirPaths["fake"]


def test_delete(setup_data):
    dirPaths, filePaths = setup_data
    # Test deleting a directory that exists and is empty.
    tmp_path = join(dirPaths["real"], "tmp")
    dir = Directory(tmp_path, create=True)
    dir.delete()
    assert not dir.exists, "Directory should not exist when deleted."

    # Test deleting a directory that exists and is not empty.
    with pytest.raises(OSError):
        dir = Directory(tmp_path, create=True)

        create_file(join(tmp_path, "file"), "some_text")
        dir.delete()
    # Test deleting a directory that does not exist.
    dir = Directory(dirPaths["fake"])
    with pytest.raises(NotADirectoryError):
        dir.delete()

    # Test deleting a directory with force set to True.
    dir = Directory(tmp_path, create=True)
    create_file(join(tmp_path, "file"), "some_text")
    dir.delete(force=True)
    assert not dir.exists, "Directory should not exist when deleted."


# Parameters: match, delete_hidden, recursive, dirs, files
@pytest.mark.parametrize(
    "match, delete_hidden, recursive, dirs, files, deleted_dirs, deleted_files, force, exception",  # deleted_dirs & deleted_files are how many dirs and files should be deleted. spread: 10x file_*.txt files, 10x random_* files, 10x file_* files (no extensions), 10x .hidden_file_* files, 10x dir_* dirs, 10x random_* dirs, 10x .hidden_dir_* dirs, 10x filled_* dirs (including 1 file each). Total of 40 dirs and 50 files
    [
        # Test case 1: Delete all txt files (10)
        ("*.txt", False, False, False, True, 0, 10, False, None),
        # Test case 2: Delete all random_* files (10)
        ("random_*", False, False, False, True, 0, 10, False, None),
        # Test case 3: Delete all file_* files (with and without extension, 20 total)
        ("file_*", False, False, False, True, 0, 20, False, None),
        # Test case 4: Delete all .hidden_file_* files (10)
        (".hidden_file_*", True, False, False, True, 0, 10, False, None),
        # Test case 5: Delete all dirs (excluding hidden, 20 total). Expect OSError because dirs are not empty
        ("*", False, False, True, False, 0, 0, False, OSError),
        # Test case 6: Delete all random_* dirs (10)
        ("random_*", False, False, True, False, 10, 0, False, None),
        # Test case 7: Delete all dir_* dirs (10)
        ("dir_*", False, False, True, False, 10, 0, False, None),
        # Test case 8: Delete all .hidden_dir_* dirs (10)
        (".hidden_dir_*", True, False, True, False, 10, 0, False, None),
        # Test case 9: Delete all files and dirs recursively (including hidden and files in filled_* dirs, 90 total)
        ("*", True, True, True, True, 40, 50, False, None),
        # Test case 10: Delete all hidden files and dirs recursivel, (10x .hidden_file_* files, 10x .hidden_dir_* dirs, 20 total)
        (".*", True, True, True, True, 10, 10, False, None),
        # Test case 11: Delete all files (including hidden, 40 total)
        ("*", True, False, False, True, 0, 40, False, None),
        # Test case 12: Delete all dirs (including hidden, 40 total, 10 files in filled_* dirs)
        ("*", True, False, True, False, 40, 10, True, None),
        # Test case 13: Delete all files and dirs (including hidden, 0 total)
        ("*", True, False, True, True, 0, 0, False, OSError),
        # Test case 14: Delete all files (including hidden) recursively (50 total)
        ("*", True, True, False, True, 0, 50, False, None),
        # Test case 15: Delete all dirs (including hidden) recursively, error because files are not deleted (0 total)
        ("*", True, True, True, False, 0, 0, False, OSError),
        # Test case 16: Delete all files and dirs (including hidden) recursively (80 total)
        ("*", True, True, True, True, 40, 50, False, None),
        # Test case 17: Attempt to delete non-empty dirs without force
        ("filled_*", False, False, True, False, 0, 0, False, OSError),
        # Test case 18: Delete non-empty dirs with force
        ("dir_*", False, False, True, False, 10, 0, True, None),
        # Test case 19: Attempt to delete hidden dirs without delete_hidden flag
        (".hidden_dir_*", False, False, True, False, 0, 0, False, None),
        # Test case 21: Attempt to delete all (including non-empty dirs) without force
        ("*", False, False, True, True, 0, 0, False, OSError),
        # Test case 22: Delete all with force, non-recursive (excludes hidden)
        ("*", False, False, True, True, 30, 40, True, None),
        # Test case 23: Delete all with force, recursively (includes hidden)
        ("*", True, True, True, True, 40, 50, True, None),
    ],
)
def test_delete_contents(
    setup_data,
    match,
    delete_hidden,
    recursive,
    dirs,
    files,
    deleted_dirs,
    deleted_files,
    force,
    exception,
):
    dirPaths, filePaths = setup_data
    dir = Directory(dirPaths["mixed"])

    def count_files_and_dirs():
        file_count = len(
            dir.list(match="*", recursive=True, files=True, dirs=False, hidden=True)[1]
        )
        dir_count = len(
            dir.list(match="*", recursive=True, files=False, dirs=True, hidden=True)[0]
        )
        return file_count, dir_count

    file_count, dir_count = count_files_and_dirs()

    args = {
        "match": match,
        "delete_hidden": delete_hidden,
        "recursive": recursive,
        "dirs": dirs,
        "files": files,
        "force": force,
    }

    if exception:
        with pytest.raises(exception):
            dir.delete_contents(**args)
    else:
        dir.delete_contents(**args)

    file_count_after, dir_count_after = count_files_and_dirs()
    expected_file_count = (
        file_count - deleted_files if not deleted_files is None else None
    )
    expected_dir_count = dir_count - deleted_dirs if not deleted_dirs is None else None
    assert (
        expected_dir_count is None or file_count_after == expected_file_count
    ), f"File count should be {expected_file_count} but is {file_count_after}"

    assert (
        expected_dir_count is None or dir_count_after == expected_dir_count
    ), f"Dir count should be {expected_dir_count} but is {dir_count_after}"


@pytest.mark.parametrize(
    "match, hidden, recursive, include_dirs, include_files, topdown, exception, expected_dirs, expected_files",
    [
        # Test case 1: List all txt files (10)
        ("*.txt", False, False, False, True, True, None, 0, 10),
        # Test case 2: List all random_* files (10)
        ("random_*", False, False, False, True, True, None, 0, 10),
        # Test case 3: List all file_* files (with and without extension, 20)
        ("file_*", False, False, False, True, True, None, 0, 20),
        # Test case 4: List all .hidden_file_* files (10)
        (".hidden_file_*", True, False, False, True, True, None, 0, 10),
        # Test case 5: List all dirs (excluding hidden, 30).
        ("*", False, False, True, False, True, None, 30, 0),
        # Test case 6: List all random_* dirs (10)
        ("random_*", False, False, True, False, True, None, 10, 0),
        # Test case 7: List all dir_* dirs (10)
        ("dir_*", False, False, True, False, True, None, 10, 0),
        # Test case 8: List all .hidden_dir_* dirs (10)
        (".hidden_dir_*", True, False, True, False, True, None, 10, 0),
        # Test case 9: List all files and dirs recursively topdown (90)
        ("*", True, True, True, True, True, None, 40, 50),
        # Test case 10: List all hidden files and dirs recursively, (10x .hidden_file_* files, 10x .hidden_dir_* dirs, 20)
        (".*", True, True, True, True, True, None, 10, 10),
        # Test case 11: List all files (including hidden, 40)
        ("*", True, False, False, True, True, None, 0, 40),
        # Test case 12: List all dirs (including hidden, 40)
        ("*", True, False, True, False, True, None, 40, 0),
        # Test case 13: List all files and dirs recursively (90)
        ("*", True, True, True, True, False, None, 40, 50),
    ],
)
def test_list(
    setup_data,
    match,
    hidden,
    recursive,
    include_dirs,
    include_files,
    topdown,
    exception,
    expected_dirs,
    expected_files,
):
    dirPaths, filePaths = setup_data
    dir = Directory(dirPaths["mixed"])

    args = {
        "match": match,
        "hidden": hidden,
        "recursive": recursive,
        "dirs": include_dirs,
        "files": include_files,
        "topdown": topdown,
    }

    def count(dirs, files):
        return len(dirs), len(files)

    if exception:
        with pytest.raises(exception):
            dir.list(**args)

    else:
        dirs, files = dir.list(**args)
    dir_count, file_count = count(dirs, files)

    assert (
        dir_count == expected_dirs
    ), f"Expected {expected_dirs} dirs but got {dir_count}"

    assert (
        file_count == expected_files
    ), f"Expected {expected_files} files but got {file_count}"

    if (
        recursive
        and "filled_dir_0" in dirs
        and (fdf := os.sep.join(["filled_dir_0", "file_0.txt"])) in files
    ):
        filled_dir_index = dirs.index("filled_dir_0")
        filled_dir_file_index = files.index(fdf)
        if topdown:
            assert (
                filled_dir_index < filled_dir_file_index
            ), f"Expected {fdf} to be after {filled_dir_index} but it is {filled_dir_file_index}"
        else:
            assert (
                filled_dir_index > filled_dir_file_index
            ), f"Expected {fdf} to be before {filled_dir_index} but it is {filled_dir_file_index}"

    list_dirs = (
        dir.list_dirs(match=match, hidden=hidden, recursive=recursive)
        if include_dirs
        else []
    )
    list_files = (
        dir.list_files(match=match, hidden=hidden, recursive=recursive)
        if include_files
        else []
    )
    assert file_count == len(
        list_files
    ), '"list_files" should return the same number of files as "list"'

    assert dir_count == len(
        list_dirs
    ), '"list_dirs" should return the same number of dirs as "list"'


def test_create(setup_data):
    dirPaths, filePaths = setup_data
    # Test creating a directory that does not exist.
    dir = Directory(join(dirPaths["real"], "new_dir"))
    assert not dir.exists, "Directory should not exist before creation."
    dir.create()
    assert dir.exists, "Directory should exist after creation."

    # Test creating a directory that already exists without exist_ok set to True.
    with pytest.raises(OSError):
        dir.create()

    # Test creating a directory that already exists with exist_ok set to True.
    dir.create(exist_ok=True)
    assert dir.exists, "Directory should exist after creation."


def test_create_dir(setup_data):
    dirPaths, filePaths = setup_data
    # Test creating a new directory within the directory.
    dir = Directory(dirPaths["real"])
    new_dir = dir.create_dir("new_dir")
    assert new_dir.exists, "Directory should exist after creation."
    assert new_dir.path == join(
        dirPaths["real"], "new_dir"
    ), "Directory path should be correct."
    assert dir["new_dir"] == new_dir, "Directory should be accessible by name."


def test_move(setup_data):
    dirPaths, filePaths = setup_data
    # Test moving the directory to a new path.
    path = join(dirPaths["real"], "new_dir")
    new_path = join(dirPaths["fake"], "new_dir")
    dir = Directory(path)
    dir.create()
    dir.move(new_path)
    assert dir.path == new_path, "Directory path should be correct."
    assert dir.exists, "Directory should exist at new path."
    assert not os.path.exists(path), "Directory should not exist at old path."


def test_create_copy(setup_data):
    dirPaths, filePaths = setup_data
    # Test creating a copy of the directory at a new path.
    path = join(dirPaths["real"], "new_dir")
    new_path = join(dirPaths["fake"], "new_dir")
    dir = Directory(path)
    dir.create()
    dir.create_copy(new_path)
    assert dir.path == path, "Directory path should be correct."
    assert dir.exists, "Directory should exist at old path."
    assert os.path.exists(new_path), "Directory should exist at new path."


def test_rename(setup_data):
    dirPaths, filePaths = setup_data
    # Test renaming the directory.
    path = join(dirPaths["real"], "new_dir")
    dir = Directory(path)
    dir.create()
    dir.rename("new_name")
    assert dir.path == join(
        dirPaths["real"], "new_name"
    ), "Directory path should be correct."
    assert dir.exists, "Directory should exist at new path."
    assert not os.path.exists(path), "Directory should not exist at old path."


def test_temporary_directory(setup_data):
    dirPaths, filePaths = setup_data
    # Test creating a temporary directory without a path.
    with Directory.temporary_directory() as dir:
        assert dir.exists, "Directory should exist."
        assert "tmp" in dir.path, "Directory path should contain 'tmp'."

    # Test creating a temporary directory with a path that exists.
    with pytest.raises(OSError):
        with Directory.temporary_directory(dirPaths["real"]) as dir:
            pytest.fail("Should not be able to create a temporary directory.")

    # Test creating a temporary directory with a path that does not exist.
    with Directory.temporary_directory(join(dirPaths["real"], "new_dir")) as dir:
        assert dir.exists, "Directory should exist."
        assert (
            join(dirPaths["real"], "new_dir") == dir.path
        ), "Directory path should be correct."

    # Test changing the path of a temporary directory.
    with pytest.raises(OSError):
        with Directory.temporary_directory() as dir:
            dir.set_path(dirPaths["real"])

    # Test deleting and creating a temporary directory.
    with Directory.temporary_directory() as dir:
        path = dir.path
        assert dir.exists, "Directory should exist."
        dir.delete()
        assert not os.path.exists(path), "Directory should not exist."
        dir.create()
        assert dir.exists, "Directory should exist."
        assert path == dir.path, "Directory path should be correct."


def test_properties_ponix(setup_data):
    dirPaths, _ = setup_data
    # Test accessing the path, root, name, parent, exists, permissions, owner, group, and size properties.
    dir = Directory(dirPaths["real"])
    verify_directory(dir, dirPaths["real"])
    assert dir.size == 9
    if os.name == "nt":
        with pytest.raises(NotImplementedError):
            dir.permissions
        with pytest.raises(NotImplementedError):
            dir.owner
        with pytest.raises(NotImplementedError):
            dir.group
    else:
        assert dir.exists, "Directory should exist but does not."
        assert dir.permissions == oct(os.stat(dirPaths["real"]).st_mode)[-3:]
        assert dir.owner == os.stat(dirPaths["real"]).st_uid
        assert dir.group == os.stat(dirPaths["real"]).st_gid


def test_change_permissions(setup_data):
    with patch("wrapkit.file_system.directory.os.chmod") as mock_chmod:
        dirPaths, filePaths = setup_data
        path = join(dirPaths["real"], "new_dir")
        dir = Directory(path)
        dir.create()

        if os.name == "nt":
            with pytest.raises(NotImplementedError):
                dir.change_permissions("755")
        else:
            dir.change_permissions("755")
            mock_chmod.assert_called_with(path, 0o755)
            dir.change_permissions("777")
            mock_chmod.assert_called_with(path, 0o777)


def test_change_owner(setup_data):
    dirPaths, filePaths = setup_data
    path = join(dirPaths["real"], "new_dir")
    dir = Directory(path, create=True)

    if os.name == "nt":
        with pytest.raises(NotImplementedError):
            dir.change_owner("root", "root")
    else:
        with patch("wrapkit.file_system.directory.os.chown") as mock_chown:
            dir.change_owner("root", "root")
            mock_chown.assert_called_with(path, 0, 0)
