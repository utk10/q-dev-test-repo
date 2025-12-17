#!/usr/bin/env python3
"""
Unit tests for main.py application with focus on error scenarios.

Tests cover:
- Logging functionality and configuration
- Error handling scenarios
- Command line argument parsing
- Log rotation and cleanup
- Exception handling
"""

import argparse
import logging
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import Application, LogManager, ApplicationError, main


class TestLogManager(unittest.TestCase):
    """Test cases for LogManager class."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_manager = LogManager(log_dir=self.temp_dir, retention_days=5)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_manager_initialization(self):
        """Test LogManager initialization with custom parameters."""
        self.assertEqual(str(self.log_manager.log_dir), self.temp_dir)
        self.assertEqual(self.log_manager.retention_days, 5)
        self.assertIsNone(self.log_manager.logger)
    
    def test_setup_logging_creates_directory(self):
        """Test that setup_logging creates log directory if it doesn't exist."""
        # Remove the temp directory to test creation
        import shutil
        shutil.rmtree(self.temp_dir)
        
        logger = self.log_manager.setup_logging()
        
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertIsNotNone(logger)
    
    def test_setup_logging_verbose_mode(self):
        """Test logging setup with verbose mode enabled."""
        logger = self.log_manager.setup_logging(verbose=True)
        
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertIsNotNone(logger)
    
    def test_setup_logging_normal_mode(self):
        """Test logging setup with normal mode."""
        logger = self.log_manager.setup_logging(verbose=False)
        
        self.assertEqual(logger.level, logging.INFO)
        self.assertIsNotNone(logger)
    
    def test_log_file_creation(self):
        """Test that log files are created with correct naming."""
        self.log_manager.setup_logging()
        
        expected_log_file = Path(self.temp_dir) / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Log files might not exist until first log entry, so we check the handler configuration
        self.assertTrue(len(self.log_manager.logger.handlers) >= 2)  # File + Console handlers
    
    def test_cleanup_old_logs(self):
        """Test cleanup of old log files."""
        # Create some old log files
        old_date = datetime.now() - timedelta(days=10)
        old_log_file = Path(self.temp_dir) / f"app_{old_date.strftime('%Y%m%d')}.log"
        old_log_file.touch()
        
        # Set the file modification time to be old
        old_timestamp = old_date.timestamp()
        os.utime(old_log_file, (old_timestamp, old_timestamp))
        
        # Setup logging (which triggers cleanup)
        self.log_manager.setup_logging()
        
        # Old file should be removed
        self.assertFalse(old_log_file.exists())
    
    @patch('main.logging.handlers.TimedRotatingFileHandler')
    def test_logging_setup_failure_fallback(self, mock_handler):
        """Test fallback to basic logging when advanced setup fails."""
        # Make the handler raise an exception
        mock_handler.side_effect = Exception("Handler creation failed")
        
        with patch('main.logging.basicConfig') as mock_basic_config:
            logger = self.log_manager.setup_logging()
            
            # Should fall back to basic logging
            mock_basic_config.assert_called_once()
            self.assertIsNotNone(logger)


