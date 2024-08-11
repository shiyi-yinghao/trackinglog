import os

class LogConfig:
    __slots__ = ['_root_log_path']

    def __init__(self, root_log_path='logs'):
        self._root_log_path = root_log_path

    @property
    def root_log_path(self):
        return self._root_log_path

    @root_log_path.setter
    def root_log_path(self, value):
        # You can add validation here if needed
        self._root_log_path = value

    def __repr__(self):
        return f"LogConfig(root_log_path={self.root_log_path})"
