#!/usr/bin/env python3
"""
Comprehensive usage examples for trackinglog package.
This file demonstrates all features and use cases of the trackinglog package.

Run with: python3 usage_examples.py
"""

import os
import sys
import tempfile
import time
from datetime import datetime

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import trackinglog


def example_basic_setup():
    """Example 1: Basic setup and usage (minimal configuration)."""
    print("\n" + "="*60)
    print("Example 1: Basic Setup and Usage")
    print("="*60)
    
    # Basic setup - creates default directories under ./cache/__trackinglog__
    trackinglog.logger.setup()
    
    # Simple function logging
    @trackinglog.logger.get_log('basic_logger')
    def simple_function(log=None):
        log.info("This is a simple logged function")
        return "Function completed"
    
    result = simple_function()
    print(f"Result: {result}")


def example_custom_task_setup():
    """Example 2: Custom task setup with specific paths."""
    print("\n" + "="*60)
    print("Example 2: Custom Task Setup")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Custom setup with specific task name and path
        trackinglog.logger.setup(
            task_name="CustomTask",
            root_folder_path=temp_dir
        )
        
        # Access folder structure
        folder_config = trackinglog.logger.config.task_config._folder_path_config
        
        print(f"Task root folder: {folder_config.root}")
        print(f"Task temp folder: {folder_config.temp}")
        print(f"Task var folder: {folder_config.var}")
        print(f"Task result folder: {folder_config.result}")
        print(f"Task cache folder: {folder_config.cache}")
        
        # Check initial task status
        print(f"Initial task status: {folder_config.status}")
        print(f"Initial task config: {folder_config.config}")


def example_comprehensive_setup():
    """Example 3: Comprehensive setup with all configuration options."""
    print("\n" + "="*60)
    print("Example 3: Comprehensive Configuration")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        trackinglog.logger.setup(
            task_name="ComprehensiveTask",
            root_folder_path=temp_dir,
            task_config={
                "task_num_limit": 3,
                "task_expiration_date": 7,  # Keep tasks for 7 days
                "task_folder_format": "%y%m%d_000001",
                "resume_task": False,  # Create new task
                "new_task": None
            },
            log_config={
                'root_log_path': os.path.join(temp_dir, "logs"),
                '_cache_log_path': os.path.join(temp_dir, "logs/cache"),
                'cache_log_num_limit': 10,
                '_cache_log_day_limit': 7
            },
            email_credential={
                'username': "example@email.com",
                'password': "password123",
                'root_emails_folder': os.path.join(temp_dir, "emails")
            },
            lock_config={
                "lock_folder_path": os.path.join(temp_dir, "locks")
            }
        )
        
        print("Comprehensive setup completed successfully!")
        print(f"Task folder: {trackinglog.logger.config.task_config._folder_path_config.root}")


def example_function_decorator():
    """Example 4: Function decorator with various options."""
    print("\n" + "="*60)
    print("Example 4: Function Decorator Usage")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        trackinglog.logger.setup(
            task_name="FunctionTest",
            root_folder_path=temp_dir
        )
        
        # Basic function logging
        @trackinglog.logger.get_log('function_logger', verbose=1)
        def logged_function(x, y, log=None):
            log.info(f"Computing {x} + {y}")
            result = x + y
            log.info(f"Result: {result}")
            return result
        
        result = logged_function(5, 3)
        print(f"Function result: {result}")
        
        # Function with profiling
        @trackinglog.logger.get_log('profiled_function', verbose=1, enable_profiling="function")
        def profiled_function(n, log=None):
            log.info(f"Processing {n} items")
            total = 0
            for i in range(n):
                total += i
            log.info(f"Sum of first {n} numbers: {total}")
            return total
        
        result = profiled_function(100)
        print(f"Profiled function result: {result}")
        
        # Function with line-level profiling
        @trackinglog.logger.get_log('line_profiled', verbose=1, enable_profiling="line")
        def line_profiled_function(log=None):
            log.info("Starting line profiling")
            # Some operations to profile
            data = [i**2 for i in range(1000)]
            result = sum(data)
            log.info(f"Computed sum: {result}")
            return result
        
        result = line_profiled_function()
        print(f"Line profiled result: {result}")


def example_class_decorator():
    """Example 5: Class decorator usage (from test.ipynb)."""
    print("\n" + "="*60)
    print("Example 5: Class Decorator Usage")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        trackinglog.logger.setup(
            task_name="ClassTest",
            root_folder_path=temp_dir
        )
        
        @trackinglog.logger.get_log('class_logger', verbose=1, enable_profiling="line", print2log=False)
        class TestClass:
            def __init__(self, value):
                self.value = value
            
            def process(self):
                self.log.info("Processing data")
                print(f"Folder structure available: {self.log.folder}")
                print(f"Variable folder path: {self.log.folder.var}")
                return self.value * 2
            
            def count_items(self, n):
                self.log.info(f"Counting {n} items")
                for i in range(n):
                    print(f"Item {i}")
                return n
        
        # Create and use the class
        test_obj = TestClass(42)
        result = test_obj.process()
        print(f"Processed value: {result}")
        
        count_result = test_obj.count_items(3)
        print(f"Count result: {count_result}")


def example_inline_logging():
    """Example 6: Inline logging without decorators."""
    print("\n" + "="*60)
    print("Example 6: Inline Logging")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        trackinglog.logger.setup(
            task_name="InlineTest",
            root_folder_path=temp_dir
        )
        
        def regular_function(x, y):
            # Get logger inside function
            log = trackinglog.logger.get_logger('inline_logger')
            log.info(f"Regular function called with {x}, {y}")
            
            result = x * y
            log.info(f"Multiplication result: {result}")
            return result
        
        result = regular_function(6, 7)
        print(f"Inline logging result: {result}")


