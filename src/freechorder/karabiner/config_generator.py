"""
Karabiner-Elements configuration generator
"""

import json
import os
import shutil
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from freechorder.core.chord_manager import Chord


class KarabinerError(Exception):
    """Raised when Karabiner operations fail."""
    pass


class KarabinerBridge:
    """Manages integration with Karabiner-Elements."""
    
    def __init__(self, config_path: Optional[str] = None, chord_timeout_ms: int = 100, sensitivity_map: Optional[Dict[int, int]] = None):
        """Initialize Karabiner bridge."""
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / '.config' / 'karabiner' / 'karabiner.json'
        
        self.profile_name = "FreeChorder"
        self.reload_command = "/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli"
        self.chord_timeout_ms = chord_timeout_ms
        
        # Dynamic sensitivity based on chord length
        # Use provided sensitivity map or defaults
        self.sensitivity_map = sensitivity_map or {
            2: 50,   # Very strict for 2-letter chords
            3: 75,   # Moderately strict for 3-letter chords
            4: 100,  # Default timing for 4-letter chords
            5: 125   # More relaxed for 5+ letter chords
        }
        
        # Track enabled/disabled groups
        self.disabled_groups = self._load_disabled_groups()
        
        # Check if Karabiner is installed
        self._check_karabiner_installed()
    
    def _check_karabiner_installed(self):
        """Check if Karabiner-Elements is installed."""
        if not os.path.exists("/Applications/Karabiner-Elements.app"):
            raise KarabinerError(
                "Karabiner-Elements is not installed. "
                "Please install it from https://karabiner-elements.pqrs.org/"
            )
        
        # Check if config directory exists
        if not self.config_path.parent.exists():
            raise KarabinerError(
                f"Karabiner config directory not found: {self.config_path.parent}"
            )
    
    def _backup_config(self):
        """Create a backup of the current Karabiner configuration."""
        if self.config_path.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.config_path.with_suffix(f'.backup.{timestamp}.json')
            shutil.copy2(self.config_path, backup_path)
            
            # Keep only the last 5 backups
            backups = sorted(self.config_path.parent.glob('karabiner.backup.*.json'))
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    old_backup.unlink()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load current Karabiner configuration."""
        if not self.config_path.exists():
            # Create default configuration
            return {
                "global": {
                    "check_for_updates_on_startup": True,
                    "show_in_menu_bar": True,
                    "show_profile_name_in_menu_bar": False
                },
                "profiles": []
            }
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise KarabinerError(f"Failed to load Karabiner config: {str(e)}")
    
    def _save_config(self, config: Dict[str, Any]):
        """Save Karabiner configuration."""
        try:
            # Pretty print JSON
            json_str = json.dumps(config, indent=2, ensure_ascii=False)
            
            # Write to temporary file first
            temp_path = self.config_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                f.write(json_str)
            
            # Move to actual location
            temp_path.replace(self.config_path)
            
        except Exception as e:
            raise KarabinerError(f"Failed to save Karabiner config: {str(e)}")
    
    def _get_or_create_profile(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get or create the FreeChorder profile."""
        # Look for existing profile
        for profile in config.get('profiles', []):
            if profile.get('name') == self.profile_name:
                return profile
        
        # Create new profile
        profiles = config.get('profiles', [])
        
        # Copy from default profile if exists
        if profiles:
            new_profile = profiles[0].copy()
            new_profile['name'] = self.profile_name
            new_profile['selected'] = False
        else:
            # Create minimal profile
            new_profile = {
                "name": self.profile_name,
                "selected": True,
                "complex_modifications": {
                    "parameters": {
                        "basic.simultaneous_threshold_milliseconds": self.chord_timeout_ms,
                        "basic.to_delayed_action_delay_milliseconds": 500,
                        "basic.to_if_alone_timeout_milliseconds": 1000,
                        "basic.to_if_held_down_threshold_milliseconds": 500
                    },
                    "rules": []
                }
            }
        
        # Ensure complex_modifications exists
        if 'complex_modifications' not in new_profile:
            new_profile['complex_modifications'] = {"rules": []}
        
        profiles.append(new_profile)
        config['profiles'] = profiles
        
        return new_profile
    
    def get_chord_sensitivity(self, chord: Chord) -> int:
        """Get the sensitivity threshold for a chord based on its length."""
        # Count only non-modifier keys
        non_modifier_keys = [key for key in chord.input_keys 
                           if key not in ['cmd', 'shift', 'option', 'control']]
        chord_length = len(non_modifier_keys)
        
        # Return appropriate sensitivity (lower = stricter)
        if chord_length <= 2:
            return self.sensitivity_map[2]
        elif chord_length == 3:
            return self.sensitivity_map[3]
        elif chord_length == 4:
            return self.sensitivity_map[4]
        else:
            return self.sensitivity_map[5]
    
    def generate_rule(self, chord: Chord) -> Dict[str, Any]:
        """Generate a Karabiner rule for a chord."""
        # Get dynamic sensitivity for this chord
        sensitivity = self.get_chord_sensitivity(chord)
        # Create the basic rule structure
        rule = {
            "description": f"FreeChorder: {'+'.join(chord.input_keys)} → {chord.output_text} (sensitivity: {sensitivity}ms)",
            "manipulators": [{
                "type": "basic",
                "from": {
                    "simultaneous": [
                        {"key_code": key} for key in chord.input_keys
                        if key not in ['cmd', 'shift', 'option', 'control']
                    ],
                    "simultaneous_options": {
                        "key_down_order": "insensitive",
                        "key_up_order": "insensitive",
                        "key_up_when": "any"
                    }
                },
                "to": self._generate_output(chord),
                "conditions": [],
                "parameters": {
                    "basic.simultaneous_threshold_milliseconds": sensitivity
                }
            }]
        }
        
        # Add modifiers if present
        modifiers = []
        for key in chord.input_keys:
            if key == 'cmd':
                modifiers.append('command')
            elif key == 'shift':
                modifiers.append('shift')
            elif key == 'option':
                modifiers.append('option')
            elif key == 'control':
                modifiers.append('control')
        
        if modifiers:
            rule['manipulators'][0]['from']['modifiers'] = {
                "mandatory": modifiers
            }
        
        return rule
    
    def _generate_output(self, chord: Chord) -> List[Dict[str, Any]]:
        """Generate output configuration for a chord."""
        if chord.output_type == "text":
            # For text output, we'll use a more reliable method
            # Instead of shell command, we'll type each character
            output = []
            
            # First, clear any existing text (optional)
            # output.append({"key_code": "a", "modifiers": ["command"]})
            # output.append({"key_code": "delete_or_backspace"})
            
            # Type each character
            for char in chord.output_text:
                if char == ' ':
                    output.append({"key_code": "spacebar"})
                elif char == '\n':
                    output.append({"key_code": "return_or_enter"})
                elif char == '\t':
                    output.append({"key_code": "tab"})
                elif char.isalpha():
                    if char.isupper():
                        output.append({
                            "key_code": char.lower(),
                            "modifiers": ["shift"]
                        })
                    else:
                        output.append({"key_code": char})
                elif char.isdigit():
                    output.append({"key_code": char})
                else:
                    # For special characters, we need to map them
                    char_mapping = {
                        '.': {"key_code": "period"},
                        ',': {"key_code": "comma"},
                        ';': {"key_code": "semicolon"},
                        ':': {"key_code": "semicolon", "modifiers": ["shift"]},
                        "'": {"key_code": "quote"},
                        '"': {"key_code": "quote", "modifiers": ["shift"]},
                        '-': {"key_code": "hyphen"},
                        '_': {"key_code": "hyphen", "modifiers": ["shift"]},
                        '=': {"key_code": "equal_sign"},
                        '+': {"key_code": "equal_sign", "modifiers": ["shift"]},
                        '[': {"key_code": "open_bracket"},
                        ']': {"key_code": "close_bracket"},
                        '{': {"key_code": "open_bracket", "modifiers": ["shift"]},
                        '}': {"key_code": "close_bracket", "modifiers": ["shift"]},
                        '\\': {"key_code": "backslash"},
                        '|': {"key_code": "backslash", "modifiers": ["shift"]},
                        '/': {"key_code": "slash"},
                        '?': {"key_code": "slash", "modifiers": ["shift"]},
                        '!': {"key_code": "1", "modifiers": ["shift"]},
                        '@': {"key_code": "2", "modifiers": ["shift"]},
                        '#': {"key_code": "3", "modifiers": ["shift"]},
                        '$': {"key_code": "4", "modifiers": ["shift"]},
                        '%': {"key_code": "5", "modifiers": ["shift"]},
                        '^': {"key_code": "6", "modifiers": ["shift"]},
                        '&': {"key_code": "7", "modifiers": ["shift"]},
                        '*': {"key_code": "8", "modifiers": ["shift"]},
                        '(': {"key_code": "9", "modifiers": ["shift"]},
                        ')': {"key_code": "0", "modifiers": ["shift"]},
                    }
                    
                    if char in char_mapping:
                        output.append(char_mapping[char])
                    # Skip unknown characters
            
            # Add automatic space after chord output (CharaChorder-style behavior)
            output.append({"key_code": "spacebar"})
            
            return output
            
        elif chord.output_type == "command":
            # Execute shell command
            return [{
                "shell_command": chord.output_text
            }]
        
        else:
            # Default to text
            return self._generate_output(Chord(
                input_keys=chord.input_keys,
                output_text=chord.output_text,
                output_type="text"
            ))
    
    def update_all_chords(self, chords: List[Chord]):
        """Update Karabiner configuration with all chords."""
        # Backup current configuration
        self._backup_config()
        
        try:
            # Load current configuration
            config = self._load_config()
            
            # Get or create FreeChorder profile
            profile = self._get_or_create_profile(config)
            
            # Group chords by length and category for better organization
            chord_groups = self._group_chords(chords)
            
            # Generate separate rules for each group
            all_rules = []
            
            # Add the impulse mode launcher rules first
            impulse_rules = self._generate_impulse_launcher_rules()
            all_rules.extend(impulse_rules)
            
            # Generate rules for each chord group
            for group_name, group_chords in chord_groups.items():
                # Skip disabled groups
                if group_name in self.disabled_groups:
                    print(f"Skipping disabled group: {group_name}")
                    continue
                    
                if group_chords:
                    # Create a separate rule set for each group
                    group_rule = {
                        "description": f"FreeChorder: {group_name}",
                        "manipulators": []
                    }
                    
                    for chord in group_chords:
                        try:
                            rule = self.generate_rule(chord)
                            # Extract the manipulator from the rule
                            if rule.get('manipulators'):
                                group_rule['manipulators'].extend(rule['manipulators'])
                        except Exception as e:
                            print(f"Warning: Failed to generate rule for {'+'.join(chord.input_keys)}: {str(e)}")
                    
                    if group_rule['manipulators']:
                        all_rules.append(group_rule)
            
            # Update complex modifications
            complex_mods = profile.get('complex_modifications', {})
            existing_rules = complex_mods.get('rules', [])
            
            # Update the timing parameters to match current sensitivity
            if 'parameters' not in complex_mods:
                complex_mods['parameters'] = {}
            complex_mods['parameters']['basic.simultaneous_threshold_milliseconds'] = self.chord_timeout_ms
            
            # Remove existing FreeChorder rules
            other_rules = [
                r for r in existing_rules 
                if not r.get('description', '').startswith('FreeChorder:')
            ]
            
            # Add new rules
            complex_mods['rules'] = other_rules + all_rules
            profile['complex_modifications'] = complex_mods
            
            # Save configuration
            self._save_config(config)
            
            # Reload Karabiner
            self._reload_karabiner()
            
        except Exception as e:
            raise KarabinerError(f"Failed to update Karabiner config: {str(e)}")
    
    def _group_chords(self, chords: List[Chord]) -> Dict[str, List[Chord]]:
        """Group chords by length and category for better organization."""
        groups = {}
        
        for chord in chords:
            # Count non-modifier keys
            non_modifier_keys = [key for key in chord.input_keys 
                               if key not in ['cmd', 'shift', 'option', 'control']]
            chord_length = len(non_modifier_keys)
            
            # Determine group name based on length and category
            if chord.category:
                # Use category if specified
                group_name = f"{chord.category.title()} Chords"
            else:
                # Group by length
                if chord_length == 2:
                    group_name = "2-Key Chords (Quick)"
                elif chord_length == 3:
                    group_name = "3-Key Chords (Standard)"
                elif chord_length == 4:
                    group_name = "4-Key Chords (Extended)"
                else:
                    group_name = f"{chord_length}+ Key Chords (Complex)"
            
            # Add to appropriate group
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(chord)
        
        # Sort groups by chord length (longest first) within each group
        # This ensures longer chords are processed before shorter ones in Karabiner
        for group_name, group_chords in groups.items():
            groups[group_name] = sorted(
                group_chords,
                key=lambda c: (
                    -len([k for k in c.input_keys if k not in ['cmd', 'shift', 'option', 'control']]),  # Longer chords first
                    '+'.join(c.input_keys)  # Then alphabetically for consistency
                )
            )
        
        # Sort groups for consistent ordering (longer chord groups first)
        sorted_groups = {}
        for key in sorted(groups.keys(), reverse=True):  # Reverse to put longer chord groups first
            sorted_groups[key] = groups[key]
        
        return sorted_groups
    
    def export_rules_to_files(self, chords: List[Chord], output_dir: str = None):
        """Export chord rules to separate JSON files for modular management."""
        if output_dir is None:
            output_dir = Path.home() / '.config' / 'freechorder' / 'karabiner_rules'
        else:
            output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Group chords
        chord_groups = self._group_chords(chords)
        
        # Export each group to a separate file
        exported_files = []
        for group_name, group_chords in chord_groups.items():
            if not group_chords:
                continue
            
            # Create filename from group name
            filename = group_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('+', 'plus')
            filepath = output_dir / f"{filename}.json"
            
            # Create rule structure for this group
            group_rules = {
                "title": f"FreeChorder - {group_name}",
                "rules": []
            }
            
            # Generate rules for each chord in the group
            for chord in group_chords:
                try:
                    rule = self.generate_rule(chord)
                    group_rules['rules'].append(rule)
                except Exception as e:
                    print(f"Warning: Failed to generate rule for {'+'.join(chord.input_keys)}: {str(e)}")
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(group_rules, f, indent=2)
            
            exported_files.append(filepath)
        
        # Also export launcher rules
        launcher_filepath = output_dir / "launcher_rules.json"
        launcher_rules = {
            "title": "FreeChorder - Launcher Rules",
            "rules": self._generate_impulse_launcher_rules()
        }
        with open(launcher_filepath, 'w') as f:
            json.dump(launcher_rules, f, indent=2)
        exported_files.append(launcher_filepath)
        
        return exported_files
    
    def _load_disabled_groups(self) -> Set[str]:
        """Load list of disabled chord groups from config."""
        config_file = Path.home() / '.config' / 'freechorder' / 'disabled_groups.yaml'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    return set(data.get('disabled_groups', []))
            except:
                pass
        return set()
    
    def _save_disabled_groups(self):
        """Save list of disabled chord groups to config."""
        config_file = Path.home() / '.config' / 'freechorder' / 'disabled_groups.yaml'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            yaml.dump({'disabled_groups': list(self.disabled_groups)}, f)
    
    def toggle_group(self, group_name: str, enable: bool = None):
        """Enable or disable a chord group."""
        if enable is None:
            # Toggle current state
            if group_name in self.disabled_groups:
                self.disabled_groups.remove(group_name)
                enabled = True
            else:
                self.disabled_groups.add(group_name)
                enabled = False
        else:
            if enable:
                self.disabled_groups.discard(group_name)
                enabled = True
            else:
                self.disabled_groups.add(group_name)
                enabled = False
        
        # Save state
        self._save_disabled_groups()
        return enabled
    
    def get_group_status(self, chords: List[Chord]) -> Dict[str, Dict[str, Any]]:
        """Get status of all chord groups."""
        groups = self._group_chords(chords)
        status = {}
        
        for group_name, group_chords in groups.items():
            status[group_name] = {
                'enabled': group_name not in self.disabled_groups,
                'chord_count': len(group_chords),
                'chords': group_chords
            }
        
        return status
    
    def _reload_karabiner(self):
        """Reload Karabiner-Elements configuration."""
        # Karabiner-Elements automatically watches and reloads the config file
        # No explicit reload command is needed
        pass
    
    def get_active_profile(self) -> Optional[str]:
        """Get the currently active Karabiner profile."""
        try:
            config = self._load_config()
            for profile in config.get('profiles', []):
                if profile.get('selected', False):
                    return profile.get('name')
            return None
        except:
            return None
    
    def _generate_impulse_launcher_rules(self) -> List[Dict[str, Any]]:
        """Generate multiple rules for launching impulse mode with different speeds."""
        rules = []
        
        # 1. Regular impulse mode (Ctrl+Option+Delete)
        regular_command = (
            'osascript -e \'tell application "Terminal"\' '
            '-e \'if (count of windows) is 0 then\' '
            '-e \'do script "source ~/.zshrc && fc impulse"\' '
            '-e \'else\' '
            '-e \'tell application "System Events" to tell process "Terminal" to keystroke "n" using command down\' '
            '-e \'delay 0.5\' '
            '-e \'do script "source ~/.zshrc && fc impulse" in window 1\' '
            '-e \'end if\' '
            '-e \'activate\' '
            '-e \'end tell\''
        )
        
        rules.append({
            "description": "FreeChorder: Launch Impulse Mode (ctrl+opt+delete)",
            "manipulators": [{
                "type": "basic",
                "from": {
                    "key_code": "delete_or_backspace",
                    "modifiers": {
                        "mandatory": ["control", "option"]
                    }
                },
                "to": [{
                    "shell_command": regular_command
                }],
                "conditions": []
            }]
        })
        
        # 2. Quick impulse mode - Faster startup (Cmd+Option+Delete)
        quick_command = (
            'osascript -e \'tell application "Terminal"\' '
            '-e \'do script "/Users/mostafa/freechorder/quick_impulse.sh"\' '
            '-e \'activate\' '
            '-e \'end tell\''
        )
        
        rules.append({
            "description": "FreeChorder: Quick Impulse Mode - Fast (cmd+opt+delete)",
            "manipulators": [{
                "type": "basic",
                "from": {
                    "key_code": "delete_or_backspace",
                    "modifiers": {
                        "mandatory": ["command", "option"]
                    }
                },
                "to": [{
                    "shell_command": quick_command
                }],
                "conditions": []
            }]
        })
        
        # 3. Native dialog mode - Instant (Shift+Option+Delete)
        native_command = 'osascript /Users/mostafa/freechorder/quick_impulse.applescript'
        
        rules.append({
            "description": "FreeChorder: Native Quick Chord Dialog - Instant (shift+opt+delete)",
            "manipulators": [{
                "type": "basic",
                "from": {
                    "key_code": "delete_or_backspace",
                    "modifiers": {
                        "mandatory": ["shift", "option"]
                    }
                },
                "to": [{
                    "shell_command": native_command
                }],
                "conditions": []
            }]
        })
        
        return rules
    
    def activate_freechorder_profile(self):
        """Activate the FreeChorder profile."""
        try:
            config = self._load_config()
            
            # Deselect all profiles
            for profile in config.get('profiles', []):
                profile['selected'] = False
            
            # Select FreeChorder profile
            for profile in config.get('profiles', []):
                if profile.get('name') == self.profile_name:
                    profile['selected'] = True
                    break
            
            self._save_config(config)
            self._reload_karabiner()
            
        except Exception as e:
            raise KarabinerError(f"Failed to activate FreeChorder profile: {str(e)}")
    
    def pause_freechorder_profile(self) -> Optional[str]:
        """Temporarily disable FreeChorder profile and return the previously active profile name."""
        try:
            config = self._load_config()
            previous_profile = None
            
            # Find currently selected profile
            for profile in config.get('profiles', []):
                if profile.get('selected', False):
                    previous_profile = profile.get('name')
                    break
            
            # If FreeChorder is active, switch to another profile
            if previous_profile == self.profile_name:
                # Deselect FreeChorder
                for profile in config.get('profiles', []):
                    profile['selected'] = False
                
                # Select first non-FreeChorder profile
                for profile in config.get('profiles', []):
                    if profile.get('name') != self.profile_name:
                        profile['selected'] = True
                        break
                
                self._save_config(config)
                self._reload_karabiner()
                return previous_profile
            
            return None
            
        except Exception as e:
            print(f"Warning: Failed to pause FreeChorder profile: {str(e)}")
            return None
    
    def resume_freechorder_profile(self):
        """Resume/activate the FreeChorder profile."""
        try:
            self.activate_freechorder_profile()
        except Exception as e:
            print(f"Warning: Failed to resume FreeChorder profile: {str(e)}")
