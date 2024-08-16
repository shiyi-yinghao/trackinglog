import os
from os.path import join as pjoin

class LogConfig:
    __slots__ = ['_root_log_path', '_cache_log_path']

    def __init__(self, root_log_path='logs', cache_log_path=None):
        self._root_log_path = root_log_path
        self._cache_log_path = cache_log_path if cache_log_path is not None else pjoin(root_log_path, "cache")
        
    @property
    def root_log_path(self):
        return self._root_log_path
    
    @property
    def cache_log_path(self):
        return self._cache_log_path

    @root_log_path.setter
    def root_log_path(self, value):
        self._root_log_path = value
        if self._cache_log_path is None:
            self._cache_log_path = pjoin(value, "cache")
    
    @cache_log_path.setter
    def cache_log_path(self, value):
        self._cache_log_path = value

    def __repr__(self):
        return f"LogConfig(root_log_path={self.root_log_path})"
