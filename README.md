# FreeChorder 🎹

A software-based CharaChorder alternative for macOS that brings chord-based typing to any keyboard using Karabiner-Elements as the backend.

## What is FreeChorder?

FreeChorder is a terminal application that allows you to:
- Define keyboard chords (simultaneous key combinations) that output text or commands
- Manage chords through a simple CLI interface
- Create chords on-the-fly with impulse chording
- Search and organize your chord library
- Import existing CharaChorder chord libraries
- Fine-tune chord detection sensitivity to match your typing speed (automatically updates all existing chords!)

Think of it as text expansion on steroids - instead of typing full words or phrases, you can press multiple keys at once to instantly output the text you need.

### ⚡ Performance Options

| Mode | Startup Time | Features | Best For |
|------|-------------|----------|----------|
| Regular (`fc impulse`) | ~2 seconds | Full features, accessibility checks | Learning & configuration |
| Quick (`fcq` or Cmd+Opt+Del) | ~0.5 seconds | Minimal startup, batch sync | Frequent chord creation |
| Native (Shift+Opt+Del) | Instant! | Dialog-based, no Python | Ultra-fast single chords |

## Example Usage

```bash
# Add a chord: pressing a+s+d simultaneously outputs "and"
freechorder add "asd" "and"

# Add another chord for "the"
freechorder add "teh" "the"

# Search for chords
freechorder search "and"

# List all chords
freechorder list


# Enter impulse mode to create chords while typing
freechorder impulse
# or use the shortcut: fc impulse

# Quick launch impulse mode: 
# - Press Ctrl+Option+Delete for regular mode
# - Press Cmd+Option+Delete for fast mode (⚡ ~0.5s startup)
# - Press Shift+Option+Delete for instant dialog (⚡⚡ no delay!

# Activate the FreeChorder profile in Karabiner
freechorder activate

# Configure chord sensitivity (default: 100ms)
# This automatically updates ALL existing chords to use the new timing!
freechorder config --chord-timeout 150  # More forgiving for slower typing
freechorder config --chord-timeout 75   # Tighter timing for faster typists
freechorder config --show               # Show current configuration

# Refresh all chords with current settings (including dynamic sensitivity)
freechorder refresh

# Export chords to modular JSON files for better organization
freechorder export --format modular  # Creates separate files by chord length/category
freechorder export --format integrated  # Updates single Karabiner config (default)

# Manage chord groups (enable/disable groups of chords)
freechorder groups --list  # Show all groups and their status
freechorder groups --disable "2-Key Chords (Quick)"  # Disable all 2-key chords
freechorder groups --enable "3-Key Chords (Standard)"  # Re-enable 3-key chords
```

### Modular Configuration

FreeChorder now supports modular rule organization, inspired by best practices from the chording community:

- **Separate rule files**: Export chords to individual JSON files grouped by length or category
- **Better maintainability**: Each file contains related chords, making it easier to manage
- **Selective enabling**: Enable/disable entire groups of chords without deleting them
- **Version control friendly**: Smaller, focused files are easier to track in git

To use modular configuration:
```bash
# Export to separate files
freechorder export --format modular

# Files are saved to ~/.config/freechorder/karabiner_rules/
# Copy them to Karabiner's complex modifications folder:
cp ~/.config/freechorder/karabiner_rules/*.json ~/.config/karabiner/assets/complex_modifications/

# Then enable them in Karabiner-Elements UI
```

### Dynamic Sensitivity

FreeChorder now automatically adjusts chord detection sensitivity based on the number of keys:

- **2-key chords**: 50ms (strict) - Prevents accidental triggers during fast typing
- **3-key chords**: 75ms (moderate) - Balanced sensitivity
- **4-key chords**: 100ms (default) - Standard timing
- **5+ key chords**: 125ms (relaxed) - More time for complex chords

This ensures that simple 2-letter combinations don't trigger accidentally while still allowing comfortable timing for complex chords.

