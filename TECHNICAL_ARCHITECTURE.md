# FreeChorder - Technical Architecture Document

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│                  (CLI Commands via Click)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Application Core Layer                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │Chord Manager│  │Search Engine │  │ Impulse Handler  │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Integration Layer                          │
│  ┌──────────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │Karabiner Bridge  │  │Config Store │  │ Stats Store  │  │
│  └──────────────────┘  └─────────────┘  └──────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    External Systems                          │
│  ┌──────────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │Karabiner-Elements│  │ File System │  │   macOS API  │  │
│  └──────────────────┘  └─────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components Detailed Design

### 1. Chord Manager (`chord_manager.py`)

**Responsibilities:**
- CRUD operations for chords
- Validation and conflict detection
- Chord organization and categorization

**Key Classes:**

```python
from dataclasses import dataclass
from typing import List, Optional, Set
from datetime import datetime
import uuid

@dataclass
class Chord:
    id: str
    input_keys: List[str]
    output_text: str
    output_type: str = "text"  # text, command, macro
    created_at: datetime = None
    modified_at: datetime = None
    usage_count: int = 0
    category: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.modified_at:
            self.modified_at = self.created_at
        if not self.tags:
            self.tags = []

class ChordManager:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.chords: Dict[str, Chord] = {}
        self.input_index: Dict[frozenset, str] = {}  # Fast lookup by input
        self.output_index: Dict[str, List[str]] = {}  # Fast lookup by output
        self.load_chords()
    
    def add_chord(self, input_keys: List[str], output_text: str) -> Chord:
        # Normalize and validate input
        input_keys = self._normalize_keys(input_keys)
        self._validate_chord(input_keys, output_text)
        
        # Check for conflicts
        conflicts = self._check_conflicts(input_keys)
        if conflicts:
            raise ChordConflictError(f"Conflicts with: {conflicts}")
        
        # Create and store chord
        chord = Chord(
            id=str(uuid.uuid4()),
            input_keys=input_keys,
            output_text=output_text
        )
        
        self.chords[chord.id] = chord
        self._update_indices(chord)
        self._save_chords()
        
        # Update Karabiner configuration
        KarabinerBridge().update_chord(chord)
        
        return chord
    
    def _check_conflicts(self, input_keys: List[str]) -> List[Chord]:
        """Check for exact matches and subset conflicts"""
        input_set = frozenset(input_keys)
        conflicts = []
        
        # Exact match
        if input_set in self.input_index:
            conflicts.append(self.chords[self.input_index[input_set]])
        
        # Subset conflicts (optional, can be warning instead of error)
        for existing_input, chord_id in self.input_index.items():
            if input_set.issubset(existing_input) or existing_input.issubset(input_set):
                if chord_id not in [c.id for c in conflicts]:
                    conflicts.append(self.chords[chord_id])
        
        return conflicts
```

### 2. Karabiner Bridge (`karabiner_bridge.py`)

**Responsibilities:**
- Generate Karabiner-Elements configurations
- Manage configuration updates safely
- Handle Karabiner reloads

**Implementation Details:**

```python
import json
import os
import shutil
from typing import List, Dict
from datetime import datetime

class KarabinerBridge:
    def __init__(self):
        self.config_path = os.path.expanduser("~/.config/karabiner/karabiner.json")
        self.profile_name = "FreeChorder"
        self.ensure_karabiner_installed()
    
    def generate_rule(self, chord: Chord) -> Dict:
        """Generate Karabiner rule for a chord"""
        rule = {
            "description": f"FreeChorder: {'+'.join(chord.input_keys)} → {chord.output_text}",
            "manipulators": [{
                "type": "basic",
                "from": {
                    "simultaneous": [
                        {"key_code": key} for key in chord.input_keys
                    ],
                    "simultaneous_options": {
                        "key_down_order": "insensitive",
                        "key_up_order": "insensitive",
                        "key_up_when": "any"
                    }
                },
                "to": self._generate_output(chord)
            }]
        }
        return rule
    
    def _generate_output(self, chord: Chord) -> List[Dict]:
        """Generate output configuration based on chord type"""
        if chord.output_type == "text":
            # Use shell command to type text (handles special characters)
            return [{
                "shell_command": f"osascript -e 'tell application \"System Events\" to keystroke \"{chord.output_text}\"'"
            }]
        elif chord.output_type == "command":
            # Execute shell command
            return [{
                "shell_command": chord.output_text
            }]
        elif chord.output_type == "keys":
            # Send key combination
            return self._parse_key_sequence(chord.output_text)
        else:
            raise ValueError(f"Unknown output type: {chord.output_type}")
    
    def update_all_chords(self, chords: List[Chord]):
        """Update Karabiner with all chords"""
        # Backup current configuration
        self._backup_config()
        
        # Load current configuration
        config = self._load_config()
        
        # Find or create FreeChorder profile
        profile = self._get_or_create_profile(config)
        
        # Generate all rules
        rules = [self.generate_rule(chord) for chord in chords]
        
        # Update complex modifications
        self._update_complex_modifications(profile, rules)
        
        # Save configuration
        self._save_config(config)
        
        # Reload Karabiner
        self._reload_karabiner()
    
    def _update_complex_modifications(self, profile: Dict, rules: List[Dict]):
        """Update complex modifications in profile"""
        complex_mods = profile.get("complex_modifications", {"rules": []})
        
        # Remove existing FreeChorder rules
        existing_rules = complex_mods.get("rules", [])
        other_rules = [r for r in existing_rules 
                      if not r.get("description", "").startswith("FreeChorder:")]
        
        # Add new FreeChorder rules
        complex_mods["rules"] = other_rules + rules
        profile["complex_modifications"] = complex_mods
```

