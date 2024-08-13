import logging
import os
import types
from typing import Callable
from functools import wraps, update_wrapper, singledispatch
from .parameter_config import LogConfig

class LogManager:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance.config = LogConfig()
        return cls._instance
        
    def __init__(self):
        self.logger_dict={}

    def setup(self, root_log_path=None):
        assert self.check_root_log_path(root_log_path), f"Invalid Root Log Path Given: {root_log_path}"
        self.config.root_log_path = root_log_path
        self.create_cache_log()

    def check_root_log_path(self, root_log_path):
        if not root_log_path:
            return False
        try:
            os.makedirs(self.config.root_log_path, exist_ok=True)
        except Exception as e:
            print("Error during creating the folder.",e)
            return False
        return True

    def setup_check(self):
        if not hasattr(self, 'config') or not self.config.root_log_path:
            raise ValueError("Root log path must be set before using loggers.")
    
    def create_cache_log(self):
        logger=self.create_logger("__cache", folderpath=self.config.cache_log_path)
        self.logger_dict["__cache"]=logger
        

    def create_logger(self, logname, filename=None, folderpath=None, log_level=logging.DEBUG):
        self.setup_check()
        if not folderpath:
            folderpath = self.config.root_log_path
        if not filename:
            filename = f"{logname}.log"
        
        full_log_path = os.path.join(folderpath, filename)
        os.makedirs(folderpath, exist_ok=True)
        logger = logging.getLogger(logname)
        handler = logging.FileHandler(full_log_path)
        formatter = logging.Formatter('%(asctime)s-%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)
        
        self.logger_dict[logname] = logger
        return logger
    
    def get_logger(self, logname, filename=None, folderpath=None, log_level=logging.DEBUG):
        self.setup_check()
        if logname not in self.logger_dict:
            self.create_logger(logname, filename, folderpath, log_level)
        
        logger = self.logger_dict[logname]
        return logger
        
    def get_log(self, logname, filename=None, folderpath=None, log_level=logging.DEBUG):       
        self.setup_check()
        logger = self.get_logger(logname, filename=filename, folderpath=folderpath, log_level=log_level)

        @singledispatch
        def decorator(obj):
            raise NotImplementedError("Unsupported type")

        @decorator.register
        def _(cls: type):  # Class decorator
            original_init = cls.__init__
            def wrapped_init(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                self.log = logger
            
            update_wrapper(wrapped_init, original_init)
            cls.__init__ = wrapped_init
            return cls

        @decorator.register(types.FunctionType)
        def _(func):  # Function decorator
            @wraps(func)
            def wrapper(*args, **kwargs):
                kwargs['log'] = logger
                logger.debug(f'Starting function {func.__name__}')
                result = func(*args, **kwargs)
                logger.debug(f'Function {func.__name__} ended.')
                return result
            return wrapper
        
        return decorator