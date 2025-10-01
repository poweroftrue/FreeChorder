#!/usr/bin/env python3
"""
Quick impulse mode - Minimal startup time version
Bypasses heavy imports and initialization for faster chord creation
"""

import sys
import time
from pathlib import Path

def quick_impulse():
    """Ultra-fast impulse mode with minimal dependencies."""
    print("\n⚡ Quick Impulse Mode (Fast Start)")
    print("=" * 40)
    print("Press 2+ keys together, then enter output")
    print("Press Ctrl+C to exit\n")
    
    # Lazy import only what we absolutely need
    from pynput import keyboard
    
    pressed_keys = set()
    chord_timeout = 0.1
    last_press_time = 0
    
    def on_press(key):
        nonlocal last_press_time, pressed_keys
        
        current_time = time.time()
        if current_time - last_press_time > chord_timeout:
            pressed_keys.clear()
        
        last_press_time = current_time
        
        try:
            if hasattr(key, 'char') and key.char:
                pressed_keys.add(key.char)
            elif hasattr(key, 'name'):
                # Skip modifiers
                if key.name not in ['cmd', 'shift', 'option', 'control', 'alt']:
                    pressed_keys.add(key.name)
        except:
            pass
            
        if len(pressed_keys) >= 2:
            # Stop listener and get input
            return False
    
    def save_chord(keys, output):
        """Quickly append chord to file without heavy imports."""
        import json
        import uuid
        from datetime import datetime
        
        chord_file = Path.home() / '.config' / 'freechorder' / 'chords.yaml'
        
        # Quick and dirty append for speed
        chord_data = {
            'id': str(uuid.uuid4()),
            'input_keys': sorted(list(keys)),
            'output_text': output,
            'output_type': 'text',
            'created_at': datetime.now().isoformat(),
            'category': 'quick_impulse'
        }
        
        # Just append to a quick cache file
        cache_file = Path.home() / '.config' / 'freechorder' / '.quick_chords_cache'
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_file, 'a') as f:
            f.write(json.dumps(chord_data) + '\n')
        
        print(f"✓ Chord saved: {'+'.join(sorted(keys))} → {output}")
        print("  (Run 'fc sync' later to update Karabiner)\n")
    
    try:
        while True:
            pressed_keys.clear()
            
            # Listen for chord
            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()
            
            if len(pressed_keys) >= 2:
                chord_keys = list(pressed_keys)
                print(f"\n🎯 Chord: {'+'.join(sorted(chord_keys))}")
                
                # Simple input without heavy libraries
                try:
                    output = input("Output: ").strip()
                    if output:
                        save_chord(chord_keys, output)
                except KeyboardInterrupt:
                    print("\n✗ Cancelled")
                    
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n✓ Quick impulse mode ended")
        print("Remember to run 'fc sync' to activate your new chords!")

if __name__ == '__main__':
    quick_impulse()