### 3. Impulse Handler (`impulse_handler.py`)

**Responsibilities:**
- Monitor keyboard input in real-time
- Detect chord combinations
- Interactive chord creation

**Implementation:**

```python
from pynput import keyboard
import time
import threading
from typing import Set, Callable

class ImpulseHandler:
    def __init__(self, chord_callback: Callable):
        self.chord_callback = chord_callback
        self.pressed_keys: Set[str] = set()
        self.chord_start_time = None
        self.chord_timeout = 0.1  # 100ms
        self.min_chord_size = 2
        self.active = False
        self.listener = None
        
    def start(self):
        """Start monitoring keyboard input"""
        self.active = True
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        print("Impulse mode active. Press keys simultaneously to create chord.")
        print("Press ESC to exit impulse mode.")
    
    def _on_press(self, key):
        """Handle key press event"""
        if key == keyboard.Key.esc:
            self.stop()
            return
        
        # Get key name
        key_name = self._get_key_name(key)
        if not key_name:
            return
        
        # Track timing
        current_time = time.time()
        if not self.chord_start_time or (current_time - self.chord_start_time) > self.chord_timeout:
            self.pressed_keys.clear()
            self.chord_start_time = current_time
        
        # Add key to chord
        self.pressed_keys.add(key_name)
        
        # Check if we have a potential chord
        if len(self.pressed_keys) >= self.min_chord_size:
            # Schedule chord detection
            threading.Timer(self.chord_timeout, self._detect_chord).start()
    
    def _detect_chord(self):
        """Detect and create chord from pressed keys"""
        if len(self.pressed_keys) >= self.min_chord_size:
            chord_keys = sorted(list(self.pressed_keys))
            print(f"\nDetected chord: {'+'.join(chord_keys)}")
            
            # Prompt for output
            output = input("Enter output text (or 'cancel' to skip): ")
            if output and output != 'cancel':
                try:
                    self.chord_callback(chord_keys, output)
                    print(f"✓ Chord created: {'+'.join(chord_keys)} → {output}")
                except Exception as e:
                    print(f"✗ Error creating chord: {e}")
            
            # Reset for next chord
            self.pressed_keys.clear()
            self.chord_start_time = None
```

### 4. Search Engine (`search_engine.py`)

**Responsibilities:**
- Fast chord search by input or output
- Fuzzy matching support
- Pattern-based search

**Implementation:**

```python
from typing import List, Optional
import re
from fuzzywuzzy import fuzz

class SearchEngine:
    def __init__(self, chord_manager: ChordManager):
        self.chord_manager = chord_manager
    
    def search(self, query: str, search_type: str = "all") -> List[Chord]:
        """Search chords by query"""
        results = []
        
        if search_type in ["all", "input"]:
            results.extend(self._search_by_input(query))
        
        if search_type in ["all", "output"]:
            results.extend(self._search_by_output(query))
        
        # Remove duplicates and sort by relevance
        seen = set()
        unique_results = []
        for chord in results:
            if chord.id not in seen:
                seen.add(chord.id)
                unique_results.append(chord)
        
        return self._sort_by_relevance(unique_results, query)
    
    def _search_by_input(self, query: str) -> List[Chord]:
        """Search by input keys"""
        results = []
        query_keys = query.lower().replace('+', ' ').split()
        
        for chord in self.chord_manager.chords.values():
            # Exact match
            if set(query_keys) == set(chord.input_keys):
                results.append((chord, 100))
                continue
            
            # Partial match
            if set(query_keys).issubset(set(chord.input_keys)):
                results.append((chord, 80))
                continue
            
            # Fuzzy match
            chord_input_str = '+'.join(chord.input_keys)
            similarity = fuzz.ratio(query, chord_input_str)
            if similarity > 60:
                results.append((chord, similarity))
        
        # Sort by score and return chords
        results.sort(key=lambda x: x[1], reverse=True)
        return [chord for chord, _ in results]
```

