import logging
import os
from functools import wraps
from .parameter_config import LogConfig

class LogManager:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance.config = LogConfig()
        return cls._instance

    def setup(self, root_log_path=None):
        assert self.check_root_log_path(root_log_path), f"Invalid Root Log Path Given: {root_log_path}"
        self.config.root_log_path = root_log_path
        

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
        if not hasattr(self, 'root_log_path') or not self.root_log_path:
            raise ValueError("Root log path must be set before using loggers.")

    def create_logger(self, logname, filename=None, folderpath=None, log_level=logging.DEBUG):
        self.setup_check()
        if not folderpath:
            folderpath = self.root_log_path
        if not filename:
            filename = f"{logname}.log"
        
        full_log_path = os.path.join(folderpath, filename)
        logger = logging.getLogger(logname)
        handler = logging.FileHandler(full_log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)
        
        self.logger_dict[logname] = logger
        return logger

    def get_log(self, logname, filename=None, folderpath=None, log_level=logging.DEBUG, func=None):
        if logname not in self.logger_dict:
            self.create_logger(logname, filename, folderpath, log_level)
        
        logger = self.logger_dict[logname]
        
        if func is None:
            return logger
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['log'] = logger  # Inject the logger into the function's keyword arguments
            logger.debug(f'Starting function {func.__name__}')
            result = func(*args, **kwargs)
            logger.debug(f'Function {func.__name__} ended.')
            return result
        return wrapper

    def get_logger(self, logname):
        self.setup_check()
        if logname in self.logger_dict:
            return self.logger_dict[logname]
        else:
            raise ValueError(f"Logger named {logname} not found. Please create it first.")
