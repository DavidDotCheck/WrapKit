import os
import shutil


def create_file(file_path, content=""):
    """
    Creates a file at the specified path with optional content.

    Args:
      file_path (str): The path where the file should be created.
      content (str, optional): The content to write to the file. Defaults to None.
    """
    try:
        with open(file_path, "w") as f:
            f.write(content)
    except FileExistsError as e:
        print(f"File {file_path} already exists")
        raise e  # re-raise the exception


def create_directory(dir_path):
    """
    Creates a directory at the specified path.

    Args:
      dir_path (str): The path where the directory should be created.
    """
    os.makedirs(dir_path)


def delete_file(file_path):
    """
    Deletes a file at the specified path.

    Args:
      file_path (str): The path of the file to delete.
    """
    os.remove(file_path)


def delete_directory(dir_path):
    """
    Deletes a directory and all its contents at the specified path.

    Args:
      dir_path (str): The path of the directory to delete.
    """
    shutil.rmtree(dir_path)