## Data Storage Design

### 1. Chord Storage Format (`~/.config/freechorder/chords.yaml`)

```yaml
version: "1.0"
metadata:
  created_at: "2025-09-27T10:00:00Z"
  last_modified: "2025-09-27T10:00:00Z"
  chord_count: 42

chords:
  - id: "550e8400-e29b-41d4-a716-446655440000"
    input_keys: ["a", "s", "d"]
    output_text: "and"
    output_type: "text"
    created_at: "2025-09-27T10:00:00Z"
    modified_at: "2025-09-27T10:00:00Z"
    usage_count: 156
    category: "common_words"
    tags: ["articles", "frequent"]
    
  - id: "550e8400-e29b-41d4-a716-446655440001"
    input_keys: ["cmd", "shift", "d"]
    output_text: "osascript -e 'tell application \"Dock\" to quit'"
    output_type: "command"
    created_at: "2025-09-27T10:01:00Z"
    modified_at: "2025-09-27T10:01:00Z"
    usage_count: 23
    category: "system_commands"
    tags: ["macos", "productivity"]

categories:
  - name: "common_words"
    description: "Frequently used words"
    color: "#4CAF50"
  - name: "programming"
    description: "Code snippets and commands"
    color: "#2196F3"
```

### 2. Application Configuration (`~/.config/freechorder/config.yaml`)

```yaml
version: "1.0"
karabiner:
  config_path: "~/.config/karabiner/karabiner.json"
  profile_name: "FreeChorder"
  reload_command: "/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli --reload-karabiner-config"

impulse:
  enabled: true
  trigger_key: "cmd+shift+i"
  chord_timeout_ms: 100
  min_chord_size: 2
  audio_feedback: true

ui:
  color_output: true
  page_size: 20
  date_format: "%Y-%m-%d %H:%M"

performance:
  max_chords: 10000
  index_update_batch_size: 100
  search_cache_size: 1000

backup:
  auto_backup: true
  backup_count: 10
  backup_on_major_change: true
```

## Performance Considerations

### 1. Indexing Strategy

```python
class ChordIndex:
    """High-performance chord indexing"""
    
    def __init__(self):
        # Primary indices
        self.by_id: Dict[str, Chord] = {}
        self.by_input: Dict[frozenset, str] = {}
        self.by_output: Dict[str, List[str]] = {}
        
        # Secondary indices for performance
        self.by_category: Dict[str, List[str]] = {}
        self.by_first_key: Dict[str, List[str]] = {}
        self.by_length: Dict[int, List[str]] = {}
        
        # Search optimization
        self.trigram_index: Dict[str, Set[str]] = {}  # For fuzzy search
        self.usage_sorted: List[str] = []  # Sorted by usage
```

### 2. Caching Strategy

```python
from functools import lru_cache
import pickle

class CachedChordManager(ChordManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._search_cache = {}
        self._karabiner_cache = None
        
    @lru_cache(maxsize=1000)
    def search_cached(self, query: str, search_type: str) -> List[Chord]:
        """Cached search results"""
        cache_key = f"{query}:{search_type}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]
        
        results = self.search(query, search_type)
        self._search_cache[cache_key] = results
        return results
    
    def invalidate_caches(self):
        """Clear all caches when chords change"""
        self._search_cache.clear()
        self._karabiner_cache = None
        self.search_cached.cache_clear()
```

## Security Considerations

### 1. Input Validation

```python
class SecurityValidator:
    @staticmethod
    def validate_output_text(text: str) -> bool:
        """Validate output text for security issues"""
        # Prevent command injection
        dangerous_patterns = [
            r'`.*`',  # Backticks
            r'\$\(.*\)',  # Command substitution
            r';\s*rm',  # rm commands
            r'>\s*/dev/',  # Device writes
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text):
                raise SecurityError(f"Potentially dangerous pattern detected: {pattern}")
        
        return True
    
    @staticmethod
    def sanitize_for_shell(text: str) -> str:
        """Escape text for shell usage"""
        # Escape special characters
        return text.replace('"', '\\"').replace("'", "\\'").replace("`", "\\`")
```

### 2. File Permission Handling

```python
import stat

class SecureFileHandler:
    @staticmethod
    def ensure_secure_directory(path: str):
        """Ensure directory has proper permissions"""
        os.makedirs(path, exist_ok=True)
        
        # Set directory permissions to 700 (owner only)
        os.chmod(path, stat.S_IRWXU)
        
    @staticmethod
    def write_secure_file(path: str, content: str):
        """Write file with secure permissions"""
        # Create with restricted permissions
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f:
            f.write(content)
```

## Error Handling Strategy

### 1. Custom Exceptions