### Keyboard Shortcuts & Fast Launch Options

FreeChorder includes multiple ways to start impulse mode, from regular to ultra-fast:

#### System-wide Shortcuts (when FreeChorder profile is active):
- **`Ctrl+Option+Delete`**: Regular impulse mode (~2 seconds startup)
- **`Cmd+Option+Delete`**: Quick impulse mode (~0.5 seconds startup) ⚡
- **`Shift+Option+Delete`**: Native dialog mode (instant - no Python!) ⚡⚡

#### Terminal Commands:
- `fc impulse` - Regular impulse mode with all features
- `fcq` - Quick impulse mode (minimal startup time)
- `fc sync` - Sync quick chords to Karabiner after using fast modes

### Using Fast Modes

The quick modes (fcq and native dialog) save chords to a cache for speed. Remember to sync them:

```bash
# After creating chords with fcq or native dialog:
fc sync  # This activates your new chords in Karabiner

# First time setup for fcq alias:
source ~/.zshrc  # Or restart terminal
```

## Project Documentation

This repository contains comprehensive documentation for building FreeChorder:

### 📋 [PROJECT_PLAN.md](PROJECT_PLAN.md)
Complete project plan covering:
- Project overview and objectives
- Technical architecture
- Feature specifications
- Implementation timeline
- CharaChorder compatibility details
- Testing and deployment strategies

### 🚀 [QUICK_START_IMPLEMENTATION.md](QUICK_START_IMPLEMENTATION.md)
Actionable implementation guide for building the MVP:
- Day-by-day development plan
- Essential code snippets
- MVP feature prioritization
- Common issues and solutions
- Testing checklist

### 🏗️ [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)
Detailed technical design document including:
- System architecture diagrams
- Component specifications with code examples
- Data structures and storage formats
- Performance optimization strategies
- Security considerations
- Error handling patterns

## Quick Start for Developers

1. **Read the documentation in this order:**
   - Start with `PROJECT_PLAN.md` for the big picture
   - Follow `QUICK_START_IMPLEMENTATION.md` to begin coding
   - Reference `TECHNICAL_ARCHITECTURE.md` for detailed implementations

2. **Prerequisites:**
   - macOS (10.15 or later)
   - Python 3.9+
   - Karabiner-Elements installed
   - Basic familiarity with terminal applications

3. **Key Technologies:**
   - **Python**: Main application language
   - **Karabiner-Elements**: Keyboard remapping backend
   - **Click/Typer**: CLI framework
   - **YAML/JSON**: Configuration storage

## Core Features

- **Chord Management**: Add, remove, edit, and search chords
- **Impulse Chording**: Create chords on-the-fly while typing
- **Conflict Detection**: Prevents chord conflicts automatically
- **Import/Export**: Compatible with CharaChorder CSV format
- **Statistics**: Track chord usage and typing improvements
- **Backup/Restore**: Never lose your chord configurations

## Why FreeChorder?

- **Free and Open Source**: No hardware purchase required
- **Customizable**: Full control over your chord library
- **Portable**: Your chords work on any Mac with Karabiner-Elements
- **Extensible**: Easy to add new features and integrations
- **Community-Driven**: Share and import chord libraries

## Development Status

This is the planning phase of FreeChorder. The documentation provides everything needed to build a fully functional system. The actual implementation can be completed in approximately 2-4 weeks following the provided guides.

## Contributing

Once the initial implementation is complete, contributions will be welcome! Areas for contribution include:
- Additional chord management features
- GUI application development
- Cross-platform support
- Machine learning for chord suggestions
- Community chord library platform

## License

This project will be released under the MIT License, making it free for personal and commercial use.

---

Ready to build the future of chord-based typing on macOS? Start with the [PROJECT_PLAN.md](PROJECT_PLAN.md) and let's make typing faster and more efficient for everyone! 🚀
