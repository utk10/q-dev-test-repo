# q-dev-test-repo

A production-ready Python application with comprehensive error handling, logging, and monitoring capabilities.

## Features

- **Comprehensive Error Handling**: Try-catch blocks around all main execution paths
- **Advanced Logging System**: Multi-level logging (INFO, ERROR, DEBUG) with file rotation
- **Log Management**: Daily log rotation with 30-day retention policy
- **Command Line Interface**: Argument parsing with verbose mode support
- **User-Friendly Error Messages**: Graceful error handling without exposing sensitive information
- **Production Ready**: Proper application structure with monitoring capabilities
- **Unit Testing**: Comprehensive test suite covering error scenarios

## Installation

No external dependencies required. The application uses only Python standard library modules.

```bash
git clone <repository-url>
cd q-dev-test-repo
```

## Usage

### Basic Usage

```bash
python main.py
```

### Verbose Mode

Enable detailed logging and debug information:

```bash
python main.py --verbose
# or
python main.py -v
```

### Help

Display usage information:

```bash
python main.py --help
```

## Logging

### Log Files

- **Location**: `logs/` directory
- **Format**: `app_YYYYMMDD.log` (e.g., `app_20231215.log`)
- **Rotation**: Daily at midnight
- **Retention**: 30 days (older files are automatically deleted)

### Log Levels

- **INFO**: General application flow and status messages
- **ERROR**: Error conditions and exceptions
- **DEBUG**: Detailed diagnostic information (enabled with `--verbose`)

### Log Format

**File logs** (detailed):
```
2023-12-15 10:30:45,123 - main_app - INFO - greet:145 - Executing greeting function
```

**Console logs** (simplified):
```
2023-12-15 10:30:45,123 - INFO - Application starting
```

## Error Handling

The application implements multiple layers of error handling:

### Application Errors
- Custom `ApplicationError` exceptions for business logic failures
- User-friendly error messages displayed to console
- Technical details logged to files with unique error IDs

### System Errors
- Graceful handling of system interruptions (Ctrl+C)
- Proper cleanup and resource management
- Fallback mechanisms for logging system failures

### Example Error Output

```bash
$ python main.py
Error: Failed to display greeting: Output stream error

# Check logs for details:
$ cat logs/app_20231215.log
2023-12-15 10:30:45,123 - main_app - ERROR - Unexpected error [20231215_103045]: Output stream error
```

## Testing

### Running Tests

```bash
python -m pytest tests/ -v
# or
python tests/test_main.py
```

### Test Coverage

The test suite covers:
- Logging system functionality and configuration
- Error handling scenarios and edge cases
- Command line argument parsing
- Log rotation and cleanup mechanisms
- Integration testing of complete workflows
- Permission and file system error scenarios

### Example Test Run

```bash
$ python tests/test_main.py
test_application_error_custom_exception (__main__.TestErrorScenarios) ... ok
test_argument_parser_setup (__main__.TestApplication) ... ok
test_cleanup_old_logs (__main__.TestLogManager) ... ok
test_full_application_workflow (__main__.TestIntegration) ... ok
test_greet_function_error_handling (__main__.TestApplication) ... ok
test_greet_function_success (__main__.TestApplication) ... ok
test_log_file_creation (__main__.TestLogManager) ... ok
test_log_manager_initialization (__main__.TestLogManager) ... ok
test_main_function_success (__main__.TestMainFunction) ... ok
test_run_method_application_error (__main__.TestApplication) ... ok
test_run_method_keyboard_interrupt (__main__.TestApplication) ... ok
test_run_method_success (__main__.TestApplication) ... ok
test_run_method_unexpected_error (__main__.TestApplication) ... ok
test_setup_logging_creates_directory (__main__.TestLogManager) ... ok
test_setup_logging_normal_mode (__main__.TestLogManager) ... ok
test_setup_logging_verbose_mode (__main__.TestLogManager) ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.123s

OK
```

## Architecture

### Components

1. **LogManager**: Handles logging configuration, file rotation, and cleanup
2. **Application**: Main application class with error handling and business logic
3. **ApplicationError**: Custom exception class for application-specific errors
4. **main()**: Entry point with argument parsing and critical error handling

### Directory Structure

```
q-dev-test-repo/
├── main.py              # Main application with enhanced error handling
├── README.md            # This documentation
├── requirements.txt     # Dependencies (none required)
├── logs/               # Log files directory
│   ├── .gitkeep        # Ensures directory exists in git
│   └── app_YYYYMMDD.log # Daily log files
└── tests/              # Test suite
    ├── __init__.py     # Test package
    └── test_main.py    # Comprehensive unit tests
```

## Configuration

### Log Retention

Default: 30 days. Modify in `LogManager.__init__()`:

```python
self.log_manager = LogManager(retention_days=60)  # 60 days retention
```

### Log Directory

Default: `logs/`. Modify in `LogManager.__init__()`:

```python
self.log_manager = LogManager(log_dir="custom_logs")
```

## Production Deployment

### Recommendations

1. **Monitoring**: Set up log monitoring for ERROR level messages
2. **Disk Space**: Monitor `logs/` directory disk usage
3. **Permissions**: Ensure write permissions for log directory
4. **Backup**: Include log files in backup strategy if needed
5. **Security**: Log files may contain sensitive information

### Example Systemd Service

```ini
[Unit]
Description=Q-Dev Test Application
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/q-dev-test-repo
ExecStart=/usr/bin/python3 main.py --verbose
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure write permissions for `logs/` directory
2. **Disk Full**: Check available disk space for log files
3. **Import Errors**: Verify Python 3.6+ is being used

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python main.py --verbose
```

### Log Analysis

Check recent errors:
```bash
tail -f logs/app_$(date +%Y%m%d).log | grep ERROR
```

## Contributing

1. Run tests before submitting changes
2. Follow existing code style and documentation patterns
3. Add tests for new functionality
4. Update README for new features

## License

This project is part of the Amazon Q automation test suite.
