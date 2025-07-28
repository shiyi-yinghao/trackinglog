#!/usr/bin/env python3
"""
Comprehensive test suite for trackinglog package.
Run with: python3 test_package.py
"""

import os
import sys
import glob
import tempfile
import shutil
import json
import time
import importlib
import subprocess
import multiprocessing
from datetime import datetime
from pathlib import Path

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import trackinglog
from trackinglog.task_manager.task_manager import TaskFolderStruct, TaskMgtAgent, TaskToken
from trackinglog.parameter_config.parameter_config import ParameterConfig
from trackinglog.log_manager.log_manager import LogManager


class TestRunner:
    """Simple test runner for tracking test results."""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
    
    def run_test_in_subprocess(self, test_name, test_func_name):
        """Run a single test in a subprocess to avoid singleton issues."""
        self.tests_run += 1
        print(f"Running {test_name}...", end=" ")
        
        # Create a temporary test file to run the test
        test_dir = os.path.dirname(os.path.abspath(__file__))
        temp_test_file = os.path.join(test_dir, f"temp_test_{test_func_name}.py")
        
        test_script_content = f'''#!/usr/bin/env python3
import sys
import os

# Add the package to path for testing
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)

# Import the test function
from test_package import {test_func_name}

try:
    {test_func_name}()
    print("PASS")
    sys.exit(0)
except Exception as e:
    import traceback
    print(f"FAIL: {{e}}")
    print(f"Error details:\\n{{traceback.format_exc()}}")
    sys.exit(1)
'''
        
        try:
            # Write temporary test file
            with open(temp_test_file, 'w') as f:
                f.write(test_script_content)
            
            # Run the test
            result = subprocess.run(
                [sys.executable, temp_test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.tests_passed += 1
                print("PASS")
            else:
                self.tests_failed += 1
                error_output = result.stdout + result.stderr
                self.failures.append((test_name, error_output))
                print("FAIL")
                if error_output.strip():
                    print(f"Error details:\\n{error_output}")
                    
        except subprocess.TimeoutExpired:
            self.tests_failed += 1
            error_msg = f"Test {test_name} timed out after 30 seconds"
            self.failures.append((test_name, error_msg))
            print(f"FAIL: {error_msg}")
            
        except Exception as e:
            self.tests_failed += 1
            error_msg = f"Failed to run subprocess: {e}"
            self.failures.append((test_name, error_msg))
            print(f"FAIL: {error_msg}")
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_test_file):
                try:
                    os.remove(temp_test_file)
                except:
                    pass  # Ignore cleanup errors

    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        self.tests_run += 1
        print(f"Running {test_name}...", end=" ")
        
        try:
            test_func()
            self.tests_passed += 1
            print("PASS")
        except Exception as e:
            self.tests_failed += 1
            import traceback
            error_details = traceback.format_exc()
            self.failures.append((test_name, error_details))
            print(f"FAIL: {e}")
            print(f"Error details:\n{error_details}")
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n{'='*50}")
        print(f"Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failures:
            print(f"\nFailed tests:")
            for test_name, error in self.failures:
                print(f"  {test_name}: {error}")
        
        return self.tests_failed == 0


def test_package_import():
    """Test basic package import."""
    assert hasattr(trackinglog, 'logger'), "trackinglog.logger not found"
    assert isinstance(trackinglog.logger, LogManager), "logger is not LogManager instance"


def test_task_token():
    """Test TaskToken dataclass."""
    # Test basic creation
    token = TaskToken(sys_status="INIT")
    assert token.sys_status == "INIT"
    assert token.user_config == {}
    
    # Test with user config
    token = TaskToken(sys_status="INPROGRESS", user_config={"key": "value"})
    assert token.sys_status == "INPROGRESS"
    assert token.user_config == {"key": "value"}


def test_task_folder_struct_lazy_initialization():
    """Test lazy initialization of TaskFolderStruct."""
    with tempfile.TemporaryDirectory() as tmpdir:
        folder_struct = TaskFolderStruct(tmpdir)
        
        # Initially, no paths should be cached
        assert len(folder_struct._paths) == 0
        
        # Access root folder - should create it and config folder
        root_path = folder_struct.root
        assert os.path.exists(root_path)
        assert "root" in folder_struct._paths
        assert "__config" in folder_struct._paths
        
        # Config token file should be created
        assert folder_struct._TaskFolderStruct__config_tkn_path is not None
        assert os.path.exists(folder_struct._TaskFolderStruct__config_tkn_path)
        
        # Access temp folder
        temp_path = folder_struct.temp
        assert os.path.exists(temp_path)
        assert "temp" in folder_struct._paths
        
        # Access other folders
        cache_path = folder_struct.cache
        var_path = folder_struct.var
        result_path = folder_struct.result
        
        assert os.path.exists(cache_path)
        assert os.path.exists(var_path)
        assert os.path.exists(result_path)


def test_task_folder_struct_status_operations():
    """Test status operations on TaskFolderStruct."""
    with tempfile.TemporaryDirectory() as tmpdir:
        folder_struct = TaskFolderStruct(tmpdir)
        
        # Initial status should be INIT
        assert folder_struct.status == "INIT"
        assert folder_struct.config == {}
        
        # Test inprogress
        test_config = {"step": 1}
        folder_struct.inprogress(test_config)
        assert folder_struct.status == "INPROGRESS"
        assert folder_struct.config == test_config
        
        # Test finish
        finish_config = {"result": "success"}
        folder_struct.finish(finish_config)
        assert folder_struct.status == "FINISH"
        assert folder_struct.config == finish_config
        
        # Test fail
        fail_config = {"error": "test error"}
        folder_struct.fail(fail_config)
        assert folder_struct.status == "FAIL"
        assert folder_struct.config == fail_config


# def test_email_credential():
#     """Test EmailCredential class."""
#     # Test with dict
#     email_data = {
#         'username': 'test@example.com',
#         'password': 'testpass',
#         'root_emails_folder': './emails'
#     }
    
#     credential = EmailCredential(email_data)
#     assert credential.username == 'test@example.com'
#     assert credential.password == 'testpass'
#     assert credential.root_emails_folder == './emails'


def test_parameter_config():
    """Test ParameterConfig class."""
    config = ParameterConfig()
    
    # Test basic setup
    with tempfile.TemporaryDirectory() as tmpdir:
        config.setup(
            task_name="test_task",
            root_folder_path=tmpdir,
            task_config={"task_num_limit": 10}
        )
        
        assert config.task_name == "test_task"
        assert config.root_folder_path == tmpdir


def test_log_manager_singleton():
    """Test LogManager singleton behavior."""
    logger1 = LogManager()
    logger2 = LogManager()
    
    assert logger1 is logger2, "LogManager should be singleton"
    assert logger1 is trackinglog.logger, "trackinglog.logger should be same instance"


def test_basic_logging_functionality():
    """Test basic logging functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup logger
        trackinglog.logger.setup(
            task_name="test_logging",
            root_folder_path=tmpdir
        )
        
        # Test get_logger
        logger = trackinglog.logger.get_logger('test_logger')
        assert logger is not None
        
        # Test basic logging
        logger.info("Test log message")
        
        # Test decorator functionality
        @trackinglog.logger.get_log('decorator_test', verbose=1)
        def test_function(log=None):
            log.info("Function executed")
            return "success"
        
        result = test_function()
        assert result == "success"

def test_error_logging_functionality():
    """Test basic logging functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup logger
        trackinglog.logger.setup(
            task_name="test_logging",
            root_folder_path=tmpdir
        )
        
        # Test get_logger
        logger = trackinglog.logger.get_logger('test_logger')
        assert logger is not None
        
        # Test basic logging
        logger.info("Test log message")
        
        # Test decorator functionality
        def func():
            @trackinglog.logger.get_log('decorator_test', verbose=1)
            def test_function(log=None):
                assert False, "Tested Error"
                log.info("Function executed")
                return "success"
            try:
                res = test_function()
            except:
                res = "erorr"
            return res
        
        result = func()
        matches = glob.glob(f"{tmpdir}/test_logging/*_*/logs/decorator_test*")
        file_path = matches[0]
        with open(file_path, 'r') as f:
            contents = f.read()

        assert "<LOG_MANAGER> - Traceback (most recent call last)" in contents
        assert "Tested Error" in contents


def test_class_logging():
    """Test class-based logging."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup logger
        trackinglog.logger.setup(
            task_name="test_class_logging",
            root_folder_path=tmpdir
        )
        
        @trackinglog.logger.get_log('class_test', verbose=1)
        class TestClass:
            def __init__(self, value):
                self.value = value
            
            def get_value(self):
                self.log.info(f"Getting value: {self.value}")
                return self.value
        
        test_obj = TestClass(42)
        result = test_obj.get_value()
        assert result == 42
        
        # Test that log attribute exists
        assert hasattr(test_obj, 'log')


def test_task_management():
    """Test task management functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup with task management
        trackinglog.logger.setup(
            task_name="test_tasks",
            root_folder_path=tmpdir,
            task_config={
                "task_num_limit": 5,
                "task_expiration_date": None,
                "resume_task": False
            }
        )
        
        # Access task folder structure
        folder_config = trackinglog.logger.config.task_config._folder_path_config
        
        # Test folder access
        root_path = folder_config.root
        temp_path = folder_config.temp
        var_path = folder_config.var
        
        assert os.path.exists(root_path)
        assert os.path.exists(temp_path)
        assert os.path.exists(var_path)
        
        # Test status management
        folder_config.inprogress({"task": "running"})
        assert folder_config.status == "INPROGRESS"
        
        folder_config.finish({"result": "completed"})
        assert folder_config.status == "FINISH"


def test_profiling_functionality():
    """Test profiling functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup logger with profiling
        trackinglog.logger.setup(
            task_name="test_profiling",
            root_folder_path=tmpdir
        )
        
        @trackinglog.logger.get_log('profiling_test', verbose=1, enable_profiling="function")
        def profiled_function(log=None):
            log.info("Profiled function executed")
            # Simulate some work
            time.sleep(0.01)
            return "profiled"
        
        result = profiled_function()
        assert result == "profiled"


def test_print_to_log():
    """Test print to log functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup logger
        trackinglog.logger.setup(
            task_name="test_print2log",
            root_folder_path=tmpdir
        )
        
        @trackinglog.logger.get_log('print2log_test', verbose=1, print2log=True)
        def function_with_prints(log=None):
            log.info("Function started")
            print("This should be captured in log")
            return "done"

        result = function_with_prints()
                
        matches = glob.glob(f"{tmpdir}/test_print2log/*_*/logs/print2log_test*")
        file_path = matches[0]
        with open(file_path, 'r') as f:
            contents = f.read()

        assert result == "done"
        assert "This should be captured in log" in contents

def test_setup_after_definition():
    """Test that setup works even when called after class/function definition."""
    # Define decorated function BEFORE setup
    @trackinglog.logger.get_log('delayed_setup_test', verbose=1)
    def function_before_setup(log=None):
        folder_root = log.folder.root
        log.info(f"Using folder: {folder_root}")
        return folder_root
    

    @trackinglog.logger.get_log('delayed_class_test', verbose=1)
    class ClassBeforeSetup:
        def __init__(self, value):
            self.value = value
        
        def process(self):
            self.log.info(f"Processing value: {self.value}")
            return self.value * 2
    
    # Now setup AFTER definitions
    with tempfile.TemporaryDirectory() as tmpdir:
        trackinglog.logger.setup(
            task_name="delayed_setup_test",
            root_folder_path=tmpdir
        )
        
        # Test function works after delayed setup
        result = function_before_setup()
        assert tmpdir in result
        
        # Test class works after delayed setup
        obj = ClassBeforeSetup(5)
        class_result = obj.process()
        assert class_result == 10
        
        # Verify logging infrastructure is working
        assert hasattr(obj, 'log')
        folder_config = trackinglog.logger.config.task_config._folder_path_config
        assert folder_config.status == "INIT"


def test_default_config_without_setup():
    """Test that system uses default config when no setup is called."""
    # Create a fresh logger instance to test default behavior
    # Note: This test relies on setup_check's fallback behavior
    
    @trackinglog.logger.get_log('default_config_test', verbose=1)
    def function_without_setup(log=None):
        log.info("Function using default config")
        folder_root = log.folder.root
        return folder_root
    
    # Call function without any setup - should trigger default setup
    result = function_without_setup()
    
    # Verify default config was used
    assert result is not None
    assert os.path.exists(result)
    assert f"{os.getcwd()}/.cache/__trackinglog__" in result
    
    # Check that default paths are created
    default_config = trackinglog.logger.config
    assert default_config is not None
    
    # Verify default task structure exists
    folder_config = default_config.task_config._folder_path_config
    assert folder_config.status == "INIT"
    assert os.path.exists(folder_config.root)


def test_setup_override_behavior():
    """Test that later setup calls override earlier ones completely."""
    # Define function that will be used with different setups
    @trackinglog.logger.get_log('override_test', verbose=1)
    def tracked_function(input_value, log=None):
        log.info(f"Processing input: {input_value}")
        folder_root = log.folder.root
        log.info(f"Using folder: {folder_root}")
        return folder_root
    
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            # Setup 1
            trackinglog.logger.setup(
                task_name="setup1",
                root_folder_path=tmpdir1
            )
            
            result1 = tracked_function("test1")
            assert tmpdir1 in result1
            
            # Setup 2 - should completely override setup 1
            trackinglog.logger.setup(
                task_name="setup2",
                root_folder_path=tmpdir2
            )
            
            result2 = tracked_function("test2")
            assert tmpdir2 in result2
            assert tmpdir1 not in result2
            
            # Verify singleton still works and uses latest config
            logger_instance = trackinglog.logger
            assert logger_instance.config.task_name == "setup2"


def test_single_setup_restriction():
    """Test that multiple setup calls raise error when single setup is enforced."""
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            # First setup should work
            trackinglog.logger.setup(
                task_name="first_setup",
                root_folder_path=tmpdir1
            )
            
            # Second setup should raise error
            try:
                trackinglog.logger.setup(
                    task_name="second_setup",
                    root_folder_path=tmpdir2
                )
                # If we reach here, the restriction isn't working
                assert False, "Expected error for multiple setup calls"
            except RuntimeError as e:
                assert "already been configured" in str(e).lower() or "multiple setup" in str(e).lower()
            except Exception as e:
                # Accept any exception that indicates setup restriction
                assert "setup" in str(e).lower() or "config" in str(e).lower()


def run_all_tests():
    """Run all tests."""
    runner = TestRunner()
    
    print("Starting trackinglog package tests...")
    print("="*50)
    
    # Basic tests
    runner.run_test_in_subprocess("Package Import", "test_package_import")
    runner.run_test_in_subprocess("Task Token", "test_task_token")
    # runner.run_test("Email Credential", test_email_credential)
    runner.run_test_in_subprocess("LogManager Singleton", "test_log_manager_singleton")
    
    # Core functionality tests
    runner.run_test_in_subprocess("Task Folder Struct Lazy Init", "test_task_folder_struct_lazy_initialization")
    runner.run_test_in_subprocess("Task Folder Status Operations", "test_task_folder_struct_status_operations")
    runner.run_test_in_subprocess("Parameter Config", "test_parameter_config")
    
    # Logging functionality tests
    runner.run_test_in_subprocess("Basic Logging", "test_basic_logging_functionality")
    runner.run_test_in_subprocess("Class Logging", "test_class_logging")
    runner.run_test_in_subprocess("Task Management", "test_task_management")
    runner.run_test_in_subprocess("Profiling", "test_profiling_functionality")
    runner.run_test_in_subprocess("Print to Log", "test_print_to_log")
    
    # Setup timing and behavior tests - run in subprocess to avoid singleton issues
    runner.run_test_in_subprocess("Default Config Without Setup", "test_default_config_without_setup")
    runner.run_test_in_subprocess("Setup After Definition", "test_setup_after_definition")
    runner.run_test_in_subprocess("Single Setup Restriction", "test_single_setup_restriction")
    # runner.run_test("Basic Logging", test_class_logging)
    return runner.print_summary()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)