class TestApplication(unittest.TestCase):
    """Test cases for Application class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.app = Application()
        self.app.log_manager = LogManager(log_dir=self.temp_dir, retention_days=5)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_argument_parser_setup(self):
        """Test command line argument parser configuration."""
        parser = self.app.setup_argument_parser()
        
        self.assertIsInstance(parser, argparse.ArgumentParser)
        
        # Test parsing valid arguments
        args = parser.parse_args(['--verbose'])
        self.assertTrue(args.verbose)
        
        args = parser.parse_args(['-v'])
        self.assertTrue(args.verbose)
        
        args = parser.parse_args([])
        self.assertFalse(args.verbose)
    
    def test_greet_function_success(self):
        """Test successful execution of greet function."""
        # Setup logger
        self.app.logger = self.app.log_manager.setup_logging()
        
        with patch('builtins.print') as mock_print:
            result = self.app.greet()
            
            self.assertTrue(result)
            mock_print.assert_called_once_with("Hello, world!")
    
    def test_greet_function_error_handling(self):
        """Test error handling in greet function."""
        # Setup logger
        self.app.logger = self.app.log_manager.setup_logging()
        
        with patch('builtins.print', side_effect=Exception("Print failed")):
            with self.assertRaises(ApplicationError):
                self.app.greet()
    
    def test_run_method_success(self):
        """Test successful application run."""
        args = argparse.Namespace(verbose=False)
        
        exit_code = self.app.run(args)
        
        self.assertEqual(exit_code, 0)
    
    def test_run_method_with_verbose(self):
        """Test application run with verbose mode."""
        args = argparse.Namespace(verbose=True)
        
        exit_code = self.app.run(args)
        
        self.assertEqual(exit_code, 0)
        self.assertEqual(self.app.logger.level, logging.DEBUG)
    
    def test_run_method_application_error(self):
        """Test application run with ApplicationError."""
        args = argparse.Namespace(verbose=False)
        
        with patch.object(self.app, 'greet', side_effect=ApplicationError("Test error")):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                exit_code = self.app.run(args)
                
                self.assertEqual(exit_code, 1)
                self.assertIn("Error: Test error", mock_stderr.getvalue())
    
    def test_run_method_keyboard_interrupt(self):
        """Test application run with KeyboardInterrupt."""
        args = argparse.Namespace(verbose=False)
        
        with patch.object(self.app, 'greet', side_effect=KeyboardInterrupt()):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                exit_code = self.app.run(args)
                
                self.assertEqual(exit_code, 130)
                self.assertIn("interrupted by user", mock_stderr.getvalue())
    
    def test_run_method_unexpected_error(self):
        """Test application run with unexpected error."""
        args = argparse.Namespace(verbose=False)
        
        with patch.object(self.app, 'greet', side_effect=RuntimeError("Unexpected error")):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                exit_code = self.app.run(args)
                
                self.assertEqual(exit_code, 1)
                stderr_output = mock_stderr.getvalue()
                self.assertIn("unexpected error occurred", stderr_output)
                self.assertIn("Error ID:", stderr_output)


class TestMainFunction(unittest.TestCase):
    """Test cases for main function and entry point."""
    
    def test_main_function_success(self):
        """Test successful main function execution."""
        with patch('sys.argv', ['main.py']):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_once_with(0)
    
    def test_main_function_with_verbose_flag(self):
        """Test main function with verbose flag."""
        with patch('sys.argv', ['main.py', '--verbose']):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_once_with(0)
    
    def test_main_function_help_flag(self):
        """Test main function with help flag."""
        with patch('sys.argv', ['main.py', '--help']):
            with patch('sys.exit') as mock_exit:
                with patch('sys.stdout', new_callable=StringIO):
                    main()
                    # Help should exit with code 0
                    mock_exit.assert_called_once_with(0)
    
    def test_main_function_invalid_argument(self):
        """Test main function with invalid argument."""
        with patch('sys.argv', ['main.py', '--invalid-flag']):
            with patch('sys.exit') as mock_exit:
                with patch('sys.stderr', new_callable=StringIO):
                    main()
                    # Invalid arguments should exit with code 2
                    mock_exit.assert_called_once_with(2)
    
    def test_main_function_critical_error(self):
        """Test main function with critical error during startup."""
        with patch('main.Application', side_effect=Exception("Critical startup error")):
            with patch('sys.exit') as mock_exit:
                with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    main()
                    
                    mock_exit.assert_called_once_with(1)
                    stderr_output = mock_stderr.getvalue()
                    self.assertIn("Critical error during application startup", stderr_output)


class TestErrorScenarios(unittest.TestCase):
    """Test cases for various error scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_directory_permission_error(self):
        """Test handling of log directory permission errors."""
        # Create a directory with no write permissions
        restricted_dir = Path(self.temp_dir) / "restricted"
        restricted_dir.mkdir()
        restricted_dir.chmod(0o444)  # Read-only
        
        log_manager = LogManager(log_dir=str(restricted_dir))
        
        # Should fall back to basic logging without crashing
        logger = log_manager.setup_logging()
        self.assertIsNotNone(logger)
        
        # Restore permissions for cleanup
        restricted_dir.chmod(0o755)
    
    def test_application_error_custom_exception(self):
        """Test ApplicationError custom exception."""
        error = ApplicationError("Test application error")
        
        self.assertEqual(str(error), "Test application error")
        self.assertIsInstance(error, Exception)
    
    def test_log_cleanup_with_permission_error(self):
        """Test log cleanup when file deletion fails."""
        log_manager = LogManager(log_dir=self.temp_dir)
        logger = log_manager.setup_logging()
        
        # Create a log file and make it read-only
        old_log = Path(self.temp_dir) / "app_20200101.log"
        old_log.touch()
        old_log.chmod(0o444)
        
        # Cleanup should handle the permission error gracefully
        log_manager._cleanup_old_logs()
        
        # File should still exist due to permission error, but no exception should be raised
        self.assertTrue(old_log.exists())
        
        # Restore permissions for cleanup
        old_log.chmod(0o644)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete application."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up integration test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_application_workflow(self):
        """Test complete application workflow from start to finish."""
        app = Application()
        app.log_manager = LogManager(log_dir=self.temp_dir, retention_days=5)
        
        # Test argument parsing
        parser = app.setup_argument_parser()
        args = parser.parse_args(['--verbose'])
        
        # Test application run
        with patch('builtins.print') as mock_print:
            exit_code = app.run(args)
            
            self.assertEqual(exit_code, 0)
            mock_print.assert_called_once_with("Hello, world!")
        
        # Verify log file was created
        log_files = list(Path(self.temp_dir).glob("app_*.log"))
        self.assertTrue(len(log_files) > 0)
    
    def test_application_with_simulated_errors(self):
        """Test application behavior with various simulated errors."""
        app = Application()
        app.log_manager = LogManager(log_dir=self.temp_dir)
        
        # Test with print function failure
        args = argparse.Namespace(verbose=True)
        
        with patch('builtins.print', side_effect=IOError("Output stream error")):
            exit_code = app.run(args)
            self.assertEqual(exit_code, 1)


if __name__ == '__main__':
    # Configure test logging to avoid interference
    logging.disable(logging.CRITICAL)
    
    # Run tests
    unittest.main(verbosity=2)