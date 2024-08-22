# TrackLogging

TrackLogging is a logging package for tracing function calls with error handling and email notification.

## Installation

You can install TrackingLog using pip:

```bash
pip install trackinglog

```

## Github URL
https://github.com/shiyi-yinghao/trackinglog

## PyPi URL
https://pypi.org/project/trackinglog/

## version History

0.1.0 Package Draft created

0.1.1 Decorator get_log and directly object creator get_logger created. Added setup check decorator. Added p-functions(print and log).

0.1.2 Added error handling. Added verbose option for decorator. Added called function name.

0.1.3 Added profiler for both function level and line level. Updated error handling logic: reset verbose to False, but it will now raise error instead. Added class name to log. Added dependency pakages. Added resource performance tracking.

0.1.4 Formatted the logging message with indentation. Add print to log feature. Refactor the get_log function.

0.1.5 AddED cache log cleaner.

## Feature in developing

Add public and private log

Add email notification

Add Kafka message notification


## Uaage for function:

```python
import logging
import trackinglog
import inspect

# Setup the LogManager with root logging path
trackinglog.logger.setup(root_log_path='./logs')

@trackinglog.logger.get_log('my_logger', verbose=1, enable_profiling="line")
def my_function(log=None):  # Notice how the log parameter is expected
    log.info("This function does something important.")
    print("Function is executing...")
    assert False, "This function is broken!"
    
my_function()  # Running the function will log start and end, using the specific logger

```

## Usage for class:
```python
@trackinglog.logger.get_log('my_logger_cls', verbose=1, enable_profiling="line", print2log=True)
class testclass:
    def __init__(self, a: int):
        self.a=a
    def p(self):
        self.log.info("class log")
        assert False , "This function is broken!"

    def count(self, n: int):
        for i in range(n):
            print(i)
    

t=testclass(2.2)
t.p()
t.count(3)

```

