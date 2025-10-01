"""
Chord Manager - Handles CRUD operations for chords
"""

import os
import yaml
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class Chord:
    """Represents a keyboard chord."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    input_keys: List[str] = field(default_factory=list)
    output_text: str = ""
    output_type: str = "text"  # text, command, macro
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary for YAML serialization."""
        data = asdict(self)
        # Convert datetime to string
        data['created_at'] = self.created_at.isoformat()
        data['modified_at'] = self.modified_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        # Convert string to datetime
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('modified_at'), str):
            data['modified_at'] = datetime.fromisoformat(data['modified_at'])
        return cls(**data)


class ChordConflictError(Exception):
    """Raised when a chord conflicts with existing chords."""
    pass


class ChordManager:
    """Manages keyboard chords."""
    
    def __init__(self, storage_path: str):
        """Initialize the chord manager."""
        self.storage_path = Path(storage_path)
        self.chords: Dict[str, Chord] = {}
        self.input_index: Dict[frozenset, str] = {}  # Fast lookup by input
        self.output_index: Dict[str, List[str]] = {}  # Fast lookup by output
        
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing chords
        self.load_chords()
    
    def load_chords(self):
        """Load chords from storage file."""
        if not self.storage_path.exists():
            # Create empty file
            self._save_chords()
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            # Load chords
            for chord_data in data.get('chords', []):
                chord = Chord.from_dict(chord_data)
                self.chords[chord.id] = chord
                self._update_indices(chord)
                
        except Exception as e:
            raise Exception(f"Failed to load chords: {str(e)}")
    
    def _save_chords(self):
        """Save chords to storage file."""
        data = {
            'version': '1.0',
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'chord_count': len(self.chords)
            },
            'chords': [chord.to_dict() for chord in self.chords.values()]
        }
        
        # Create backup if file exists
        if self.storage_path.exists():
            backup_path = self.storage_path.with_suffix('.yaml.bak')
            self.storage_path.rename(backup_path)
        
        try:
            with open(self.storage_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            # Restore backup on error
            if backup_path.exists():
                backup_path.rename(self.storage_path)
            raise Exception(f"Failed to save chords: {str(e)}")
        
        # Remove backup on success
        if 'backup_path' in locals() and backup_path.exists():
            backup_path.unlink()
    
    def _update_indices(self, chord: Chord):
        """Update search indices for a chord."""
        # Input index
        input_key = frozenset(chord.input_keys)
        self.input_index[input_key] = chord.id
        
        # Output index
        if chord.output_text not in self.output_index:
            self.output_index[chord.output_text] = []
        if chord.id not in self.output_index[chord.output_text]:
            self.output_index[chord.output_text].append(chord.id)
    
    def _remove_from_indices(self, chord: Chord):
        """Remove chord from search indices."""
        # Input index
        input_key = frozenset(chord.input_keys)
        if input_key in self.input_index:
            del self.input_index[input_key]
        
        # Output index
        if chord.output_text in self.output_index:
            self.output_index[chord.output_text] = [
                cid for cid in self.output_index[chord.output_text] 
                if cid != chord.id
            ]
            if not self.output_index[chord.output_text]:
                del self.output_index[chord.output_text]
    
    def _normalize_keys(self, keys: List[str]) -> List[str]:
        """Normalize and validate input keys."""
        # Valid key codes for Karabiner
        valid_keys = {
            # Letters
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            # Numbers
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            # Special keys
            'space', 'return', 'tab', 'delete', 'escape', 'backspace',
            'up', 'down', 'left', 'right',
            # Modifiers (for special chords)
            'cmd', 'command', 'shift', 'option', 'opt', 'control', 'ctrl'
        }
        
        normalized = []
        for key in keys:
            key_lower = key.lower().strip()
            
            # Handle aliases
            if key_lower == 'command':
                key_lower = 'cmd'
            elif key_lower == 'opt':
                key_lower = 'option'
            elif key_lower == 'ctrl':
                key_lower = 'control'
            
            if key_lower not in valid_keys:
                raise ValueError(f"Invalid key: {key}")
            
            normalized.append(key_lower)
        
        return sorted(normalized)  # Sort for consistency
    
    def _check_conflicts(self, input_keys: List[str]) -> List[Chord]:
        """Check for chord conflicts."""
        input_set = frozenset(input_keys)
        conflicts = []
        
        # Exact match
        if input_set in self.input_index:
            conflicts.append(self.chords[self.input_index[input_set]])
        
        # Optional: Check for subset conflicts (can be warning instead of error)
        # Commented out for now to allow overlapping chords
        # for existing_input, chord_id in self.input_index.items():
        #     if input_set.issubset(existing_input) or existing_input.issubset(input_set):
        #         if self.chords[chord_id] not in conflicts:
        #             conflicts.append(self.chords[chord_id])
        
        return conflicts
    
    def add_chord(self, input_keys: List[str], output_text: str, 
                  category: Optional[str] = None, tags: List[str] = None) -> Chord:
        """Add a new chord."""
        # Normalize and validate input
        input_keys = self._normalize_keys(input_keys)
        
        if not input_keys:
            raise ValueError("Input keys cannot be empty")
        if not output_text:
            raise ValueError("Output text cannot be empty")
        
        # Check for conflicts
        conflicts = self._check_conflicts(input_keys)
        if conflicts:
            conflict_str = ', '.join(['+'.join(c.input_keys) for c in conflicts])
            raise ChordConflictError(f"Chord already exists: {conflict_str}")
        
        # Create chord
        chord = Chord(
            input_keys=input_keys,
            output_text=output_text,
            category=category,
            tags=tags or []
        )
        
        # Store chord
        self.chords[chord.id] = chord
        self._update_indices(chord)
        self._save_chords()
        
        return chord
    
    def remove_chord_by_input(self, input_keys: List[str]) -> Optional[Chord]:
        """Remove a chord by its input keys."""
        input_keys = self._normalize_keys(input_keys)
        input_key = frozenset(input_keys)
        
        if input_key not in self.input_index:
            return None
        
        chord_id = self.input_index[input_key]
        chord = self.chords[chord_id]
        
        # Remove from indices and storage
        self._remove_from_indices(chord)
        del self.chords[chord_id]
        self._save_chords()
        
        return chord
    
    def remove_chord_by_output(self, output_text: str) -> Optional[Chord]:
        """Remove the first chord with the given output text."""
        if output_text not in self.output_index:
            return None
        
        chord_ids = self.output_index[output_text]
        if not chord_ids:
            return None
        
        # Remove the first matching chord
        chord_id = chord_ids[0]
        chord = self.chords[chord_id]
        
        # Remove from indices and storage
        self._remove_from_indices(chord)
        del self.chords[chord_id]
        self._save_chords()
        
        return chord
    
    def get_all_chords(self) -> List[Chord]:
        """Get all chords sorted by creation date."""
        return sorted(self.chords.values(), key=lambda c: c.created_at)
    
    def search_chords(self, query: str, search_type: str = 'all') -> List[Chord]:
        """Search for chords."""
        results = []
        query_lower = query.lower()
        
        if search_type in ['all', 'input']:
            # Search in input keys
            for chord in self.chords.values():
                input_str = '+'.join(chord.input_keys)
                if query_lower in input_str.lower():
                    results.append(chord)
        
        if search_type in ['all', 'output']:
            # Search in output text
            for chord in self.chords.values():
                if query_lower in chord.output_text.lower():
                    if chord not in results:
                        results.append(chord)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get chord statistics."""
        total_usage = sum(c.usage_count for c in self.chords.values())
        categories = set(c.category for c in self.chords.values() if c.category)
        most_used = sorted(self.chords.values(), key=lambda c: c.usage_count, reverse=True)
        
        return {
            'total_chords': len(self.chords),
            'total_usage': total_usage,
            'categories': len(categories),
            'most_used': most_used[:10]
        }
    
    def increment_usage(self, chord_id: str):
        """Increment usage count for a chord."""
        if chord_id in self.chords:
            self.chords[chord_id].usage_count += 1
            self.chords[chord_id].modified_at = datetime.now()
            self._save_chords()
