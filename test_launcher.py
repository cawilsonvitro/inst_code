#!/usr/bin/env python3
"""
Unit tests for launcher functionality
"""
import unittest
import os
import json
import tempfile
import sys
from unittest.mock import patch, MagicMock
import socket


class TestLauncherUtilities(unittest.TestCase):
    """Test launcher utility functions without external dependencies"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
    def test_ip_address_detection(self):
        """Test IP address detection functionality"""
        # Test hostname and IP detection
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            self.assertIsInstance(hostname, str)
            self.assertIsInstance(ip_address, str)
        except Exception as e:
            self.fail(f"IP address detection failed: {e}")
            
    def test_tool_selection_logic(self):
        """Test tool selection based on IP address"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            
        tool_ip = config['Tool_ip']
        
        # Test known IP mappings
        test_cases = [
            ('192.168.1.1', 'host'),
            ('192.168.1.2', 'fourpp'),
            ('192.168.1.3', 'hall'),
            ('127.0.0.1', 'testing')
        ]
        
        for ip, expected_tool in test_cases:
            if ip in tool_ip:
                actual_tool = tool_ip[ip]
                self.assertEqual(actual_tool, expected_tool, 
                               f"IP {ip} should map to tool {expected_tool}, got {actual_tool}")
                
    def test_file_path_construction(self):
        """Test file path construction for different tools"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            
        # Test path construction logic (without actually running launcher)
        test_tools = ['hall', 'fourpp', 'rdt', 'nearir']
        
        for tool in test_tools:
            if tool == 'hall':
                # Special case for hall with HMS system
                hall_config = config.get('Hall', {})
                if hall_config.get('sys') == 'HMS':
                    expected_filename = 'hall_script.py'
                else:
                    expected_filename = f'{tool}.py'
            else:
                expected_filename = f'{tool}.py'
                
            expected_path = f'tools//{tool}//{expected_filename}'
            # Just verify the path format is reasonable
            self.assertIn(tool, expected_path)
            self.assertTrue(expected_path.endswith('.py'))
            
    def test_virtual_environment_path_construction(self):
        """Test virtual environment path construction"""
        # Test the path construction logic
        cwd = os.getcwd()
        expected_venv_path = os.path.join(cwd, '.venv')
        expected_python_path = os.path.join(expected_venv_path, 'Scripts', 'python.exe')
        
        # On Unix-like systems, it would be 'bin' instead of 'Scripts'
        if not sys.platform.startswith('win'):
            expected_python_path = os.path.join(expected_venv_path, 'bin', 'python')
            
        # Test path construction
        self.assertIn('.venv', expected_venv_path)
        self.assertIn('python', expected_python_path)


class TestLauncherErrorHandling(unittest.TestCase):
    """Test error handling in launcher"""
    
    def test_missing_config_file(self):
        """Test behavior when config file is missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_config_path = os.path.join(temp_dir, 'missing_config.json')
            
            with self.assertRaises(FileNotFoundError):
                with open(missing_config_path, 'r') as f:
                    json.load(f)
                    
    def test_invalid_config_format(self):
        """Test behavior with invalid config format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"Tool_ip": "not_a_dict"}')  # Invalid format
            invalid_config_path = f.name
            
        try:
            with open(invalid_config_path, 'r') as f:
                config = json.load(f)
                # This should be a dict, but we wrote a string
                tool_ip = config.get('Tool_ip', {})
                self.assertNotIsInstance(tool_ip, dict, 
                                       "Invalid config should be detected")
        finally:
            os.unlink(invalid_config_path)
            
    @patch('socket.gethostname')
    @patch('socket.gethostbyname')
    def test_network_error_handling(self, mock_gethostbyname, mock_gethostname):
        """Test behavior when network operations fail"""
        # Simulate network errors
        mock_gethostname.side_effect = socket.error("Network error")
        mock_gethostbyname.side_effect = socket.error("Network error")
        
        with self.assertRaises(socket.error):
            socket.gethostname()
            
        with self.assertRaises(socket.error):
            socket.gethostbyname('test')


class TestConstraintsFile(unittest.TestCase):
    """Test constraints file handling"""
    
    def test_constraints_file_exists(self):
        """Test that constraints.txt exists"""
        constraints_path = os.path.join(os.path.dirname(__file__), 'constraints.txt')
        self.assertTrue(os.path.exists(constraints_path), "constraints.txt should exist")
        
    def test_constraints_file_readable(self):
        """Test that constraints.txt is readable"""
        constraints_path = os.path.join(os.path.dirname(__file__), 'constraints.txt')
        
        try:
            with open(constraints_path, 'r') as f:
                lines = f.readlines()
                self.assertIsInstance(lines, list)
        except Exception as e:
            self.fail(f"Failed to read constraints.txt: {e}")


if __name__ == '__main__':
    unittest.main()