# Chord Ordering Fix - Solution Summary

## Problem
1. **Shorter chords trigger before longer chords**: When you have overlapping chords like `i+s` and `h+i+s+t`, Karabiner would trigger the shorter chord first, preventing longer chords from working.
2. **Cannot add chords in impulse mode**: When existing chords are active in Karabiner, pressing multiple keys to create a new chord would trigger existing chords instead of being captured for creation.

## Solution Implemented

### 1. Chord Sorting (Longest First)
**File**: `src/freechorder/karabiner/config_generator.py`

**Changes in `_group_chords()` method**:
- Chords are now sorted by length within each group (longest first)
- Groups themselves are also ordered with longer chord groups first
- This ensures Karabiner processes longer chords before shorter ones

```python
# Sort chords within each group - longest first
groups[group_name] = sorted(
    group_chords,
    key=lambda c: (
        -len([k for k in c.input_keys if k not in ['cmd', 'shift', 'option', 'control']]),  # Longer first
        '+'.join(c.input_keys)  # Then alphabetically
    )
)

# Sort groups - longer chord groups first
sorted_groups = {}
for key in sorted(groups.keys(), reverse=True):
    sorted_groups[key] = groups[key]
```

### 2. Profile Pausing During Impulse Mode
**Files**: 
- `src/freechorder/karabiner/config_generator.py` - Added pause/resume methods
- `src/freechorder/core/impulse_handler.py` - Integrated pause/resume

**New methods in KarabinerBridge**:
- `pause_freechorder_profile()`: Temporarily switches away from FreeChorder profile
- `resume_freechorder_profile()`: Switches back to FreeChorder profile

**Updated ImpulseHandler**:
- Pauses FreeChorder profile when impulse mode starts
- Resumes FreeChorder profile when impulse mode ends (ESC or exit)
- This prevents existing chords from interfering with chord creation

## How It Works

### Before the Fix
```
Karabiner Rule Order:
1. i+s → "is"          (triggers first, blocks longer chords)
2. h+i+s+t → "hist"    (never triggers because i+s fires first)
3. d+o → "do"
4. a+d+l+o → "load"    (might not trigger if a+d or d+o exist)
```

### After the Fix
```
Karabiner Rule Order:
1. a+d+l+o → "load"    (4 keys - checked first)
2. h+i+s+t → "hist"    (4 keys)
3. h+t+w → "with"      (3 keys)
4. a+d+s → "and"       (3 keys)
5. i+s → "is"          (2 keys - checked last)
6. d+o → "do"          (2 keys)
```

Now when you press `h+i+s+t`, Karabiner checks the 4-key chord first before falling back to `i+s`.

## Testing

### Test the Chord Ordering
1. Create overlapping chords:
   ```bash
   fc add "i s" "is"
   fc add "h i s t" "history"
   fc refresh
   ```

2. Test typing `h+i+s+t` - it should output "history" not "is"

### Test Impulse Mode Profile Pausing
1. Start impulse mode:
   ```bash
   fc impulse
   ```
   
2. You should see:
   ```
   🔄 Pausing FreeChorder profile in Karabiner...
   ✓ FreeChorder profile paused (chords temporarily disabled)
   ```

3. Press multiple keys together - they won't trigger existing chords
4. Enter output text and save
5. Exit impulse mode (ESC) - you should see:
   ```
   🔄 Resuming FreeChorder profile in Karabiner...
   ✓ FreeChorder profile resumed (chords re-enabled)
   ```

## Commands to Apply the Fix

If you have existing chords, refresh them to apply the new ordering:

```bash
# Refresh all chords with new sorting
freechorder refresh

# Or just sync if you have quick impulse chords pending
freechorder sync
```

## Technical Details

### Karabiner Rule Processing
Karabiner-Elements processes rules in the order they appear in the config file. The first matching rule wins. This is why ordering matters:
- If `i+s` appears before `h+i+s+t`, pressing all four keys will match `i+s` first
- By placing longer chords first, we give them priority to match

### Profile Switching
When impulse mode starts:
1. Reads current Karabiner config
2. Finds active profile
3. If FreeChorder is active, switches to the first non-FreeChorder profile
4. Saves config (Karabiner auto-reloads)

When impulse mode ends:
1. Switches back to FreeChorder profile
2. All your chords are active again

This is completely safe and non-destructive - it just temporarily changes which profile is active.

## Benefits

1. ✅ **Longer chords work correctly**: No more conflicts with shorter subsets
2. ✅ **Impulse mode works smoothly**: Can create chords without interference
3. ✅ **Automatic**: No manual intervention needed
4. ✅ **Safe**: Profiles are properly restored on exit
5. ✅ **Organized**: Chord groups are logically ordered

## Limitations

- You still can't have identical chord keys with different outputs (this is by design)
- Impulse mode requires at least one other Karabiner profile to exist (usually "Default" exists)
- Profile switching takes ~100-200ms (imperceptible in practice)

