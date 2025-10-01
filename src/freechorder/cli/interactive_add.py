#!/usr/bin/env python3
"""
Interactive chord addition - Better UX for creating chords
"""

import click
from typing import List, Optional, Tuple
from freechorder.core.chord_manager import ChordManager, ChordConflictError
from freechorder.karabiner.config_generator import KarabinerBridge


class InteractiveChordAdder:
    """Interactive chord addition with better UX."""
    
    def __init__(self, chord_manager: ChordManager, karabiner: KarabinerBridge):
        self.chord_manager = chord_manager
        self.karabiner = karabiner
        self.last_added = []  # Track recent chords for undo
        self.max_history = 10
    
    def add_interactive(self, input_keys: Optional[str] = None, output_text: Optional[str] = None,
                       category: Optional[str] = None, skip_confirm: bool = False):
        """Add a chord with interactive prompts and confirmation."""
        
        # Step 1: Get input keys if not provided
        if not input_keys:
            click.echo("\n🎯 Add New Chord")
            click.echo("=" * 50)
            input_keys = click.prompt(
                "Enter keys to press together",
                type=str,
                help_text="Examples: 'asd', 'a+s+d', 'abc'"
            ).strip()
        
        # Parse and normalize keys
        keys_raw = input_keys.replace('+', '').replace(' ', '').lower()
        keys_list = list(keys_raw)
        
        if len(keys_list) < 2:
            click.echo("❌ Error: Need at least 2 keys for a chord")
            return None
        
        # Step 2: Check for existing conflicts BEFORE asking for output
        try:
            normalized_keys = self.chord_manager._normalize_keys(keys_list)
            conflicts = self.chord_manager._check_conflicts(normalized_keys)
            
            if conflicts:
                existing = conflicts[0]
                click.echo(f"\n⚠️  Chord {'+'.join(normalized_keys)} already exists!")
                click.echo(f"   Current output: '{existing.output_text}'")
                
                if click.confirm("\n   Would you like to replace it?", default=False):
                    # Remove old chord first
                    self.chord_manager.remove_chord_by_input(normalized_keys)
                    click.echo("   ✓ Old chord removed")
                else:
                    click.echo("   ✗ Chord addition cancelled")
                    return None
                    
        except ValueError as e:
            click.echo(f"❌ Invalid keys: {e}")
            click.echo("\n💡 Tip: Use only letters (a-z), numbers (0-9), or special keys like 'space', 'tab'")
            return None
        
        # Step 3: Show visual preview of the chord
        chord_display = '+'.join(normalized_keys)
        click.echo(f"\n📝 Chord preview: {chord_display}")
        click.echo(f"   Keys needed: {len(normalized_keys)}")
        
        # Get sensitivity info
        sensitivity = self.karabiner.get_chord_sensitivity(
            type('obj', (), {'input_keys': normalized_keys})
        )
        click.echo(f"   Timing: {sensitivity}ms")
        
        # Step 4: Get output text if not provided
        if not output_text:
            click.echo()
            output_text = click.prompt(
                "Enter what to output",
                type=str
            ).strip()
        
        if not output_text:
            click.echo("❌ Error: Output text cannot be empty")
            return None
        
        # Step 5: Show preview and confirm (unless skipped)
        if not skip_confirm:
            click.echo(f"\n✨ Preview:")
            click.echo(f"   When you press: {chord_display}")
            click.echo(f"   Output will be: '{output_text}' ")
            
            if category:
                click.echo(f"   Category: {category}")
            
            if not click.confirm("\n   Save this chord?", default=True):
                click.echo("   ✗ Chord not saved")
                return None
        
        # Step 6: Actually add the chord
        try:
            chord = self.chord_manager.add_chord(
                input_keys=normalized_keys,
                output_text=output_text,
                category=category
            )
            
            # Update Karabiner
            all_chords = self.chord_manager.get_all_chords()
            self.karabiner.update_all_chords(all_chords)
            
            # Track for undo
            self._add_to_history(chord)
            
            # Success message
            click.echo(f"\n✅ Chord created successfully!")
            click.echo(f"   {chord_display} → '{output_text}'")
            click.echo(f"   The chord is now active system-wide!")
            
            # Show helpful tips
            if len(self.last_added) > 1:
                click.echo(f"\n💡 Tip: Use 'fc undo' to remove the last {len(self.last_added)} chord(s)")
            
            return chord
            
        except ChordConflictError as e:
            click.echo(f"\n❌ Error: {e}")
            return None
        except Exception as e:
            click.echo(f"\n❌ Error creating chord: {e}")
            return None
    
    def add_batch(self, chord_pairs: List[Tuple[str, str]], category: Optional[str] = None):
        """Add multiple chords at once."""
        click.echo(f"\n📦 Batch Add: {len(chord_pairs)} chords")
        click.echo("=" * 50)
        
        successful = 0
        failed = 0
        
        for input_keys, output_text in chord_pairs:
            click.echo(f"\n➤ {input_keys} → {output_text}")
            result = self.add_interactive(
                input_keys=input_keys,
                output_text=output_text,
                category=category,
                skip_confirm=True  # Skip individual confirmations in batch mode
            )
            
            if result:
                successful += 1
            else:
                failed += 1
        
        # Summary
        click.echo(f"\n" + "=" * 50)
        click.echo(f"✅ Added: {successful} chords")
        if failed > 0:
            click.echo(f"❌ Failed: {failed} chords")
    
    def undo_last(self, count: int = 1):
        """Undo the last N added chords."""
        if not self.last_added:
            click.echo("❌ No chords to undo")
            return
        
        count = min(count, len(self.last_added))
        click.echo(f"\n🔄 Undoing last {count} chord(s)...")
        
        for _ in range(count):
            if not self.last_added:
                break
                
            chord = self.last_added.pop()
            try:
                self.chord_manager.remove_chord_by_input(chord.input_keys)
                click.echo(f"   ✓ Removed: {'+'.join(chord.input_keys)} → {chord.output_text}")
            except Exception as e:
                click.echo(f"   ✗ Failed to remove chord: {e}")
        
        # Update Karabiner
        all_chords = self.chord_manager.get_all_chords()
        self.karabiner.update_all_chords(all_chords)
        
        click.echo(f"\n✅ Undo complete!")
    
    def show_similar_chords(self, input_keys: str):
        """Show chords with similar keys to help avoid conflicts."""
        keys_set = set(input_keys.replace('+', '').replace(' ', '').lower())
        
        similar = []
        for chord in self.chord_manager.get_all_chords():
            chord_keys_set = set(chord.input_keys)
            
            # Find overlap
            overlap = keys_set & chord_keys_set
            if overlap:
                similarity = len(overlap) / max(len(keys_set), len(chord_keys_set))
                if similarity >= 0.5:  # 50% or more keys in common
                    similar.append((chord, similarity, overlap))
        
        if similar:
            click.echo(f"\n⚠️  Found {len(similar)} similar chord(s):")
            for chord, sim, overlap in sorted(similar, key=lambda x: -x[1]):
                overlap_str = '+'.join(sorted(overlap))
                click.echo(f"   {'+'.join(chord.input_keys)} → '{chord.output_text}'")
                click.echo(f"      (shares: {overlap_str})")
    
    def suggest_common_chords(self):
        """Suggest common chords to add."""
        common_chords = [
            # Common words
            ("t+h+e", "the"),
            ("a+n+d", "and"),
            ("t+h+a", "that"),
            ("w+i+t", "with"),
            ("f+o+r", "for"),
            ("t+h+i", "this"),
            ("y+o+u", "you"),
            ("h+a+v", "have"),
            ("b+u+t", "but"),
            ("n+o+t", "not"),
            
            # Programming
            ("f+u+n", "function"),
            ("r+e+t", "return"),
            ("i+m+p", "import"),
            ("c+l+s", "class"),
            ("d+e+f", "def"),
            
            # Common phrases
            ("t+y", "thank you"),
            ("p+l+s", "please"),
            ("b+t+w", "by the way"),
        ]
        
        existing_keys = {frozenset(chord.input_keys) for chord in self.chord_manager.get_all_chords()}
        
        suggestions = []
        for keys_str, output in common_chords:
            keys = keys_str.split('+')
            if frozenset(sorted(keys)) not in existing_keys:
                suggestions.append((keys_str, output))
        
        if suggestions:
            click.echo("\n💡 Suggested common chords to add:")
            for i, (keys, output) in enumerate(suggestions[:10], 1):
                click.echo(f"   {i}. {keys} → '{output}'")
            
            click.echo(f"\n   Use 'fc add \"{suggestions[0][0]}\" \"{suggestions[0][1]}\"' to add one")
    
    def _add_to_history(self, chord):
        """Add chord to undo history."""
        self.last_added.append(chord)
        if len(self.last_added) > self.max_history:
            self.last_added.pop(0)

