#!/usr/bin/env python3
"""
Demo script to test the enhanced main.py application.
This script demonstrates the error handling and logging capabilities.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Exit Code: {result.returncode}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Command timed out!")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def check_log_files():
    """Check if log files were created."""
    print(f"\n{'='*60}")
    print("Checking Log Files")
    print(f"{'='*60}")
    
    logs_dir = Path("logs")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        if log_files:
            print(f"Found {len(log_files)} log file(s):")
            for log_file in log_files:
                print(f"  - {log_file}")
                
                # Show last few lines of the log
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"    Last few lines:")
                            for line in lines[-3:]:
                                print(f"    {line.strip()}")
                except Exception as e:
                    print(f"    Error reading log file: {e}")
        else:
            print("No log files found.")
    else:
        print("Logs directory not found.")

def main():
    """Run demonstration tests."""
    print("Enhanced Main.py Application Demo")
    print("This demo tests the error handling and logging capabilities.")
    
    # Change to the workspace directory
    os.chdir('/workspace')
    
    # Test 1: Basic execution
    run_command("python main.py", "Basic application execution")
    
    # Test 2: Verbose mode
    run_command("python main.py --verbose", "Verbose mode execution")
    
    # Test 3: Help command
    run_command("python main.py --help", "Help command")
    
    # Test 4: Invalid argument (should show error)
    run_command("python main.py --invalid", "Invalid argument handling")
    
    # Check log files
    check_log_files()
    
    # Test 5: Run unit tests
    run_command("python tests/test_main.py", "Unit tests execution")
    
    print(f"\n{'='*60}")
    print("Demo completed!")
    print("Check the logs/ directory for generated log files.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()