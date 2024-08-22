import logging
import os
import types
import atexit
import datetime
import inspect
import time
import traceback
import psutil
import sys
import io
import pandas as pd
from line_profiler import LineProfiler
from typing import Callable
from functools import wraps, update_wrapper, singledispatch
from contextlib import redirect_stdout
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
        
    def setup_check(func):
        def decorator(self, *args, **kwargs):
            if not hasattr(self, 'config') or not self.config.root_log_path:
                raise ValueError("Root log path must be set before using loggers.")
            return func(self, *args, **kwargs)
        return decorator
       
    @staticmethod
    def get_log_string(*args, **kwargs):
            modified_args = []
            for arg in args:
                if isinstance(arg, pd.DataFrame):
                    # Convert DataFrame to string with added lines
                    spliter="\n--------------------------------------\n"
                    df_str =  spliter + arg.to_string(max_rows=kwargs.get("max_rows", 10), max_cols=kwargs.get("max_cols", 10), max_colwidth=kwargs.get("max_colwidth", 35), show_dimensions=True) + spliter
                    modified_args.append(df_str)
                elif isinstance(arg, dict):
                    spliter="\n- - - - - - - - - - - - - - - - - - - \n"
                    rows = []
                    for k, v in arg.items():
                        rows.append({'key': k, 'value': v})

                    df_str = spliter + pd.DataFrame(rows).to_string(max_rows=kwargs.get("max_rows", 10), max_cols=kwargs.get("max_cols", 10), max_colwidth=kwargs.get("max_colwidth", 35), show_dimensions=True) + spliter
                    modified_args.append(df_str)
                elif isinstance(arg, float):
                    modified_args.append("{:.6f}".format(arg).rstrip('0'))
                else:
                    modified_args.append(str(arg))

            msg = ' '.join(modified_args)
            return msg

    def cache_log_cleaner(self, days=7):
        self.config.cache_log_path
        pass

    def create_cache_log(self):
        self.cache_log_cleaner()
        self.create_logger("__cache", folderpath=self.config.cache_log_path)
        
    @setup_check
    def create_logger(self, logname, filename=None, folderpath=None, log_level=logging.DEBUG, timestamp=True, formart_align=True):
        if not folderpath:
            folderpath = self.config.root_log_path
        if not filename:
            filename = logname
        else:
            filename = os.path.splitext(filename)[0]
        
        time_stamp=datetime.datetime.now().strftime("%y%m%d_%H%M%S")

        if timestamp:
            filename = f"{filename}_{time_stamp}.log"
        else:
            filename = f"{filename}.log"
        
        full_log_path = os.path.join(folderpath, filename)
        os.makedirs(folderpath, exist_ok=True)
        logger = logging.getLogger(logname)
        handler = logging.FileHandler(full_log_path)
        if formart_align:
            formatter = logging.Formatter('%(asctime)s-%(levelname)-8s-%(caller_func_name)-10s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        else:
            formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(caller_func_name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)

        def split_kwargs(**kwargs):
            log_kwargs = {key[5:]: value for key, value in kwargs.items() if key.startswith('_log_')}
            if "verbose" in kwargs:
                log_kwargs["verbose"]=kwargs["verbose"]
            other_kwargs = {key: value for key, value in kwargs.items() if not key.startswith('_log_') and key!="verbose"}
            return log_kwargs, other_kwargs
    
        def print_and_log(log_method, default_verbose=True):
            @wraps(log_method)
            def wrapper(*args, **kwargs):
                log_kwargs, remaining_kwargs = split_kwargs(**kwargs)
                system_msg=log_kwargs.get("system_msg", None)
                func_name = inspect.stack()[1].function if system_msg is None else system_msg
                msg = LogManager.get_log_string(*args, **log_kwargs)
                log_method(msg, extra={'caller_func_name': func_name}, **remaining_kwargs)
                if log_kwargs.get("verbose", default_verbose):
                    print(msg)
                if log_kwargs.get("notify", False):
                    # Place holder for email notification/kafka message sending
                    pass 

            return wrapper

        # Decorate existing logger methods
        logging_methods = ['info', 'debug', 'warning', 'error', 'critical']
        for method in logging_methods:
            setattr(logger, f'p{method}', print_and_log(getattr(logger, method), default_verbose=True))
            setattr(logger, method, print_and_log(getattr(logger, method), default_verbose=False))

        self.logger_dict[logname] = logger
        
        atexit.register(LogManager.close_log, logger, handler) 
    
    @setup_check
    def get_logger(self, logname, filename=None, folderpath=None, log_level=logging.DEBUG):
        if logname not in self.logger_dict:
            self.create_logger(logname, filename, folderpath, log_level)
        
        logger = self.logger_dict[logname]
        return logger

    @staticmethod
    def close_log(logger, file_handler):
        try:
            file_handler.close()
            logger.removeHandler(file_handler)
        except Exception:
            pass

        

    @setup_check    
    def get_log(self, logname, filename=None, folderpath=None, log_level=logging.DEBUG, verbose=0, enable_profiling="function", print2log=False):
        logger = self.get_logger(logname, filename=filename, folderpath=folderpath, log_level=log_level)

        def trace_error_msg():
            traceback_str = traceback.format_exc()
            lines = traceback_str.split('\n')
            filtered_lines = [line for i, line in enumerate(lines) if "log_manager" not in line \
                    and (i == 0 or "log_manager" not in lines[i - 1])]
            return '\n'.join(filtered_lines)
        
        class CapturePrints:
            """A context manager to capture print statements and handle exceptions."""
            def __init__(self):
                self._original_stdout = None
                self._stringio = None
                self.exception = None

            def __enter__(self):
                self._original_stdout = sys.stdout  # Keep track of the original stdout
                self._stringio = io.StringIO()      # Create a StringIO buffer to capture output
                sys.stdout = self._stringio         # Replace the standard output
                return self._stringio

            def __exit__(self, exc_type, exc_value, traceback_info):
                sys.stdout = self._original_stdout  # Restore the original stdout
                if exc_type is not None:
                    # Capture the exception details
                    self.exception = (exc_type, exc_value, traceback_info)
                    return False  # Propagate the exception after logging it
                return True
            
        def manage_profiling(func, args, kwargs, profiling_type=None, print2log=False):
            if profiling_type == "line":
                profiler = LineProfiler()
                profiler.add_function(func)
                profiler.enable()
            elif profiling_type in ["function", "func"]:
                start_time = time.time()
                process = psutil.Process()
                cpu_before = process.cpu_percent(interval=None)
                memory_before = process.memory_info().rss
            
            if print2log:
                with CapturePrints() as captured:
                    result = func(*args, **kwargs)
                    captured_print = captured.getvalue()
                    logger.pinfo(captured_print, verbose=verbose, _log_system_msg=func.__name__)
            else:
                result = func(*args, **kwargs)

            if profiling_type == "line":
                profiler.disable()
                profiling_info = io.StringIO()
                profiler.print_stats(stream=profiling_info)
                profiling_info = profiling_info.getvalue()
                logger.info("LineProfiler Stats:\n"+profiling_info, _log_system_msg="<LOG_MANAGER>")

            elif profiling_type in ["function", "func"]:
                cpu_after = process.cpu_percent(interval=None)
                memory_after = process.memory_info().rss
                end_time = time.time()
                time_taken = end_time - start_time     
                logger.info(f"Time Taken: ** {func.__name__} ** took {time_taken//3600:.0f} hr {time_taken//60:.0f} min {time_taken % 60:.2f} sec", _log_system_msg="<LOG_MANAGER>")
                logger.info(f"Resource usage: CPU {cpu_after - cpu_before}%, Memory {((memory_after - memory_before) / (1024 * 1024)):.2f} MB", _log_system_msg="<LOG_MANAGER>")
            return result

        @singledispatch
        def decorator(obj):
            raise NotImplementedError("Unsupported type")

        @decorator.register
        def _(cls: type):  # Class decorator
            original_init = cls.__init__

            @wraps(cls.__init__)
            def wrapped_init(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                self.log = logger
            
            update_wrapper(wrapped_init, original_init)
            cls.__init__ = wrapped_init


            def attribute_profile_decorator(func, profiling_type, print2log):
                """Decorator that adds log method calls and adds profiling to functions."""
                @wraps(func)
                def wrapper(*args, **kwargs):
                    if verbose:
                        logger.debug(f"** {cls.__name__}.{func.__name__} ** Called", _log_system_msg="<LOG_MANAGER>")

                    try:
                        _result = manage_profiling(func, args, kwargs, profiling_type=profiling_type, print2log=print2log)
                    except Exception as e:
                        logger.error(f"Uncatched Error: {e}", _log_system_msg="<LOG_MANAGER>")
                        logger.error(trace_error_msg(), _log_system_msg="<LOG_MANAGER>")
                        profiler.disable()
                        del profiler
                        raise

                    if verbose:
                            logger.debug(f"** {cls.__name__}.{func.__name__} ** Returned", _log_system_msg="<LOG_MANAGER>")
    
                    return _result
                return wrapper

            def profile_all_methods(cls, profiling_type, print2log):
                """Class decorator that applies the `attr_profiler_decorator` decorator to all callable methods of a class."""
                for attr_name in dir(cls):
                    attr = getattr(cls, attr_name)
                    if callable(attr) and not attr_name.startswith("__"):
                        setattr(cls, attr_name, attribute_profile_decorator(attr, profiling_type, print2log))

            profile_all_methods(cls, enable_profiling, print2log)

            return cls

        @decorator.register(types.FunctionType)
        def _(func):  # Function decorator
            @wraps(func)
            def wrapper(*args, **kwargs):
                if verbose:
                    logger.debug(f'Function ** {func.__name__} ** Called', _log_system_msg="<LOG_MANAGER>")
                try:
                    kwargs.pop('log', None)
                    kwargs['log'] = logger
                    _result = manage_profiling(func, args, kwargs, profiling_type=enable_profiling, print2log=print2log)
                    if verbose:
                        logger.debug(f'Function ** {func.__name__} ** Returned.', _log_system_msg="<LOG_MANAGER>")
                    return _result
                except Exception as e:
                    logger.error(f"Uncatched Error: {e}", _log_system_msg="<LOG_MANAGER>")
                    logger.error(trace_error_msg(), _log_system_msg="<LOG_MANAGER>")
                    raise
            return wrapper
        
        return decorator
    
    setup_check=staticmethod(setup_check)