```python
class FreeChorderError(Exception):
    """Base exception for FreeChorder"""
    pass

class ChordConflictError(FreeChorderError):
    """Raised when chord conflicts with existing chord"""
    pass

class KarabinerError(FreeChorderError):
    """Raised when Karabiner operations fail"""
    pass

class ValidationError(FreeChorderError):
    """Raised when validation fails"""
    pass
```

### 2. Error Recovery

```python
class ErrorRecovery:
    @staticmethod
    def with_retry(func, max_retries=3, delay=1.0):
        """Retry failed operations with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay * (2 ** attempt))
    
    @staticmethod
    def safe_config_update(update_func):
        """Safely update configuration with rollback"""
        backup_path = None
        try:
            # Create backup
            backup_path = ConfigManager.backup_current()
            
            # Perform update
            result = update_func()
            
            # Verify update
            if not ConfigManager.verify_config():
                raise ConfigError("Configuration verification failed")
            
            return result
            
        except Exception as e:
            # Rollback on error
            if backup_path:
                ConfigManager.restore_backup(backup_path)
            raise
```

## Testing Strategy

### 1. Unit Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestChordManager:
    @pytest.fixture
    def chord_manager(self, tmp_path):
        return ChordManager(storage_path=tmp_path / "chords.yaml")
    
    def test_add_simple_chord(self, chord_manager):
        chord = chord_manager.add_chord(["a", "s", "d"], "and")
        assert chord.input_keys == ["a", "s", "d"]
        assert chord.output_text == "and"
    
    def test_conflict_detection(self, chord_manager):
        chord_manager.add_chord(["a", "s", "d"], "and")
        
        with pytest.raises(ChordConflictError):
            chord_manager.add_chord(["a", "s", "d"], "AND")
    
    @patch('karabiner_bridge.KarabinerBridge.update_chord')
    def test_karabiner_update(self, mock_update, chord_manager):
        chord = chord_manager.add_chord(["a", "s"], "as")
        mock_update.assert_called_once_with(chord)
```

### 2. Integration Test Example

```python
class TestKarabinerIntegration:
    def test_full_chord_lifecycle(self, temp_karabiner_config):
        # Add chord
        runner = CliRunner()
        result = runner.invoke(cli, ['add', 'asd', 'and'])
        assert result.exit_code == 0
        
        # Verify Karabiner config updated
        config = load_karabiner_config()
        rules = get_freechorder_rules(config)
        assert len(rules) == 1
        assert rules[0]['description'] == 'FreeChorder: a+s+d → and'
        
        # Test chord works (manual verification needed)
        
        # Remove chord
        result = runner.invoke(cli, ['remove', 'asd'])
        assert result.exit_code == 0
        
        # Verify removed from Karabiner
        config = load_karabiner_config()
        rules = get_freechorder_rules(config)
        assert len(rules) == 0
```

## Deployment Architecture

### 1. Installation Script

```bash
#!/usr/bin/env bash
# install.sh

set -e

echo "Installing FreeChorder..."

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

if ! [ -d "/Applications/Karabiner-Elements.app" ]; then
    echo "Error: Karabiner-Elements must be installed"
    echo "Download from: https://karabiner-elements.pqrs.org/"
    exit 1
fi

# Create virtual environment
python3 -m venv ~/.freechorder/venv
source ~/.freechorder/venv/bin/activate

# Install package
pip install --upgrade pip
pip install freechorder

# Create config directory
mkdir -p ~/.config/freechorder

# Create initial configuration
cat > ~/.config/freechorder/config.yaml << EOF
version: "1.0"
karabiner:
  profile_name: "FreeChorder"
impulse:
  enabled: true
  chord_timeout_ms: 100
EOF

# Add to PATH
echo 'export PATH="$HOME/.freechorder/venv/bin:$PATH"' >> ~/.zshrc

echo "✓ FreeChorder installed successfully!"
echo "Run 'freechorder --help' to get started"
```

### 2. Distribution Methods

1. **Homebrew Formula**
```ruby
class Freechorder < Formula
  desc "Software CharaChorder for macOS using Karabiner-Elements"
  homepage "https://github.com/username/freechorder"
  url "https://github.com/username/freechorder/archive/v1.0.0.tar.gz"
  sha256 "..."
  
  depends_on "python@3.9"
  depends_on "karabiner-elements"
  
  def install
    virtualenv_install_with_resources
  end
  
  test do
    system "#{bin}/freechorder", "--version"
  end
end
```

2. **PyPI Package**
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="freechorder",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0",
        "pyyaml>=6.0",
        "pynput>=1.7",
        "fuzzywuzzy>=0.18",
    ],
    entry_points={
        "console_scripts": [
            "freechorder=freechorder.cli.main:cli",
        ],
    },
)
```

This technical architecture provides a solid foundation for building FreeChorder with proper separation of concerns, performance optimization, and security considerations.
