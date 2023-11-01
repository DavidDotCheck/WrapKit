from functools import wraps
import os
from typing import Literal


class FileSystemObject:
    def is_file(self):
        return False
    
    def is_dir(self):
        return False
      

# a wrapper that makes sure that the directory still exists and prints a warning if it does not
def ensure_path_is(type: Literal["file", "dir"]):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if type == "file" and not os.path.isfile(self.path):
                raise FileNotFoundError(f"File {self.path} does not exist.")
            elif type == "dir" and not os.path.isdir(self.path):
                raise NotADirectoryError(f"Directory {self.path} does not exist.")
            return f(self, *args, **kwargs)

        return wrapper

    return decorator
