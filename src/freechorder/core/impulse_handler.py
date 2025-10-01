"""
Impulse chording handler for FreeChorder
Allows creating chords on-the-fly while typing
"""

import sys
import time
import threading
from typing import Set, List, Callable, Optional
from pynput import keyboard
import click

from freechorder.core.chord_manager import ChordManager, ChordConflictError
from freechorder.karabiner.config_generator import KarabinerBridge


class ImpulseHandler:
    """Handles impulse chording - creating chords on the fly."""
    
    def __init__(self, chord_manager: ChordManager, karabiner: KarabinerBridge, config=None):
        """Initialize the impulse handler."""
        self.chord_manager = chord_manager
        self.karabiner = karabiner
        self.config = config
        self.pressed_keys: Set[str] = set()
        self.chord_start_time: Optional[float] = None
        
        # Load timing from config or use defaults
        if config:
            self.chord_timeout = config.chord_timeout_ms / 1000.0  # Convert ms to seconds
            self.min_chord_size = config.min_chord_size
        else:
            self.chord_timeout = 0.1  # 100ms window for chord detection
            self.min_chord_size = 2
            
        # Copy the sensitivity map from karabiner for display purposes
        self.sensitivity_map = karabiner.sensitivity_map if hasattr(karabiner, 'sensitivity_map') else {
            2: 50,
            3: 75,
            4: 100,
            5: 125
        }
            
        self.active = False
        self.listener = None
        self.detection_timer = None
        self.input_mode = False  # Flag to indicate we're getting user input
        self.trigger_combination = {'cmd', 'shift', 'i'}  # Default trigger
        self.trigger_pressed = set()
        self.paused_profile = None  # Track if we paused a profile
        
    def start(self):
        """Start monitoring keyboard input."""
        self.active = True
        
        # Pause Karabiner FreeChorder profile to prevent chord interference
        click.echo("\n🔄 Pausing FreeChorder profile in Karabiner...")
        self.paused_profile = self.karabiner.pause_freechorder_profile()
        if self.paused_profile:
            click.echo("✓ FreeChorder profile paused (chords temporarily disabled)")
        else:
            click.echo("⚠️  FreeChorder profile not active or already paused")
        
        click.echo("\n🎹 Impulse Chording Mode Active!")
        click.echo("=" * 50)
        click.echo("How to use:")
        click.echo("1. Press multiple keys simultaneously (2+ keys)")
        click.echo("2. When prompted, type the output text")
        click.echo("3. Press Enter to save the chord")
        click.echo(f"4. Press {'+'.join(sorted(self.trigger_combination))} to toggle impulse mode")
        click.echo("5. Press ESC to exit")
        click.echo("=" * 50)
        click.echo("\n⚙️  Dynamic chord sensitivity:")
        click.echo("   • 2 keys: 50ms (strict)")
        click.echo("   • 3 keys: 75ms (moderate)")
        click.echo("   • 4 keys: 100ms (default)")
        click.echo("   • 5+ keys: 125ms (relaxed)")
        click.echo("\nListening for chords...")
        
        # Check for the "not trusted" error by capturing stderr
        import io
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            
            # Check for immediate errors
            time.sleep(0.2)
            stderr_output = sys.stderr.getvalue()
            
            if "not trusted" in stderr_output:
                sys.stderr = old_stderr  # Restore stderr
                click.echo("\n❌ macOS Security Error: This process is not trusted!")
                click.echo("\nYour terminal needs accessibility permissions to monitor keyboard input.")
                click.echo("\n🔧 To fix this:")
                click.echo("1. Open System Settings → Privacy & Security → Accessibility")
                click.echo("2. Find and check your terminal application")
                click.echo("3. IMPORTANT: Completely quit and restart your terminal")
                click.echo("4. Run 'freechorder impulse' again")
                click.echo("\nFor detailed help, run: freechorder permissions")
                self.stop()
                return
            
            sys.stderr = old_stderr  # Restore stderr
            
            # Keep the program running
            while self.active:
                time.sleep(0.1)
                if self.listener and not self.listener.running and not self.input_mode:
                    click.echo("\n⚠️  Keyboard listener stopped unexpectedly.")
                    self.active = False
                    break
                    
        except KeyboardInterrupt:
            sys.stderr = old_stderr
            self.stop()
        except Exception as e:
            sys.stderr = old_stderr
            click.echo(f"\n✗ Error: {str(e)}")
            self.stop()
    
    def stop(self):
        """Stop monitoring keyboard input."""
        self.active = False
        if self.listener:
            self.listener.stop()
        if self.detection_timer:
            self.detection_timer.cancel()
        
        # Resume Karabiner FreeChorder profile
        if hasattr(self, 'paused_profile') and self.paused_profile:
            click.echo("\n🔄 Resuming FreeChorder profile in Karabiner...")
            self.karabiner.resume_freechorder_profile()
            click.echo("✓ FreeChorder profile resumed (chords re-enabled)")
        
        click.echo("\n✓ Impulse mode deactivated.")
    
    def _get_key_name(self, key) -> Optional[str]:
        """Get normalized key name from pynput key object."""
        try:
            # Handle character keys
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            
            # Handle special keys
            special_key_map = {
                keyboard.Key.space: 'space',
                keyboard.Key.enter: 'return',
                keyboard.Key.tab: 'tab',
                keyboard.Key.backspace: 'backspace',
                keyboard.Key.delete: 'delete',
                keyboard.Key.esc: 'escape',
                keyboard.Key.cmd: 'cmd',
                keyboard.Key.cmd_l: 'cmd',
                keyboard.Key.cmd_r: 'cmd',
                keyboard.Key.shift: 'shift',
                keyboard.Key.shift_l: 'shift',
                keyboard.Key.shift_r: 'shift',
                keyboard.Key.alt: 'option',
                keyboard.Key.alt_l: 'option',
                keyboard.Key.alt_r: 'option',
                keyboard.Key.ctrl: 'control',
                keyboard.Key.ctrl_l: 'control',
                keyboard.Key.ctrl_r: 'control',
            }
            
            if key in special_key_map:
                return special_key_map[key]
            
            # Handle function keys and others
            if hasattr(key, 'name'):
                return key.name
            
        except AttributeError:
            pass
        
        return None
    
    def _on_press(self, key):
        """Handle key press event."""
        if not self.active:
            return
        
        # Check for ESC to exit
        if key == keyboard.Key.esc:
            self.stop()
            return False
        
        # Get key name
        key_name = self._get_key_name(key)
        if not key_name:
            return
        
        # Check for trigger combination
        if key_name in self.trigger_combination:
            self.trigger_pressed.add(key_name)
            if self.trigger_pressed == self.trigger_combination:
                # Toggle detection
                click.echo("\n[Impulse detection paused - press trigger again to resume]")
                self.trigger_pressed.clear()
                return
        
        # Skip modifier keys for chord detection
        if key_name in ['cmd', 'shift', 'option', 'control']:
            return
        
        # Track timing
        current_time = time.time()
        if not self.chord_start_time or (current_time - self.chord_start_time) > self.chord_timeout:
            self.pressed_keys.clear()
            self.chord_start_time = current_time
        
        # Add key to potential chord
        self.pressed_keys.add(key_name)
        
        # Cancel previous timer
        if self.detection_timer:
            self.detection_timer.cancel()
        
        # Start new detection timer
        if len(self.pressed_keys) >= self.min_chord_size:
            self.detection_timer = threading.Timer(self.chord_timeout, self._detect_chord)
            self.detection_timer.start()
    
    def _on_release(self, key):
        """Handle key release event."""
        key_name = self._get_key_name(key)
        if key_name and key_name in self.trigger_combination:
            self.trigger_pressed.discard(key_name)
    
    def _detect_chord(self):
        """Detect and create chord from pressed keys."""
        if len(self.pressed_keys) >= self.min_chord_size:
            chord_keys = sorted(list(self.pressed_keys))
            
            # Check if this chord already exists
            existing = self._check_existing_chord(chord_keys)
            if existing:
                click.echo(f"\n⚠️  Chord {'+'.join(chord_keys)} already exists → {existing.output_text}")
                self.pressed_keys.clear()
                self.chord_start_time = None
                return
            
        # Calculate the sensitivity for this chord
        non_modifier_keys = [key for key in chord_keys 
                           if key not in ['cmd', 'shift', 'option', 'control']]
        chord_length = len(non_modifier_keys)
        
        # Get sensitivity value
        if chord_length <= 2:
            sensitivity = self.sensitivity_map[2]
        elif chord_length == 3:
            sensitivity = self.sensitivity_map[3]
        elif chord_length == 4:
            sensitivity = self.sensitivity_map[4]
        else:
            sensitivity = self.sensitivity_map[5]
        
        click.echo(f"\n\n🎯 Detected chord: {'+'.join(chord_keys)} (sensitivity: {sensitivity}ms)")
        
        # Temporarily pause listener to get user input
        self.input_mode = True  # Flag that we're in input mode
        if self.listener:
            self.listener.stop()
            self.listener = None
            
        # Small delay to ensure keyboard listener is fully stopped
        time.sleep(0.2)
        
        # Clear any buffered input from the chord keys using termios
        # This is necessary because the chord keys might be in the input buffer
        try:
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except:
            # Fallback for non-Unix systems or if termios fails
            import select
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                try:
                    sys.stdin.read(1)
                except:
                    break
        
        # Additional delay to ensure all keys are flushed
        time.sleep(0.3)
        
        # Prompt for output
        try:
            # Use input() instead of click.prompt to avoid conflicts
            click.echo("\nEnter output text (or 'skip' to cancel):")
            sys.stdout.flush()
            output = input(">>> ").strip()
            
            if output and output.lower() != 'skip':
                # Add the chord
                try:
                    chord = self.chord_manager.add_chord(
                        input_keys=chord_keys,
                        output_text=output,
                        category="impulse"
                    )
                    
                    # Update Karabiner configuration
                    all_chords = self.chord_manager.get_all_chords()
                    self.karabiner.update_all_chords(all_chords)
                    
                    click.echo(f"✓ Chord created: {'+'.join(chord_keys)} → {output}")
                    click.echo("The chord is now active!")
                    
                except ChordConflictError as e:
                    click.echo(f"✗ Error: {str(e)}")
                except Exception as e:
                    click.echo(f"✗ Error creating chord: {str(e)}")
            else:
                click.echo("✗ Chord creation cancelled")
            
        except (EOFError, KeyboardInterrupt):
            click.echo("\n✗ Chord creation cancelled")
        except Exception as e:
            click.echo(f"\n✗ Error getting input: {str(e)}")
        
        # Reset state
        self.pressed_keys.clear()
        self.chord_start_time = None
        
        # Restart listener
        click.echo("\nListening for chords...")
        self.input_mode = False  # No longer in input mode
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def _check_existing_chord(self, keys: List[str]) -> Optional['Chord']:
        """Check if a chord with these keys already exists."""
        try:
            # Check in the chord manager's input index
            key_set = frozenset(keys)
            if key_set in self.chord_manager.input_index:
                chord_id = self.chord_manager.input_index[key_set]
                return self.chord_manager.chords.get(chord_id)
        except:
            pass
        return None
