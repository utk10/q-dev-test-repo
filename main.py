#!/usr/bin/env python3
"""
Main application with comprehensive error handling and logging.

This module provides a production-ready application with:
- Comprehensive error handling and logging
- Command line argument parsing
- Log rotation and retention management
- User-friendly error messages
"""

import argparse
import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path


class ApplicationError(Exception):
    """Custom exception for application-specific errors."""
    pass


class LogManager:
    """Manages logging configuration, rotation, and cleanup."""
    
    def __init__(self, log_dir="logs", retention_days=30):
        self.log_dir = Path(log_dir)
        self.retention_days = retention_days
        self.logger = None
        
    def setup_logging(self, verbose=False):
        """Configure logging with file rotation and console output."""
        try:
            # Ensure log directory exists
            self.log_dir.mkdir(exist_ok=True)
            
            # Configure root logger
            self.logger = logging.getLogger('main_app')
            self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
            
            # Clear any existing handlers
            self.logger.handlers.clear()
            
            # Create formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            simple_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            
            # File handler with daily rotation
            log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.handlers.TimedRotatingFileHandler(
                log_file,
                when='midnight',
                interval=1,
                backupCount=self.retention_days,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)
            
            # Clean up old log files
            self._cleanup_old_logs()
            
            self.logger.info("Logging system initialized successfully")
            return self.logger
            
        except Exception as e:
            # Fallback to basic logging if setup fails
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            logging.error(f"Failed to setup advanced logging: {e}")
            return logging.getLogger('main_app')
    
    def _cleanup_old_logs(self):
        """Remove log files older than retention period."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            for log_file in self.log_dir.glob("app_*.log*"):
                try:
                    file_stat = log_file.stat()
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        if self.logger:
                            self.logger.debug(f"Removed old log file: {log_file}")
                            
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Failed to process log file {log_file}: {e}")
                        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to cleanup old logs: {e}")


class Application:
    """Main application class with error handling and logging."""
    
    def __init__(self):
        self.log_manager = LogManager()
        self.logger = None
        
    def setup_argument_parser(self):
        """Configure command line argument parsing."""
        parser = argparse.ArgumentParser(
            description="A simple greeting application with comprehensive logging and error handling.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python main.py                    # Run with default settings
  python main.py --verbose          # Run with verbose logging
  python main.py -v                 # Short form of verbose
            """
        )
        
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Enable verbose logging (DEBUG level)'
        )
        
        return parser
    
    def greet(self):
        """Core greeting functionality with error handling."""
        try:
            self.logger.info("Executing greeting function")
            message = "Hello, world!"
            print(message)
            self.logger.info(f"Greeting displayed: {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in greeting function: {e}")
            self.logger.debug(f"Greeting function traceback: {traceback.format_exc()}")
            raise ApplicationError(f"Failed to display greeting: {str(e)}")
    
    def run(self, args):
        """Main application execution with comprehensive error handling."""
        try:
            # Initialize logging
            self.logger = self.log_manager.setup_logging(verbose=args.verbose)
            self.logger.info("Application starting")
            self.logger.debug(f"Command line arguments: {vars(args)}")
            
            # Execute core functionality
            success = self.greet()
            
            if success:
                self.logger.info("Application completed successfully")
                return 0
            else:
                self.logger.error("Application completed with errors")
                return 1
                
        except ApplicationError as e:
            # Handle application-specific errors
            self.logger.error(f"Application error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1
            
        except KeyboardInterrupt:
            # Handle user interruption gracefully
            self.logger.info("Application interrupted by user")
            print("\nApplication interrupted by user.", file=sys.stderr)
            return 130
            
        except Exception as e:
            # Handle unexpected errors
            error_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.logger.error(f"Unexpected error [{error_id}]: {e}")
            self.logger.debug(f"Unexpected error traceback [{error_id}]: {traceback.format_exc()}")
            
            print(f"An unexpected error occurred. Error ID: {error_id}", file=sys.stderr)
            print("Please check the log files for more details.", file=sys.stderr)
            return 1
            
        finally:
            # Cleanup and final logging
            if self.logger:
                self.logger.info("Application shutdown")


def main():
    """Application entry point with argument parsing and error handling."""
    try:
        # Create application instance
        app = Application()
        
        # Parse command line arguments
        parser = app.setup_argument_parser()
        args = parser.parse_args()
        
        # Run application
        exit_code = app.run(args)
        sys.exit(exit_code)
        
    except SystemExit:
        # Re-raise SystemExit to preserve exit codes
        raise
        
    except Exception as e:
        # Handle errors in main setup
        print(f"Critical error during application startup: {e}", file=sys.stderr)
        print("Unable to initialize logging system.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
