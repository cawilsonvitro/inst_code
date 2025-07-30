#!/usr/bin/env python3
"""
Unit tests for configuration loading and validation
"""
import unittest
import json
import os
import tempfile
from unittest.mock import patch


class TestConfigurationLoading(unittest.TestCase):
    """Test configuration file loading and validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
    def test_config_file_exists(self):
        """Test that config.json exists"""
        self.assertTrue(os.path.exists(self.config_path), "config.json should exist")
        
    def test_config_is_valid_json(self):
        """Test that config.json contains valid JSON"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.fail(f"config.json contains invalid JSON: {e}")
        except Exception as e:
            self.fail(f"Failed to read config.json: {e}")
            
    def test_config_has_required_sections(self):
        """Test that config.json has all required sections"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            
        required_sections = [
            'Tool_ip',
            'Hall',
            'RDT',
            'Database_Config',
            'Tool_pre'
        ]
        
        for section in required_sections:
            self.assertIn(section, config, f"Config should contain {section} section")
            
    def test_tool_ip_mapping_validity(self):
        """Test that Tool_ip mappings are valid"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            
        tool_ip = config.get('Tool_ip', {})
        self.assertIsInstance(tool_ip, dict, "Tool_ip should be a dictionary")
        
        # Check that required tools are mapped
        expected_tools = ['host', 'fourpp', 'hall', 'rdt', 'nearir']
        mapped_tools = list(tool_ip.values())
        
        for tool in expected_tools:
            self.assertIn(tool, mapped_tools, f"Tool '{tool}' should be mapped in Tool_ip")
            
        # Check IP address format (basic validation)
        for ip, tool in tool_ip.items():
            self.assertIsInstance(ip, str, f"IP {ip} should be a string")
            self.assertIsInstance(tool, str, f"Tool {tool} should be a string")
            # Basic IP format check
            parts = ip.split('.')
            if ip != '127.0.0.1':  # Allow localhost
                self.assertEqual(len(parts), 4, f"IP {ip} should have 4 parts")
                
    def test_database_config_structure(self):
        """Test that Database_Config has required fields"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            
        db_config = config.get('Database_Config', {})
        required_fields = ['host', 'db', 'driver']
        
        for field in required_fields:
            self.assertIn(field, db_config, f"Database_Config should contain {field}")
            self.assertIsInstance(db_config[field], str, f"Database_Config.{field} should be a string")


class TestConfigurationUtilities(unittest.TestCase):
    """Test configuration utility functions"""
    
    def test_config_loading_with_invalid_file(self):
        """Test behavior when config file is invalid"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON
            invalid_config_path = f.name
            
        try:
            with self.assertRaises(json.JSONDecodeError):
                with open(invalid_config_path, 'r') as f:
                    json.load(f)
        finally:
            os.unlink(invalid_config_path)
            
    def test_config_loading_with_missing_file(self):
        """Test behavior when config file is missing"""
        missing_path = 'nonexistent_config.json'
        
        with self.assertRaises(FileNotFoundError):
            with open(missing_path, 'r') as f:
                json.load(f)


if __name__ == '__main__':
    unittest.main()