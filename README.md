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
# ===== ADDING CHORDS =====

# Interactive mode - Best for beginners (prompts for everything)
fc add

# Quick add with preview and confirmation
fc add "asd" "and"

# Super quick - no confirmation (for power users)
fc add "the" "the" --no-confirm

# Add with category
fc add "fun" "function" --category "programming"

# Batch add from file
fc add --batch my_chords.txt

# Get suggestions for common chords
fc suggest


# ===== MANAGING CHORDS =====

# List all chords
fc list

# Search for chords
fc search "and"

# Remove a chord
fc remove "asd"

# Undo last chord addition (lifesaver!)
fc undo

# Undo last 3 additions
fc undo 3

# View statistics
fc stats

# Detailed statistics breakdown
fc stats --detailed


# ===== IMPULSE MODE (Create Chords While Typing) =====

# Enter impulse mode - creates chords on-the-fly
fc impulse

# Quick launch impulse mode with keyboard shortcuts:
# - Ctrl+Option+Delete: Regular mode (~2 sec startup)
# - Cmd+Option+Delete: Quick mode (~0.5 sec startup) ⚡
# - Shift+Option+Delete: Native dialog (instant!) ⚡⚡

# Sync quick chords after using fast modes
fc sync


# ===== CONFIGURATION =====

# Activate the FreeChorder profile in Karabiner
fc activate

# Configure chord sensitivity (automatically updates all chords!)
fc config --chord-timeout 150  # More forgiving for slower typing
fc config --chord-timeout 75   # Tighter timing for faster typists
fc config --show               # Show current configuration

# Refresh all chords with current settings
fc refresh

# Export chords to modular JSON files
fc export --format modular  # Separate files by length/category
fc export --format integrated  # Single Karabiner config (default)


# ===== CHORD GROUPS =====

# Manage chord groups (enable/disable sets of chords)
fc groups --list  # Show all groups and their status
fc groups --disable "2-Key Chords (Quick)"  # Disable all 2-key chords
fc groups --enable "3-Key Chords (Standard)"  # Re-enable 3-key chords


# ===== PERMISSIONS =====

# Check accessibility permissions (needed for impulse mode)
fc permissions
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

### 📚 User Guides

#### 🎯 [IMPROVEMENTS_GUIDE.md](IMPROVEMENTS_GUIDE.md)
Complete guide to the enhanced features:
- Interactive chord addition workflow
- Undo functionality usage
- Batch import from files
- Chord suggestions system
- Before/after comparisons

#### 📖 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
Quick command reference card:
- All commands with examples
- Common workflows
- Troubleshooting tips
- Decision trees for choosing commands

#### 📊 [STATS_FIX.md](STATS_FIX.md)
Statistics and analytics guide:
- Understanding chord distributions
- Category breakdowns
- Recent activity tracking
- Detailed view usage

### 🔧 Technical Documentation (For Developers)

#### 🔬 [RESEARCH_AND_IMPROVEMENTS_SUMMARY.md](RESEARCH_AND_IMPROVEMENTS_SUMMARY.md)
Comprehensive implementation summary:
- UX research and pain points identified
- Solutions implemented with code details
- Before/after metrics and comparisons
- Future enhancement roadmap

#### 📝 [CHORD_ORDERING_FIX.md](CHORD_ORDERING_FIX.md)
Critical bug fix documentation:
- Problem: Shorter chords triggering before longer ones
- Solution: Longest-first sorting algorithm
- Profile pausing during impulse mode
- Testing and verification results

## Quick Start for Users

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/freechorder.git
cd freechorder

# Create virtual environment and install
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Install Karabiner-Elements
# Download from: https://karabiner-elements.pqrs.org/
```

### First Steps
```bash
# 1. Get suggestions for common chords
fc suggest

# 2. Add your first chord interactively
fc add
# Follow the prompts...

# 3. Activate FreeChorder in Karabiner
fc activate

# 4. Test it! Press your chord keys in any app
# They should output the text you defined

# 5. View your chords
fc list

