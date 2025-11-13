"""
Configuration loader for agents and tasks.
Loads YAML configuration files and provides easy access to settings.
"""

import yaml
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Singleton configuration loader"""
    
    _instance = None
    _agents_config = None
    _tasks_config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_configs()
        return cls._instance
    
    def _load_configs(self):
        """Load all configuration files"""
        config_dir = Path(__file__).parent
        
        # Load agents config
        agents_path = config_dir / 'agents_config.yaml'
        with open(agents_path, 'r', encoding='utf-8') as f:
            self._agents_config = yaml.safe_load(f)
        
        # Load tasks config
        tasks_path = config_dir / 'tasks_config.yaml'
        with open(tasks_path, 'r', encoding='utf-8') as f:
            self._tasks_config = yaml.safe_load(f)
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        return self._agents_config['agents'].get(agent_name, {})
    
    def get_task_config(self, task_name: str) -> Dict[str, Any]:
        """Get configuration for a specific task"""
        return self._tasks_config['tasks'].get(task_name, {})
    
    def get_task_description(self, task_name: str, **kwargs) -> str:
        """Get task description with variable substitution"""
        task_config = self.get_task_config(task_name)
        description = task_config.get('description', '')
        
        # Replace placeholders with provided values
        return description.format(**kwargs)
    
    def get_task_expected_output(self, task_name: str) -> str:
        """Get expected output for a task"""
        task_config = self.get_task_config(task_name)
        return task_config.get('expected_output', '')
    
    def get_categories(self) -> list:
        """Get available activity categories"""
        return self._tasks_config.get('categories', {}).get('available', [])
    
    def get_interest_mapping(self) -> Dict[str, list]:
        """Get mapping of interests to categories"""
        return self._tasks_config.get('categories', {}).get('interest_mapping', {})
    
    @property
    def agents(self) -> Dict[str, Any]:
        """Get all agent configurations"""
        return self._agents_config.get('agents', {})
    
    @property
    def tasks(self) -> Dict[str, Any]:
        """Get all task configurations"""
        return self._tasks_config.get('tasks', {})


# Global config instance
config = Config()
