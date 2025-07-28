# TrackingLog

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/trackinglog)](https://pypi.org/project/trackinglog/)
[![GitHub](https://img.shields.io/badge/github-trackinglog-green)](https://github.com/shiyi-yinghao/trackinglog)

TrackingLog is a comprehensive Python logging package designed for tracing function calls with advanced features including error handling, profiling, task management, and email notifications. It provides decorators and managers for comprehensive application monitoring and debugging.

## 🚀 Features

- **Function & Class Logging**: Decorators for automatic entry/exit logging
- **Profiling Integration**: Line-level and function-level performance profiling
- **Task Management**: Structured task lifecycle management with resume capabilities
- **Error Handling**: Comprehensive error tracking and logging
- **Email Notifications**: Built-in email notification system
- **Print Capture**: Redirect print statements to log files
- **Resource Monitoring**: CPU and memory usage tracking
- **Cache Management**: Automatic log cleanup and rotation
- **Flexible Configuration**: Centralized configuration management

## 📦 Installation

```bash
pip install trackinglog
```

### Dependencies

- `numpy>=2.0.1`
- `pandas>=2.2.2`  
- `line_profiler>=4.1.3`

## 🔧 Quick Start

### Basic Setup

```python
import trackinglog

# Basic setup with default configuration
trackinglog.logger.setup()

@trackinglog.logger.get_log('my_logger')
def my_function(log=None):
    log.info("This function does something important.")
    return "Function completed"

result = my_function()
```

### Custom Task Setup

```python
import trackinglog

# Custom setup with specific task name and path
trackinglog.logger.setup(
    task_name="My_Project",
    root_folder_path='./my_logs'
)

@trackinglog.logger.get_log('custom_logger', verbose=1, enable_profiling="function")
def compute_data(x, y, log=None):
    log.info(f"Computing {x} + {y}")
    result = x + y
    log.info(f"Result: {result}")
    return result

result = compute_data(5, 3)
```

## 📚 Usage Examples

### Function Decorator

```python
import trackinglog

trackinglog.logger.setup(task_name="FunctionExample")

# Basic function logging
@trackinglog.logger.get_log('function_logger', verbose=1)
def process_data(data, log=None):
    log.info(f"Processing {len(data)} items")
    processed = [x * 2 for x in data]
    log.info("Processing completed")
    return processed

# Function with line-level profiling
@trackinglog.logger.get_log('profiled_func', verbose=1, enable_profiling="line")
def intensive_computation(n, log=None):
    log.info(f"Starting computation for {n} iterations")
    result = sum(i**2 for i in range(n))
    log.info(f"Computation result: {result}")
    return result

result = process_data([1, 2, 3, 4, 5])
profiled_result = intensive_computation(1000)
```

### Class Decorator

```python
import trackinglog

trackinglog.logger.setup(task_name="ClassExample")

@trackinglog.logger.get_log('class_logger', verbose=1, print2log=True)
class DataProcessor:
    def __init__(self, name):
        self.name = name
        self.log.info(f"DataProcessor '{name}' initialized")
    
    def process(self, data):
        self.log.info(f"Processing data with {len(data)} items")
        print(f"Processing {self.name}")  # This will be captured in logs
        return [x * 2 for x in data]
    
    def get_stats(self):
        self.log.info("Generating statistics")
        # Access folder structure
        print(f"Results folder: {self.log.folder.result}")
        return {"processed": True}

processor = DataProcessor("MyProcessor")
result = processor.process([1, 2, 3])
stats = processor.get_stats()
```

### Inline Logging

```python
import trackinglog

trackinglog.logger.setup(task_name="InlineExample")

def regular_function(x, y):
    # Get logger inside function
    log = trackinglog.logger.get_logger('inline_logger')
    log.info(f"Function called with {x}, {y}")
    
    result = x * y
    log.info(f"Calculation result: {result}")
    return result

result = regular_function(6, 7)
```

## ⚙️ Configuration

### Comprehensive Setup

```python
import trackinglog

trackinglog.logger.setup(
    task_name="ComprehensiveExample",
    root_folder_path='./task_logs',
    task_config={
        "task_num_limit": 5,
        "task_expiration_date": 7,  # Keep tasks for 7 days
        "resume_task": False,       # Create new task
        "new_task": None
    },
    log_config={
        'root_log_path': "./logs",
        '_cache_log_path': "./logs/cache",
        'cache_log_num_limit': 10,
        '_cache_log_day_limit': 7
    },
    email_credential={
        'username': "your_email@example.com",
        'password': "your_password",
        'root_emails_folder': "./logs/emails"
    },
    lock_config={
        "lock_folder_path": "./logs/locks"
    }
)
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `task_name` | Name for the current task | `"Default_Task"` |
| `root_folder_path` | Root directory for all task files | `"./cache/__trackinglog__"` |
| `task_config` | Task management settings | See below |
| `log_config` | Logging configuration | See below |
| `email_credential` | Email notification settings | None |
| `lock_config` | File locking configuration | None |

#### Task Config Options

```python
task_config = {
    "task_num_limit": 500,           # Maximum number of tasks to keep
    "task_expiration_date": 30,      # Days to keep tasks
    "task_folder_format": "%y%m%d_000001",  # Task folder naming format
    "resume_task": None,             # None: auto, True: resume latest, False: new task
    "new_task": None                 # None: auto, True: force new, False: resume only
}
```

#### Log Config Options

```python
log_config = {
    'root_log_path': "./logs",           # Main log directory
    '_cache_log_path': "./logs/cache",   # Cache log directory
    'cache_log_num_limit': 50,           # Max cache log files
    '_cache_log_day_limit': 30           # Days to keep cache logs
}
```

## 🏗️ Task Management

TrackingLog creates a structured folder hierarchy for each task:

```
task_folder/
├── root/           # Main task directory
├── temp/           # Temporary files
├── cache/          # Cache files
├── var/            # Variable data
├── result/         # Task results
└── __config/       # Task configuration and status
```

### Task Status Management

```python
import trackinglog
from datetime import datetime

trackinglog.logger.setup(task_name="StatusExample")

# Get folder configuration
folder_config = trackinglog.logger.config.task_config._folder_path_config

# Set task as in progress
progress_config = {
    "step": 1,
    "description": "Processing data",
    "timestamp": datetime.now().isoformat()
}
folder_config.inprogress(progress_config)

# Mark as finished
finish_config = {
    "step": 2,
    "description": "Task completed successfully",
    "result": "All operations completed",
    "timestamp": datetime.now().isoformat()
}
folder_config.finish(finish_config)

# Check status
print(f"Task status: {folder_config.status}")
print(f"Task config: {folder_config.config}")
```

### Task Resume

```python
import trackinglog

# Create new task
trackinglog.logger.setup(
    task_name="ResumeExample",
    task_config={"resume_task": False}  # Force new task
)

# Later, resume the latest task
trackinglog.logger.setup(
    task_name="ResumeExample", 
    task_config={"resume_task": "LATEST"}  # Resume latest task
)
```

## 🔍 Profiling

### Function-Level Profiling

```python
@trackinglog.logger.get_log('profiler', enable_profiling="function")
def compute_heavy(n, log=None):
    total = 0
    for i in range(n):
        total += i ** 2
    return total
```

### Line-Level Profiling

```python
@trackinglog.logger.get_log('line_profiler', enable_profiling="line")
def detailed_analysis(data, log=None):
    # Each line will be profiled
    processed = []
    for item in data:
        result = item * 2 + 1
        processed.append(result)
    return processed
```

## 📧 Email Notifications

```python
import trackinglog

# Setup with email credentials
trackinglog.logger.setup(
    task_name="EmailExample",
    email_credential={
        'username': "your_email@example.com",
        'password': "your_app_password",
        'root_emails_folder': "./emails"
    }
)

# Email notifications will be sent for errors and task completion
```

## 🚨 Error Handling

```python
import trackinglog

trackinglog.logger.setup(task_name="ErrorExample")

@trackinglog.logger.get_log('error_logger', verbose=1)
def risky_function(should_fail=False, log=None):
    log.info("Function started")
    
    if should_fail:
        log.error("About to raise an error")
        raise ValueError("This is a test error")
    
    log.info("Function completed successfully")
    return "Success"

# Successful execution
try:
    result = risky_function(should_fail=False)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")

# Error case - will be logged automatically
try:
    result = risky_function(should_fail=True)
except Exception as e:
    print(f"Caught error: {e}")
    
    # Manually mark task as failed
    folder_config = trackinglog.logger.config.task_config._folder_path_config
    folder_config.fail({"error": str(e), "timestamp": "2024-01-01T12:00:00"})
```

## 🎯 Multiple Loggers

```python
import trackinglog

trackinglog.logger.setup(task_name="MultiLoggerExample")

# Create different loggers for different components
auth_logger = trackinglog.logger.get_logger('auth_system')
db_logger = trackinglog.logger.get_logger('database')
api_logger = trackinglog.logger.get_logger('api_handler')

# Use them independently
auth_logger.info("User authentication started")
db_logger.info("Database connection established")
api_logger.info("API request received")

# Or use with decorators
@trackinglog.logger.get_log('auth_decorator', verbose=1)
def authenticate_user(username, log=None):
    log.info(f"Authenticating user: {username}")
    return f"User {username} authenticated"

@trackinglog.logger.get_log('db_decorator', verbose=1)  
def query_database(query, log=None):
    log.info(f"Executing query: {query}")
    return "Query results"
```

## 📖 API Reference

### LogManager Methods

- `setup(**config)`: Configure the logging system
- `get_log(name, verbose=0, enable_profiling=None, print2log=False)`: Decorator for functions/classes
- `get_logger(name)`: Get logger instance for inline usage

### Decorator Parameters

- `name`: Logger name (string)
- `verbose`: Logging verbosity level (0, 1, 2)
- `enable_profiling`: Profiling mode ("function", "line", or None)
- `print2log`: Capture print statements in logs (boolean)

### Task Status Methods

- `folder_config.inprogress(config)`: Mark task as in progress
- `folder_config.finish(config)`: Mark task as finished
- `folder_config.fail(config)`: Mark task as failed
- `folder_config.status`: Get current task status
- `folder_config.config`: Get current task configuration

## 📋 Version History

- **0.1.9.1**: Default task name and root folder path, usage without setup, increased task limit to 500
- **0.1.9**: Optimized log logic and bug fixes
- **0.1.8.6**: Enhanced resume task mechanism with True option for latest task
- **0.1.8.5**: New resume task mechanism with boolean controls
- **0.1.8.4**: Enhanced task status management (finish, inprogress, fail)
- **0.1.8.3**: Enhanced task manager with finish tokens
- **0.1.8**: Embedded task manager and optimized cache logic
- **0.1.7**: Added error handling message mechanism
- **0.1.6.2**: Bug fixes
- **0.1.6**: Updated to Parameter config, added inline log usage
- **0.1.5**: Added cache log cleaner
- **0.1.4**: Formatted logging with indentation, print to log feature
- **0.1.3**: Added profiler, error handling, class name logging, resource tracking
- **0.1.2**: Added error handling, verbose option, function name logging
- **0.1.1**: Created decorators and setup check
- **0.1.0**: Package draft created

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- **GitHub**: https://github.com/shiyi-yinghao/trackinglog
- **PyPI**: https://pypi.org/project/trackinglog/
- **Author**: Yinghao Li (shiyi.yinghao@gmail.com)

## 🆘 Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.