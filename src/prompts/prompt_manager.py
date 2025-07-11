"""
Prompt management system for AI summarization.
Handles loading prompts from files and variable substitution.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class PromptManager:
    """Manages prompts loaded from files with variable substitution."""
    
    def __init__(self, config_path: str = "src/prompts/config.yaml"):
        """
        Initialize prompt manager.
        
        Args:
            config_path: Path to the prompt configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._prompt_cache = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load prompt configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in prompt configuration: {e}")
    
    def _load_prompt_file(self, prompt_key: str) -> str:
        """Load prompt content from file."""
        if prompt_key not in self.config.get('prompts', {}):
            raise ValueError(f"Unknown prompt key: {prompt_key}")
        
        prompt_config = self.config['prompts'][prompt_key]
        file_path = prompt_config['path']
        
        # Check cache first
        if file_path in self._prompt_cache:
            return self._prompt_cache[file_path]
        
        # Load from file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self._prompt_cache[file_path] = content
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
    
    def get_prompt(self, prompt_key: str, variables: Dict[str, Any]) -> str:
        """
        Get a prompt with variables substituted.
        
        Args:
            prompt_key: Key identifying the prompt
            variables: Dictionary of variables to substitute
            
        Returns:
            Prompt text with variables substituted
        """
        # Load prompt template
        prompt_template = self._load_prompt_file(prompt_key)
        
        # Validate required variables
        self._validate_variables(prompt_key, variables)
        
        # Substitute variables
        try:
            return prompt_template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing required variable in prompt '{prompt_key}': {e}")
        except Exception as e:
            raise ValueError(f"Error substituting variables in prompt '{prompt_key}': {e}")
    
    def _validate_variables(self, prompt_key: str, variables: Dict[str, Any]) -> None:
        """Validate that all required variables are provided."""
        if prompt_key not in self.config.get('prompts', {}):
            return
        
        prompt_config = self.config['prompts'][prompt_key]
        required_vars = prompt_config.get('variables', [])
        
        for var_name in required_vars:
            if var_name not in variables:
                raise ValueError(f"Required variable '{var_name}' not provided for prompt '{prompt_key}'")
    
    def get_available_prompts(self) -> Dict[str, str]:
        """Get list of available prompts with descriptions."""
        prompts = {}
        for key, config in self.config.get('prompts', {}).items():
            prompts[key] = config.get('description', 'No description available')
        return prompts
    
    def get_default_prompt(self) -> str:
        """Get the default prompt key."""
        return self.config.get('default_prompt', 'comprehensive')
    
    def get_variable_info(self, prompt_key: str) -> Dict[str, Any]:
        """Get information about variables for a specific prompt."""
        if prompt_key not in self.config.get('prompts', {}):
            raise ValueError(f"Unknown prompt key: {prompt_key}")
        
        prompt_config = self.config['prompts'][prompt_key]
        variables = prompt_config.get('variables', [])
        
        var_info = {}
        for var_name in variables:
            var_info[var_name] = {
                'description': 'See README.md for variable documentation',
                'required': True,  # All variables are required since we removed the config
                'default': None,
                'type': 'str'
            }
        
        return var_info
    
    def add_prompt(self, key: str, file_path: str, description: str, variables: list) -> None:
        """
        Add a new prompt to the configuration.
        
        Args:
            key: Unique key for the prompt
            file_path: Path to the prompt file
            description: Description of the prompt
            variables: List of variable names used in the prompt
        """
        if key in self.config.get('prompts', {}):
            raise ValueError(f"Prompt key '{key}' already exists")
        
        # Add to config
        if 'prompts' not in self.config:
            self.config['prompts'] = {}
        
        self.config['prompts'][key] = {
            'path': file_path,
            'description': description,
            'variables': variables
        }
        
        # Save updated config
        self._save_config()
    
    def _save_config(self) -> None:
        """Save the current configuration back to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ValueError(f"Error saving prompt configuration: {e}")
    
    def reload_config(self) -> None:
        """Reload configuration from file and clear cache."""
        self.config = self._load_config()
        self._prompt_cache.clear()
    
 