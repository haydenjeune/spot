import yaml


class LaunchConfig(object):
    def __init__(self, path=None):
        self.arg_dict = {}

        if path is not None:
            self.load(path)

    def load(self, path):
        with open(path) as file:
            new_dict = yaml.load(file)
        self._merge_new_dict(new_dict)

    def _merge_new_dict(self, dict):
        self.arg_dict = {**self.arg_dict, **dict}

    def kwargs(self):
        return self.arg_dict


if __name__ == '__main__':
    cfg = LaunchConfig()
    cfg.load('gpu.yaml')
    print(cfg.kwargs())