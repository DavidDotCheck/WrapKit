# wrapkit/file_system/file.py

class File:
    def __init__(self, path: str, create=False, resolve_links=False):
        self.resolve = resolve_links
        self.path = path
    