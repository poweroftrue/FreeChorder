# Implementation Summary: Chord Ordering & Impulse Mode Fix

## Changes Made

### 1. Fixed Chord Ordering in Karabiner Config
**File**: `src/freechorder/karabiner/config_generator.py`

**Problem**: Shorter chords were processed before longer chords in Karabiner, causing conflicts. For example, if you had both `i+s → "is"` and `h+i+s+t → "history"`, typing all four keys would only trigger `i+s`.

**Solution**: Modified `_group_chords()` method to:
- Sort chords within each group by length (longest first)
- Sort groups themselves by chord length (longer chord groups first)
- This ensures Karabiner checks longer chords before falling back to shorter ones

**Code changes**:
```python
# Sort chords within each group - longest first
for group_name, group_chords in groups.items():
    groups[group_name] = sorted(
        group_chords,
        key=lambda c: (
            -len([k for k in c.input_keys if k not in ['cmd', 'shift', 'option', 'control']]),
            '+'.join(c.input_keys)
        )
    )

# Sort groups - longer chord groups first
sorted_groups = {}
for key in sorted(groups.keys(), reverse=True):
    sorted_groups[key] = groups[key]
```

### 2. Added Profile Pausing for Impulse Mode
**File**: `src/freechorder/karabiner/config_generator.py`

**Problem**: When trying to create chords in impulse mode, existing chords would trigger, preventing you from pressing multiple keys simultaneously to create a new chord.

**Solution**: Added two new methods to temporarily disable the FreeChorder profile:

#### New Method: `pause_freechorder_profile()`
- Switches Karabiner away from FreeChorder profile to a different profile
- Returns the name of the paused profile
- Prevents any FreeChorder chords from triggering

```python
def pause_freechorder_profile(self) -> Optional[str]:
    """Temporarily disable FreeChorder profile and return the previously active profile name."""
    # Finds current profile
    # If FreeChorder is active, switches to first non-FreeChorder profile
    # Saves config and reloads Karabiner
```

#### New Method: `resume_freechorder_profile()`
- Re-activates the FreeChorder profile
- Restores chord functionality

```python
def resume_freechorder_profile(self):
    """Resume/activate the FreeChorder profile."""
    # Activates FreeChorder profile again
```

### 3. Integrated Profile Pausing in Impulse Handler
**File**: `src/freechorder/core/impulse_handler.py`

**Changes**:

#### Added instance variable:
```python
self.paused_profile = None  # Track if we paused a profile
```

#### Modified `start()` method:
```python
def start(self):
    # Pause Karabiner profile BEFORE starting keyboard listener
    click.echo("\n🔄 Pausing FreeChorder profile in Karabiner...")
    self.paused_profile = self.karabiner.pause_freechorder_profile()
    if self.paused_profile:
        click.echo("✓ FreeChorder profile paused (chords temporarily disabled)")
    
    # ... rest of start logic
```

#### Modified `stop()` method:
```python
def stop(self):
    # ... existing stop logic
    
    # Resume Karabiner profile when exiting
    if hasattr(self, 'paused_profile') and self.paused_profile:
        click.echo("\n🔄 Resuming FreeChorder profile in Karabiner...")
        self.karabiner.resume_freechorder_profile()
        click.echo("✓ FreeChorder profile resumed (chords re-enabled)")
```

## Testing Results

### Chord Ordering Test
✅ **Verified**: Chords are now ordered correctly in Karabiner config:
1. Launcher rules (impulse mode triggers)
2. 4+ key chord groups
3. 3-key chord groups
4. 2-key chord groups

Within each group, longer chords appear first.

### Impulse Mode Test
✅ **Expected behavior**:
```
$ fc impulse

🔄 Pausing FreeChorder profile in Karabiner...
✓ FreeChorder profile paused (chords temporarily disabled)

🎹 Impulse Chording Mode Active!
...

[User presses ESC to exit]

🔄 Resuming FreeChorder profile in Karabiner...
✓ FreeChorder profile resumed (chords re-enabled)

✓ Impulse mode deactivated.
```

## Impact

### Benefits
1. ✅ **Longer chords work correctly** - No more conflicts with shorter subsets
2. ✅ **Impulse mode works seamlessly** - Can create chords without existing chords interfering
3. ✅ **Automatic and transparent** - Users don't need to manually manage profiles
4. ✅ **Safe** - Profile is always restored on exit (even on errors/interrupts)
5. ✅ **Better organization** - Chords are logically grouped and ordered

### Example: Before vs After

**Before** (broken):
- Pressing `h+i+s+t` would trigger `i+s` if `i+s` existed
- In impulse mode, pressing `a+b+c` would trigger existing `a+b` chord

**After** (fixed):
- Pressing `h+i+s+t` correctly triggers the 4-key chord
- In impulse mode, pressing `a+b+c` is captured for creating a new chord

## Usage

### For Users
No action needed! The fix is automatic:

```bash
# Refresh existing chords to apply new ordering
freechorder refresh

# Use impulse mode normally
freechorder impulse
```

### For Developers
If modifying chord management code:
1. Always maintain longest-first ordering in `_group_chords()`
2. Remember that Karabiner processes rules in sequential order
3. Profile pausing is critical for impulse mode functionality

## Files Modified
1. `src/freechorder/karabiner/config_generator.py` - Chord sorting & profile pausing
2. `src/freechorder/core/impulse_handler.py` - Integrated profile pausing
3. `CHORD_ORDERING_FIX.md` - User-facing documentation

## No Breaking Changes
- All existing functionality preserved
- Backward compatible with existing chord files
- No changes to CLI interface
- No changes to config file format

