"""
Tests for the prompt management system.
"""

import pytest
import tempfile
import os
from src.prompts.prompt_manager import PromptManager


class TestPromptManager:
    """Test cases for PromptManager."""
    
    def test_load_config(self):
        """Test loading configuration from YAML file."""
        manager = PromptManager()
        config = manager.config
        
        assert 'prompts' in config
        assert 'comprehensive' in config['prompts']
        assert 'bullet_points' in config['prompts']
        assert 'key_points' in config['prompts']
        assert 'structured' in config['prompts']
    
    def test_get_available_prompts(self):
        """Test getting list of available prompts."""
        manager = PromptManager()
        prompts = manager.get_available_prompts()
        
        assert 'comprehensive' in prompts
        assert 'bullet_points' in prompts
        assert 'key_points' in prompts
        assert 'structured' in prompts
        
        # Check descriptions are present
        assert isinstance(prompts['comprehensive'], str)
        assert len(prompts['comprehensive']) > 0
    
    def test_get_prompt_with_variables(self):
        """Test getting a prompt with variable substitution."""
        manager = PromptManager()
        
        variables = {
            'text': 'This is a test text to summarize.',
            'max_length': 200
        }
        
        prompt = manager.get_prompt('comprehensive', variables)
        
        assert 'This is a test text to summarize.' in prompt
        assert '200' in prompt
        assert '{text}' not in prompt  # Variables should be substituted
        assert '{max_length}' not in prompt
    
    def test_get_prompt_missing_variable(self):
        """Test error handling for missing required variables."""
        manager = PromptManager()
        
        variables = {
            'text': 'Test text'
            # Missing max_length
        }
        
        with pytest.raises(ValueError):
            manager.get_prompt('comprehensive', variables)
    
    def test_unknown_prompt_key(self):
        """Test error handling for unknown prompt keys."""
        manager = PromptManager()
        
        variables = {'text': 'Test', 'max_length': 100}
        
        with pytest.raises(ValueError):
            manager.get_prompt('unknown_prompt', variables)
    
    def test_get_variable_info(self):
        """Test getting variable information for a prompt."""
        manager = PromptManager()
        
        var_info = manager.get_variable_info('comprehensive')
        
        assert 'text' in var_info
        assert 'max_length' in var_info
        
        # Check variable details (all variables are now required and type 'str')
        assert var_info['text']['required'] is True
        assert var_info['max_length']['required'] is True
        assert var_info['max_length']['type'] == 'str'
        assert var_info['max_length']['default'] is None
    
    def test_get_default_prompt(self):
        """Test getting the default prompt key."""
        manager = PromptManager()
        default = manager.get_default_prompt()
        
        assert default in ['comprehensive', 'bullet_points', 'key_points', 'structured']


if __name__ == '__main__':
    pytest.main([__file__]) 