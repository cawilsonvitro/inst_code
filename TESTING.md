# Test Infrastructure for Instrument Control Suite

This directory contains comprehensive test coverage for the instrument control suite.

## Running Tests

### Run All Tests
```bash
python3 run_tests.py
```

### Run Specific Test Module
```bash
python3 run_tests.py test_config
python3 run_tests.py test_launcher
python3 run_tests.py test_basic
python3 run_tests.py test_integration
```

### Run Individual Test Classes
```bash
python3 -m unittest test_config.TestConfigurationLoading -v
python3 -m unittest test_launcher.TestLauncherUtilities -v
python3 -m unittest test_basic.TestBasicFunctionality -v
python3 -m unittest test_integration.TestLauncherIntegration -v
```

## Test Coverage

### test_config.py
- **TestConfigurationLoading**: Tests configuration file loading and validation
- **TestConfigurationUtilities**: Tests configuration utility functions

### test_launcher.py  
- **TestLauncherUtilities**: Tests launcher utility functions without external dependencies
- **TestLauncherErrorHandling**: Tests error handling in launcher
- **TestConstraintsFile**: Tests constraints file handling

### test_basic.py
- **TestBasicFunctionality**: Tests basic functionality without external dependencies
- **TestPathHandling**: Tests path handling and file operations
- **TestConfigValidation**: Tests configuration validation beyond just loading
- **TestErrorRecovery**: Tests error recovery and graceful degradation

### test_integration.py
- **TestLauncherIntegration**: Integration tests for launcher functionality
- **TestSystemIntegration**: Tests system-level integration
- **TestMockInstrumentConnections**: Mock tests for instrument connections

## Test Areas Covered

### Configuration Management
- ✅ JSON file loading and validation
- ✅ Required sections presence
- ✅ IP address to tool mapping
- ✅ Database configuration structure
- ✅ Error handling for invalid/missing configs

### Launcher Functionality
- ✅ IP address detection
- ✅ Tool selection logic
- ✅ File path construction
- ✅ Virtual environment path handling
- ✅ Cross-platform compatibility
- ✅ Argument parsing

### Path Handling
- ✅ Cross-platform path normalization
- ✅ Virtual environment detection
- ✅ File system permissions
- ✅ Path resolution

### System Integration
- ✅ Python environment compatibility
- ✅ Standard library availability
- ✅ File structure integrity
- ✅ Error recovery mechanisms

### Mock Instrument Testing
- ✅ TCP connection simulation
- ✅ Instrument configuration validation
- ✅ Network error handling

## Fixes Applied

### Cross-Platform Compatibility
- Fixed launcher.py to use `os.path.join()` instead of hardcoded Windows paths
- Fixed virtual environment path detection for Unix/Linux systems
- Fixed path separator issues (`//` → proper path joining)

### Bug Fixes
- Fixed assignment operator bug in launcher.py (line 98: `==` → `=`)
- Improved error handling for missing configuration files
- Enhanced path normalization for better cross-platform support

## Test Statistics
- **Total Tests**: 37
- **Success Rate**: 100%
- **Coverage Areas**: 8 major components
- **Test Files**: 4 comprehensive test modules

## Dependencies

The tests are designed to run with minimal dependencies:
- Python 3.x standard library
- unittest module (built-in)
- No external packages required for basic testing

## Future Test Enhancements

Potential areas for additional testing when dependencies are available:
- Full GUI testing with actual Tkinter components
- Real TCP server testing with network dependencies
- Instrument driver testing with hardware mocks
- Database integration testing with SQL dependencies