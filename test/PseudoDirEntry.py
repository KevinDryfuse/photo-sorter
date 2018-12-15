class PseudoDirEntry:
    def __init__(self, name, path, is_dir, stat):
        self.name = name
        self.path = path
        self._is_dir = is_dir
        self._stat = stat

    def is_dir(self):
        return self._is_dir

    def stat(self):
        return self._stat