def example_task_status_management():
    """Example 7: Task status and configuration management."""
    print("\n" + "="*60)
    print("Example 7: Task Status Management")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        trackinglog.logger.setup(
            task_name="StatusTest",
            root_folder_path=temp_dir
        )
        
        # Get folder configuration
        folder_config = trackinglog.logger.config.task_config._folder_path_config
        
        # Check initial status
        print(f"Initial status: {folder_config.status}")
        print(f"Initial config: {folder_config.config}")
        
        # Set task as in progress with custom config
        progress_config = {
            "step": 1,
            "description": "Processing data",
            "timestamp": datetime.now().isoformat()
        }
        folder_config.inprogress(progress_config)
        print(f"In progress status: {folder_config.status}")
        print(f"Progress config: {folder_config.config}")
        
        # Simulate some work
        time.sleep(0.1)
        
        # Mark as finished
        finish_config = {
            "step": 2,
            "description": "Task completed successfully",
            "result": "All operations completed",
            "timestamp": datetime.now().isoformat()
        }
        folder_config.finish(finish_config)
        print(f"Final status: {folder_config.status}")
        print(f"Final config: {folder_config.config}")


def example_print_to_log():
    """Example 8: Print to log functionality."""
    print("\n" + "="*60)
    print("Example 8: Print to Log Capture")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        trackinglog.logger.setup(
            task_name="PrintTest",
            root_folder_path=temp_dir
        )
        
        @trackinglog.logger.get_log('print_logger', verbose=1, print2log=True)
        def function_with_prints(log=None):
            log.info("Function started")
            print("This print will be captured in the log")
            print("So will this one")
            
            # Regular logging still works
            log.info("Regular log message")
            
            return "Function completed"
        
        result = function_with_prints()
        print(f"Function with print capture result: {result}")


def example_error_handling():
    """Example 9: Error handling and logging."""
    print("\n" + "="*60)
    print("Example 9: Error Handling")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        trackinglog.logger.setup(
            task_name="ErrorTest",
            root_folder_path=temp_dir
        )
        
        @trackinglog.logger.get_log('error_logger', verbose=1)
        def function_with_error(should_fail=False, log=None):
            log.info("Function started")
            
            if should_fail:
                log.error("About to raise an error")
                raise ValueError("This is a test error")
            
            log.info("Function completed successfully")
            return "Success"
        
        # Successful execution
        try:
            result = function_with_error(should_fail=False)
            print(f"Success case result: {result}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        # Error case
        try:
            result = function_with_error(should_fail=True)
            print(f"Error case result: {result}")
        except Exception as e:
            print(f"Expected error caught: {e}")
            
            # Check task status after error
            folder_config = trackinglog.logger.config.task_config._folder_path_config
            error_config = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            folder_config.fail(error_config)
            print(f"Task marked as failed: {folder_config.status}")


def example_task_resume():
    """Example 10: Task resume functionality."""
    print("\n" + "="*60)
    print("Example 10: Task Resume")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print("**temp_dir, ", temp_dir)
        # Create initial task
        trackinglog.logger.setup(
            task_name="ResumeTest1",
            root_folder_path=temp_dir,
            task_config={"resume_task": False}  # Create new task
        )
        
        folder_config = trackinglog.logger.config.task_config._folder_path_config
        folder_config.inprogress({"step": 1, "data": "initial"})
        
        print(f"Created task with status: {folder_config.status}")
        print(f"Task config: {folder_config.config}")
        print(f"root_folder: ", folder_config.root)
        
        # Resume latest task
        trackinglog.logger.setup(
            task_name="ResumeTest1",
            root_folder_path=temp_dir,
            task_config={"resume_task": "LATEST"}  # Resume latest task
        )
        
        folder_config = trackinglog.logger.config.task_config._folder_path_config
        print(f"Resumed task status: {folder_config.status}")
        print(f"Resumed task config: {folder_config.config}")


def example_multiple_loggers():
    """Example 11: Multiple loggers in same application."""
    print("\n" + "="*60)
    print("Example 11: Multiple Loggers")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        trackinglog.logger.setup(
            task_name="MultiLogger",
            root_folder_path=temp_dir
        )
        
        # Different loggers for different components
        auth_logger = trackinglog.logger.get_logger('auth_system')
        db_logger = trackinglog.logger.get_logger('database')
        api_logger = trackinglog.logger.get_logger('api_handler')
        
        # Simulate different system components
        auth_logger.info("User authentication started")
        db_logger.info("Database connection established")
        api_logger.info("API request received")
        
        # Use decorators with different logger names
        @trackinglog.logger.get_log('auth_decorator', verbose=1)
        def authenticate_user(username, log=None):
            log.info(f"Authenticating user: {username}")
            return f"User {username} authenticated"
        
        @trackinglog.logger.get_log('db_decorator', verbose=1)
        def query_database(query, log=None):
            log.info(f"Executing query: {query}")
            return "Query results"
        
        auth_result = authenticate_user("testuser")
        db_result = query_database("SELECT * FROM users")
        
        print(f"Auth result: {auth_result}")
        print(f"DB result: {db_result}")


def run_all_examples():
    """Run all usage examples."""
    print("TrackingLog Package - Comprehensive Usage Examples")
    print("=" * 80)
    
    examples = [
        example_basic_setup,
        example_custom_task_setup,
        example_comprehensive_setup,
        example_function_decorator,
        example_class_decorator,
        example_inline_logging,
        example_task_status_management,
        example_print_to_log,
        example_error_handling,
        example_task_resume,
        example_multiple_loggers
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\nError in example {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("All usage examples completed!")
    print("="*80)


if __name__ == "__main__":
    run_all_examples()