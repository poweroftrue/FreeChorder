# FreeChorder - Quick Start Implementation Guide

## Immediate Next Steps (MVP in 2 weeks)

### Day 1-2: Project Setup & Basic Structure

1. **Initialize Project**
```bash
mkdir freechorder
cd freechorder
python3 -m venv venv
source venv/bin/activate
pip install click pyyaml pynput

# Create project structure
mkdir -p src/freechorder/{core,karabiner,cli}
touch src/freechorder/__init__.py
touch src/freechorder/cli/main.py
touch src/freechorder/core/chord_manager.py
touch src/freechorder/karabiner/config_generator.py
```

2. **Create Basic CLI Structure** (`src/freechorder/cli/main.py`)
```python
import click
from ..core.chord_manager import ChordManager
from ..karabiner.config_generator import KarabinerConfig

@click.group()
def cli():
    """FreeChorder - Software CharaChorder for macOS"""
    pass

@cli.command()
@click.argument('input_keys')
@click.argument('output_text')
def add(input_keys, output_text):
    """Add a new chord"""
    # Implementation here
    
@cli.command()
@click.argument('search_term')
def search(search_term):
    """Search for chords"""
    # Implementation here

if __name__ == '__main__':
    cli()
```

### Day 3-4: Core Chord Management

1. **Implement Chord Storage** (`~/.config/freechorder/chords.yaml`)
```yaml
chords:
  - id: "chord_001"
    input: ["a", "s", "d"]
    output: "and"
    created: "2025-09-27T10:00:00"
    usage_count: 0
    
  - id: "chord_002"
    input: ["t", "h", "e"]
    output: "the"
    created: "2025-09-27T10:01:00"
    usage_count: 0
```

2. **Basic CRUD Operations**
- Add chord with validation
- Remove chord by input or ID
- List all chords
- Search chords (simple string matching first)

### Day 5-7: Karabiner Integration

1. **Understand Karabiner Config Location**
   - Primary: `~/.config/karabiner/karabiner.json`
   - Backup existing configuration first!

2. **Generate Complex Modifications**
```json
{
  "title": "FreeChorder Chords",
  "rules": [
    {
      "description": "Chord: asd → and",
      "manipulators": [
        {
          "type": "basic",
          "from": {
            "simultaneous": [
              {"key_code": "a"},
              {"key_code": "s"},
              {"key_code": "d"}
            ],
            "simultaneous_options": {
              "key_down_order": "insensitive",
              "key_up_order": "insensitive",
              "key_up_when": "any"
            }
          },
          "to": [
            {"shell_command": "echo -n 'and' | pbcopy && osascript -e 'tell application \"System Events\" to keystroke \"v\" using command down'"}
          ]
        }
      ]
    }
  ]
}
```

3. **Configuration Update Process**
   - Read existing karabiner.json
   - Find or create FreeChorder profile
   - Update complex_modifications
   - Write back to file
   - Trigger Karabiner reload

### Day 8-9: Testing & Debugging

1. **Test Cases**
   - Single key chords (edge case)
   - Multi-key chords (2-6 keys)
   - Special characters in output
   - Conflicting chords
   - Karabiner reload

2. **Common Issues to Handle**
   - Karabiner not installed
   - Permission issues
   - Invalid key codes
   - Chord conflicts

### Day 10-11: Impulse Chording (Basic)

1. **Simple Implementation**
```python
# Using pynput to monitor keys
from pynput import keyboard
import time

class ImpulseChorder:
    def __init__(self):
        self.pressed_keys = set()
        self.last_press_time = 0
        
    def on_press(self, key):
        current_time = time.time()
        if current_time - self.last_press_time > 0.1:  # 100ms timeout
            self.pressed_keys.clear()
        
        self.pressed_keys.add(key)
        self.last_press_time = current_time
        
        if len(self.pressed_keys) >= 2:  # Minimum chord size
            # Prompt for output
            self.create_chord(self.pressed_keys)
```

### Day 12-14: Polish & Release

1. **Essential Features Only**
   - Help text and documentation
   - Basic error handling
   - Installation script
   - README with examples

2. **Create Installation Script**
```bash
#!/bin/bash
# install.sh
pip install -e .
mkdir -p ~/.config/freechorder
echo "FreeChorder installed! Run 'freechorder --help' to get started."
```

## MVP Feature Set

