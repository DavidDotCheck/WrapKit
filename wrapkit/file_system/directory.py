# wrapkit/file_system/directory.py
from abc import abstractmethod
import os
import shutil
import fnmatch
import tempfile as tf

from contextlib import contextmanager
from typing import Optional, Union
from ._util import FileSystemObject, ensure_path_is
from .file import File

if os.name != "nt":
    import pwd
    import grp


class Directory(FileSystemObject):
    def __init__(self, path: str, create=False, resolve=False):
        self.resolve = resolve

        self.set_path(path, create)

    # override
    @abstractmethod
    def is_dir(self):
        return True

    @property
    def path(self):
        return self._path

    # returns drive letter on windows and root on unix
    @property
    def root(self):
        return self.parts[0]

    @property
    def name(self):
        return self.parts[-1]

    @property
    def parent(self):
        return os.sep.join(self.parts[:-1])

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    @ensure_path_is("dir")
    def permissions(self):
        if os.name == "nt":
            raise NotImplementedError(
                "Getting permissions is not supported on Windows."
            )
        else:
            st = os.stat(self.path)
            permissions = oct(st.st_mode)[-3:]
            return permissions

    @property
    @ensure_path_is("dir")
    def owner(self):
        if os.name == "nt":
            raise NotImplementedError("Getting owner is not supported on Windows.")
        else:
            return os.stat(self.path).st_uid

    @property
    @ensure_path_is("dir")
    def group(self):
        if os.name == "nt":
            raise NotImplementedError("Getting group is not supported on Windows.")
        else:
            return os.stat(self.path).st_gid

    @property
    @ensure_path_is("dir")
    def size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __repr__(self):
        return f"Directory({self.path})"

    def __str__(self):
        return self.path

    def __add__(self, other):
        new_path = os.path.join(self.path, other)
        return Directory(new_path)

    def __truediv__(self, other):
        new_path = os.path.join(self.path, other)
        return Directory(new_path)

    def __floordiv__(self, other):
        new_path = os.path.join(self.path, other)
        return Directory(new_path)

    def __getitem__(self, name):
        abs_path = os.path.join(self.path, name)
        if os.path.isdir(abs_path):
            return Directory(abs_path)
        elif os.path.isfile(abs_path):
            return File(abs_path)
        if os.path.islink(abs_path) and self.resolve:
            return Directory(abs_path, resolve=True)
        else:
            raise KeyError(f"Could not find file or directory {abs_path}")

    def __setitem__(self, name, value):
        if isinstance(value, Directory):
            value.rename(name)
        elif isinstance(value, File):
            value.rename(name)
        else:
            raise ValueError(
                "Value must be of type 'Directory' or 'File', not "
                f"{type(value).__name__}"
            )

    def __delitem__(self, name):
        os.remove(os.path.join(self.path, name))

    def __iter__(self):
        return iter([item for lst in self.list() for item in lst])

    def __len__(self):
        return len([item for lst in self.list() for item in lst])

    def __contains__(self, item):
        return item in [item for lst in self.list() for item in lst]

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return (
            self.path == other.path
            if isinstance(other, Directory)
            else self.path == other
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_path(self, new_path: str, create=False):
        if os.path.islink(new_path):
            if self.resolve:
                new_path = os.path.realpath(new_path)
            else:
                raise ValueError(
                    "Path is a symbolic link. Use resolve=True to resolve symbolic links or use 'Link' class."
                )

        if os.path.isfile(new_path):
            raise NotADirectoryError("Path is a file. Use 'File' class instead.")
        self._path = new_path.replace("/", os.sep).replace("\\", os.sep)
        if create and not os.path.exists(self._path):
            os.makedirs(self._path, exist_ok=True)
        self.parts = self._path.split(os.sep)

    @ensure_path_is("dir")
    def delete(self, force=False):
        try:
            if force:
                shutil.rmtree(self.path)
            else:
                os.rmdir(self.path)
        except OSError as e:
            raise

    @ensure_path_is("dir")
    def delete_contents(
        self,
        match="*",
        delete_hidden=False,
        recursive=False,
        dirs=True,
        files=True,
        force=False,
        prescan=True,
        dry_run=False,
    ):
        """Deletes the contents of the directory.

        Args:
            match (str, optional): A fnmatch wildcard to filter results by. Defaults to "*".
            delete_hidden (bool, optional): whether or not to delete hidden directories. Defaults to False.
            recursive (bool, optional): Will delete files and directories recursively. When deleting dirs but not files, will raise an error if a directory is not empty. Use force=True for this case instead. Defaults to False.
            dirs (bool, optional): Whether or not to delete directories. Defaults to True.
            files (bool, optional): Whether or not to delete files. Defaults to True.
            force (bool, optional): Attempt to delete files and directories even if they are locked, filled, or in use. Defaults to False.
            prescan (bool, optional): Run a series of pre-scans that aim to detect issues in the configuration or file system. Performance intensive. Defaults to True.
            dry_run (bool, optional): Return a list of Directories and Files instead of deleting. Defaults to False.

        Raises:
            OSError: Directory is not empty and neither force nor recursive is True.
            OSError: File is locked or in use and force is False.

        Returns:
            Tuple[List[Directory], List[File]]: If dry_run is True, returns a tuple with the first element being a list of Directory objects and the second a list of File objects that would be deleted. Otherwise, returns None.
        """
        dirs_list, files_list = self.list(
            match=match,
            hidden=delete_hidden,
            recursive=recursive,
            dirs=dirs,
            files=files,
            topdown=False,
        )

        if prescan:
            if not (force or (recursive and files)):
                filled_dirs = self.get_filled_dirs()
                for filled_dir in filled_dirs:
                    if filled_dir in dirs_list:
                        raise OSError(
                            f"Directory {filled_dir} is not empty. Use force=True or recursive=True to delete it."
                        )
            if not force:
                for file_path in files_list:
                    if not Directory._file_deletable(
                        os.path.join(self.path, file_path)
                    ):
                        raise OSError(
                            f"File {file_path} is locked or in use. Use force=True to attempt to delete it anyway."
                        )

        if dry_run:
            return [Directory(os.path.join(self.path, d)) for d in dirs_list], [
                File(os.path.join(self.path, f)) for f in files_list
            ]

        deleted_items = []
        if files:
            for file_path in files_list:
                full_path = os.path.join(self.path, file_path)
                try:
                    os.remove(full_path)
                    deleted_items.append(File(full_path))
                except OSError as e:
                    if force:
                        pass  # Optionally log the error
                    else:
                        raise  # Re-raise the exception if not forcing

        if dirs:
            for dir_path in dirs_list:
                full_path = os.path.join(self.path, dir_path)
                try:
                    if force:
                        shutil.rmtree(full_path)
                    else:
                        os.rmdir(full_path)
                    deleted_items.append(Directory(full_path))
                except OSError as e:
                    if force:
                        pass  # Optionally log the error
                    else:
                        raise  # Re-raise the exception if not forcing

        return deleted_items

    @staticmethod
    def _file_deletable(file_path):
        if not os.access(file_path, os.W_OK):
            return False  # No write permission
        try:
            with open(file_path, "a"):
                pass
            return True
        except IOError:
            return False  # File is likely locked or in use

    @ensure_path_is("dir")
    def list(
        self,
        match="*",
        recursive=False,
        hidden=False,
        dirs=True,
        files=True,
        topdown=True,
    ):
        files_list = []
        dirs_list = []

        if recursive:
            for root, dirnames, filenames in os.walk(self.path, topdown=topdown):
                if dirs:
                    dirs_list.extend(
                        [
                            os.path.relpath(os.path.join(root, d), self.path)
                            for d in dirnames
                        ]
                    )
                if files:
                    files_list.extend(
                        [
                            os.path.relpath(os.path.join(root, f), self.path)
                            for f in filenames
                        ]
                    )
        else:
            for entry in os.listdir(self.path):
                full_path = os.path.join(self.path, entry)
                if os.path.isfile(full_path) and files:
                    files_list.append(entry)
                elif os.path.isdir(full_path) and dirs:
                    dirs_list.append(entry)
        if not hidden:
            files_list = [
                f for f in files_list if not os.path.basename(f).startswith(".")
            ]
            dirs_list = [
                d for d in dirs_list if not os.path.basename(d).startswith(".")
            ]

        if match != "*":
            files_list = [
                f for f in files_list if fnmatch.fnmatch(os.path.basename(f), match)
            ]
            dirs_list = [
                d for d in dirs_list if fnmatch.fnmatch(os.path.basename(d), match)
            ]

        return dirs_list, files_list

    @ensure_path_is("dir")
    def list_files(self, match="*", hidden=False, recursive=False):
        return self.list(
            match, hidden=hidden, recursive=recursive, dirs=False, files=True
        )[1]

    @ensure_path_is("dir")
    def list_dirs(self, match="*", hidden=False, recursive=False):
        return self.list(
            match=match, hidden=hidden, recursive=recursive, dirs=True, files=False
        )[0]

    @ensure_path_is("dir")
    def get_filled_dirs(self, match="*", hidden=False):
        filled_dirs = []

        for entry in os.listdir(self.path):
            full_path = os.path.join(self.path, entry)

            # Skip hidden files/directories if hidden=False
            if not hidden and entry.startswith("."):
                continue

            # Check if the entry is a directory and matches the match pattern
            if os.path.isdir(full_path) and fnmatch.fnmatch(entry, match):
                # Check if the directory is not empty
                if os.listdir(full_path):
                    filled_dirs.append(entry)

        return filled_dirs

    @ensure_path_is("dir")
    def write_file(self, file: File):
        if os.path.isabs(file.path):
            raise ValueError("File path is absolute, cannot write to directory.")
        else:
            file.path = os.path.join(self.path, file.path)
            file.write()

    def create(self, exist_ok=False):
        os.makedirs(self.path, exist_ok=exist_ok)

    @ensure_path_is("dir")
    def create_dir(self, name: str):
        new_dir = Directory(os.path.join(self.path, name), create=True)
        return new_dir

    @ensure_path_is("dir")
    def move(self, new_path: str):
        shutil.move(self.path, new_path)
        self.set_path(new_path)

    @ensure_path_is("dir")
    def create_copy(self, new_path: str):
        shutil.copytree(self.path, new_path)
        return Directory(new_path)

    @ensure_path_is("dir")
    def rename(self, new_name: str):
        self.move(os.path.join(self.parent, new_name))
        self.set_path(os.path.join(self.parent, new_name))

    @ensure_path_is("dir")
    def change_permissions(self, mode: Union[int, str]):
        if os.name == "nt":
            raise NotImplementedError(
                "Changing permissions is not supported on Windows."
            )
        else:
            if isinstance(mode, str):
                mode = int(mode, 8)
            os.chmod(self.path, mode)

    @ensure_path_is("dir")
    def change_owner(self, owner: str, group: Optional[str] = None):
        if os.name == "nt":
            raise NotImplementedError("Changing owner is not supported on Windows.")
        else:
            # Get the uid and gid from the username and group name
            uid = pwd.getpwnam(owner).pw_uid
            gid = grp.getgrnam(group).gr_gid

            # Change the owner and group of the directory
            os.chown(self.path, uid, gid)

    @staticmethod
    @contextmanager
    def temporary_directory(path: Optional[str] = None, exist_ok=False):
        if path and os.path.exists(path) and not exist_ok:
            raise OSError(
                "Path already exists. Using an existing directory will delete it and all of its contents. Use exist_ok=True to allow this."
            )

        if path is None:
            path = tf.mkdtemp()

        dir = Directory(path, create=True)

        def raise_(*args, **kwargs):
            raise OSError("Cannot change path of temporary directory.")

        dir.set_path = raise_

        try:
            yield dir
        finally:
            dir.delete_contents(
                match="*", force=True, recursive=True, delete_hidden=True
            )
            dir.delete(force=True)
