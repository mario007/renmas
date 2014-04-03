
import os.path


class Loader:
    def __init__(self, directories=None):
        self._dirs = []
        if directories is not None:
            for d in directories:
                self.add_directory(d)

    def load(self, dirname, filename):
        """filename is just name of the file not full absolute file name.
        Loader will try to find that file in all registerd
        directories and if it finds one it will load file and return contents
        of the file otherwise None is returned.
        """
        for d in self._dirs:
            full_name = os.path.join(d, dirname, filename)
            if os.path.isfile(full_name):
                f = open(full_name)
                contents = f.read()
                f.close()
                return contents
        return None

    def add_directory(self, directory):
        if directory not in self._dirs:
            self._dirs.append(directory)

    def exist(self, dirname, filename):
        for d in self._dirs:
            full_name = os.path.join(d, dirname, filename)
            if os.path.isfile(full_name):
                return True
        return False
