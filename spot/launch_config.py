import yaml


class LaunchConfig(object):
    """A representation of the yaml config file used to launch an instance."""
    def __init__(self, path=None):
        self.arg_dict = {}
        if path is not None:
            self.load(path)

    def is_not_defined(self, attribute):
        """Checks too see if a given attribute has not been defined yet."""
        return attribute not in self.arg_dict

    def add(self, **kwargs):
        """Adds attributes to the config based on keyword arguments."""
        self._merge_new_dict(kwargs)

    def get(self, key):
        """Returns the value associated with a key in the config."""
        return self.arg_dict[key]

    def load(self, path):
        """Loads the contents the specified yaml config file into the object."""
        with open(path) as file:
            new_dict = yaml.load(file)
        self._merge_new_dict(new_dict)

    def _merge_new_dict(self, dict):
        """Merges a new dictionary into the internal config dictionary.
        WARNING: Overwrite behaviour is currently undefined.
        """
        # TODO: Define overwrite behaviour - also bad name, change this
        self.arg_dict = {**self.arg_dict, **dict}

    def kwargs(self):
        """Returns the config dictionary such that it can be unpacked and used to launch an instance."""
        return self.arg_dict


if __name__ == '__main__':
    cfg = LaunchConfig()
    cfg.load('gpu.yaml')
    print(cfg.kwargs())