### Must Have (Week 1)
- ✅ Add/remove chords via CLI
- ✅ List all chords
- ✅ Basic search functionality
- ✅ Karabiner config generation
- ✅ Automatic Karabiner reload

### Should Have (Week 2)
- ✅ Impulse chording (basic)
- ✅ Conflict detection
- ✅ Import from CSV
- ✅ Backup/restore configs

### Nice to Have (Post-MVP)
- Statistics tracking
- Advanced search with regex
- Categories and tags
- GUI application
- Cloud sync

## Quick Command Reference

```bash
# Basic usage
freechorder add "asd" "and"
freechorder add "teh" "the"
freechorder list
freechorder remove "asd"
freechorder search "the"

# Impulse mode
freechorder impulse  # Then press keys + Enter to define output

# Management
freechorder backup
freechorder config --karabiner-path /custom/path/karabiner.json
```

## Critical Code Snippets

### 1. Safe Karabiner Config Update
```python
import json
import shutil
from datetime import datetime

def update_karabiner_config(new_rules):
    config_path = os.path.expanduser("~/.config/karabiner/karabiner.json")
    
    # Backup
    backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(config_path, backup_path)
    
    # Read current config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Find or create FreeChorder profile
    freechorder_profile = None
    for profile in config['profiles']:
        if profile['name'] == 'FreeChorder':
            freechorder_profile = profile
            break
    
    if not freechorder_profile:
        # Create new profile based on default
        freechorder_profile = config['profiles'][0].copy()
        freechorder_profile['name'] = 'FreeChorder'
        config['profiles'].append(freechorder_profile)
    
    # Update complex modifications
    freechorder_rules = {
        "title": "FreeChorder Chords",
        "rules": new_rules
    }
    
    # Replace or add FreeChorder rules
    complex_mods = freechorder_profile.get('complex_modifications', {})
    rules = complex_mods.get('rules', [])
    
    # Remove existing FreeChorder rules
    rules = [r for r in rules if r.get('description', '').startswith('FreeChorder:')]
    
    # Add new rules
    rules.extend(new_rules)
    complex_mods['rules'] = rules
    freechorder_profile['complex_modifications'] = complex_mods
    
    # Write back
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Reload Karabiner
    os.system("'/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli' --reload-karabiner-config")
```

### 2. Chord Validation
```python
def validate_chord(input_keys, output_text, existing_chords):
    # Check for empty
    if not input_keys or not output_text:
        raise ValueError("Input and output cannot be empty")
    
    # Check for conflicts
    input_set = set(input_keys)
    for chord in existing_chords:
        if set(chord['input']) == input_set:
            raise ValueError(f"Chord {input_keys} already exists")
        
        # Check for subset conflicts
        if set(chord['input']).issubset(input_set) or input_set.issubset(set(chord['input'])):
            print(f"Warning: Potential conflict with chord {chord['input']}")
    
    # Validate key codes
    valid_keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                  '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                  'space', 'return', 'tab', 'delete', 'escape']
    
    for key in input_keys:
        if key not in valid_keys:
            raise ValueError(f"Invalid key: {key}")
    
    return True
```

## Testing Checklist

- [ ] Install Karabiner-Elements
- [ ] Create test chords: "asd" → "and", "teh" → "the"
- [ ] Verify chords work in any application
- [ ] Test chord deletion
- [ ] Test Karabiner reload
- [ ] Test with 10+ chords
- [ ] Test error cases (no Karabiner, bad keys, etc.)

## Common Issues & Solutions

1. **Karabiner not reloading**
   - Check if Karabiner-Elements is running
   - Verify CLI tool path exists
   - Try manual reload in Karabiner preferences

2. **Chords not working**
   - Check Karabiner EventViewer for key events
   - Verify JSON syntax in karabiner.json
   - Ensure FreeChorder profile is selected

3. **Permission issues**
   - Karabiner needs Accessibility permissions
   - Terminal may need Full Disk Access for config files

## Resources

- Karabiner Complex Modifications: https://ke-complex-modifications.pqrs.org/
- Karabiner JSON Reference: https://karabiner-elements.pqrs.org/docs/json/
- Example Configurations: https://github.com/pqrs-org/KE-complex_modifications

Start with Day 1-2 tasks and build incrementally. Focus on getting basic chord addition working with Karabiner first, then add features progressively.
