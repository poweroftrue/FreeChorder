"""
Configuration management for FreeChorder
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Manages FreeChorder configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration."""
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / '.config' / 'freechorder' / 'config.yaml'
        
        # Default configuration
        self.defaults = {
            'version': '1.0',
            'karabiner': {
                'config_path': '~/.config/karabiner/karabiner.json',
                'profile_name': 'FreeChorder',
                'reload_command': '/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli --reload-karabiner-config'
            },
            'impulse': {
                'enabled': True,
                'trigger_key': 'cmd+shift+i',
                'chord_timeout_ms': 100,
                'min_chord_size': 2,
                'sensitivity_scaling': {
                    '2_keys': 50,   # Sensitivity for 2-key chords
                    '3_keys': 75,   # Sensitivity for 3-key chords
                    '4_keys': 100,  # Sensitivity for 4-key chords
                    '5_plus_keys': 125  # Sensitivity for 5+ key chords
                },
                'audio_feedback': True
            },
            'ui': {
                'color_output': True,
                'page_size': 20,
                'date_format': '%Y-%m-%d %H:%M'
            },
            'storage': {
                'chord_file': '~/.config/freechorder/chords.yaml',
                'backup_count': 10,
                'auto_backup': True
            }
        }
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.config_path.exists():
            # Create default config
            self._save_config(self.defaults)
            return self.defaults.copy()
        
        try:
            with open(self.config_path, 'r') as f:
                loaded_config = yaml.safe_load(f) or {}
            
            # Merge with defaults
            return self._merge_configs(self.defaults, loaded_config)
            
        except Exception as e:
            print(f"Warning: Failed to load config: {str(e)}")
            return self.defaults.copy()
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"Warning: Failed to save config: {str(e)}")
    
    def _merge_configs(self, defaults: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults."""
        result = defaults.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-separated key."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save configuration
        self._save_config(self.config)
    
    @property
    def chord_file(self) -> str:
        """Get chord file path."""
        path = self.get('storage.chord_file', '~/.config/freechorder/chords.yaml')
        return os.path.expanduser(path)
    
    @property
    def karabiner_config_path(self) -> str:
        """Get Karabiner config path."""
        path = self.get('karabiner.config_path', '~/.config/karabiner/karabiner.json')
        return os.path.expanduser(path)
    
    @property
    def karabiner_profile_name(self) -> str:
        """Get Karabiner profile name."""
        return self.get('karabiner.profile_name', 'FreeChorder')
    
    @property
    def impulse_enabled(self) -> bool:
        """Check if impulse mode is enabled."""
        return self.get('impulse.enabled', True)
    
    @property
    def impulse_trigger_key(self) -> str:
        """Get impulse mode trigger key."""
        return self.get('impulse.trigger_key', 'cmd+shift+i')
    
    @property
    def chord_timeout_ms(self) -> int:
        """Get chord timeout in milliseconds."""
        return self.get('impulse.chord_timeout_ms', 100)
    
    @property
    def min_chord_size(self) -> int:
        """Get minimum chord size."""
        return self.get('impulse.min_chord_size', 2)
    
    @property
    def sensitivity_map(self) -> Dict[int, int]:
        """Get sensitivity scaling map for different chord lengths."""
        scaling = self.get('impulse.sensitivity_scaling', {})
        return {
            2: scaling.get('2_keys', 50),
            3: scaling.get('3_keys', 75),
            4: scaling.get('4_keys', 100),
            5: scaling.get('5_plus_keys', 125)
        }