# 6. See statistics
fc stats
```

### For Beginners
1. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick command guide
2. Read [IMPROVEMENTS_GUIDE.md](IMPROVEMENTS_GUIDE.md) - Feature walkthrough
3. Start with `fc suggest` to get ideas
4. Use `fc add` (interactive mode) to learn the system

### For Power Users
1. Create a batch file with your chords
2. Import with `fc add --batch chords.txt`
3. Use `--no-confirm` flag for speed
4. Adjust timing with `fc config`

## Quick Start for Developers

1. **Read the documentation in this order:**
   - Start with `RESEARCH_AND_IMPROVEMENTS_SUMMARY.md` for implementation details
   - Check `CHORD_ORDERING_FIX.md` and `STATS_FIX.md` for critical fixes
   - Review the code in `src/freechorder/` for implementation

2. **Prerequisites:**
   - macOS (10.15 or later)
   - Python 3.9+
   - Karabiner-Elements installed
   - Basic familiarity with terminal applications

3. **Key Technologies:**
   - **Python 3.9+**: Main application language
   - **Click**: CLI framework for commands
   - **Karabiner-Elements**: Keyboard remapping backend
   - **pynput**: Keyboard monitoring for impulse mode
   - **YAML/JSON**: Configuration storage
   - **PyObjC**: macOS integration

4. **Project Structure:**
   ```
   freechorder/
   ├── src/freechorder/
   │   ├── cli/
   │   │   ├── main.py              # Main CLI entry point
   │   │   ├── interactive_add.py   # Enhanced chord addition
   │   │   └── quick_impulse.py     # Fast impulse mode
   │   ├── core/
   │   │   ├── chord_manager.py     # Chord CRUD operations
   │   │   └── impulse_handler.py   # Real-time chord creation
   │   ├── karabiner/
   │   │   └── config_generator.py  # Karabiner integration
   │   └── utils/
   │       ├── config.py            # Configuration management
   │       └── permissions.py       # Accessibility checks
   └── examples/
       └── starter_chords.txt       # Sample batch file
   ```

## Core Features

### ✨ NEW: Enhanced User Experience
- **Interactive Mode**: Guided chord addition with prompts and previews
- **Undo Functionality**: Instantly undo mistakes (`fc undo`)
- **Chord Suggestions**: Get ideas for common chords (`fc suggest`)
- **Batch Addition**: Import multiple chords from files
- **Better Validation**: Conflict detection before you type everything
- **Visual Statistics**: Beautiful charts showing chord distributions

### Chord Management
- **Add**: Interactive, quick, or batch modes with confirmation
- **Remove**: Delete chords by input keys or output text
- **Search**: Find chords by input or output
- **List**: View all chords with sorting options
- **Undo**: Remove last N chord additions
- **Stats**: Comprehensive analytics with visual breakdowns

### Impulse Chording
- **Create on-the-fly**: Press keys together, then define output
- **Profile Pausing**: Auto-disables chords during impulse mode (no interference!)
- **Multiple Triggers**: Keyboard shortcuts at different speeds
- **Dynamic Sensitivity**: Automatic timing based on chord length

### Smart Features
- **Conflict Detection**: Prevents duplicate and overlapping chords
- **Chord Ordering**: Longer chords processed first (prevents short-chord issues)
- **Category Support**: Organize chords into groups
- **Dynamic Sensitivity**: 2-key (50ms), 3-key (75ms), 4-key (100ms), 5+ key (125ms)
- **Export/Import**: Modular JSON files for version control

## Why FreeChorder?

- **Free and Open Source**: No hardware purchase required
- **Customizable**: Full control over your chord library
- **Portable**: Your chords work on any Mac with Karabiner-Elements
- **Extensible**: Easy to add new features and integrations
- **Community-Driven**: Share and import chord libraries

## Development Status

✅ **Fully Functional!** FreeChorder is now complete and ready to use.

### Recent Enhancements (Latest Updates)
- ✅ **Interactive Chord Addition** - Guided workflow with previews
- ✅ **Undo Functionality** - Fix mistakes instantly
- ✅ **Chord Suggestions** - Get started faster
- ✅ **Batch Import** - Add multiple chords at once
- ✅ **Enhanced Statistics** - Visual breakdowns and analytics
- ✅ **Profile Pausing** - Impulse mode now pauses existing chords
- ✅ **Chord Ordering Fix** - Longer chords process before shorter ones
- ✅ **Better UX** - Confirmation prompts, error messages, and tips

### Available Commands
```bash
fc add          # Interactive chord addition
fc undo         # Undo last addition
fc suggest      # Get chord ideas
fc stats        # View analytics
fc impulse      # Create chords on-the-fly
fc list         # View all chords
fc search       # Find chords
fc remove       # Delete chords
fc config       # Configure settings
fc groups       # Manage chord groups
fc export       # Export configurations
fc activate     # Enable FreeChorder profile
fc refresh      # Update all chords
fc sync         # Sync quick chords
fc permissions  # Check permissions
```

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

## Get Started

Ready to supercharge your typing with chord-based input? 

### For Users:
```bash
fc suggest    # Get ideas
fc add        # Add your first chord
fc activate   # Enable FreeChorder
```

### For Developers:
Start with [RESEARCH_AND_IMPROVEMENTS_SUMMARY.md](RESEARCH_AND_IMPROVEMENTS_SUMMARY.md) for complete implementation details

Let's make typing faster and more efficient for everyone! 🚀

---

**Latest Updates:**
- ✅ Interactive chord addition with previews
- ✅ Undo functionality (`fc undo`)
- ✅ Chord suggestions (`fc suggest`)  
- ✅ Enhanced statistics with visual charts
- ✅ Profile pausing during impulse mode
- ✅ Chord ordering fix (longer chords first)
- ✅ Batch import from files
- ✅ Better UX throughout
