# FreeChorder Quick Reference Card

## 🚀 Getting Started (3 Steps)

```bash
# 1. Get suggestions for what to add
fc suggest

# 2. Add your first chord (interactive mode)
fc add

# 3. Test it! Press the keys together in any app
```

---

## 📝 Common Commands

### Adding Chords

```bash
fc add                           # Interactive mode (recommended for beginners)
fc add "asd" "and"               # Quick add with preview
fc add "xyz" "text" --no-confirm # Skip confirmation (fast)
fc add --batch chords.txt        # Bulk import from file
```

### Managing Chords

```bash
fc list                  # Show all chords
fc search "text"         # Find chords
fc remove "asd"          # Remove by input keys
fc undo                  # Undo last addition
fc undo 3                # Undo last 3 additions
```

### Discovery

```bash
fc suggest               # Get common chord ideas
fc stats                 # View usage statistics
```

### Configuration

```bash
fc config --show                 # View current settings
fc config --chord-timeout 150    # Adjust timing
fc refresh                       # Apply config to all chords
```

### Impulse Mode

```bash
fc impulse               # Create chords while typing
fc sync                  # Sync quick-added chords
```

**Keyboard shortcuts:**
- `Ctrl+Opt+Delete` - Regular impulse mode
- `Cmd+Opt+Delete` - Quick impulse mode (fast)
- `Shift+Opt+Delete` - Native dialog (instant)

---

## 📄 Batch File Format

Create a text file (e.g., `my_chords.txt`):

```
# Comments start with #
the,the
and,and
wit,with

# Programming
fun,function
ret,return
```

Then import:
```bash
fc add --batch my_chords.txt
```

---

## 🎯 Common Workflows

### First Time Setup
```bash
fc suggest                          # Get ideas
fc add --batch starter_chords.txt   # Add basics
fc activate                         # Enable in Karabiner
```

### Daily Usage
```bash
fc impulse                # Create chords as you type
# [Press multiple keys, enter output]
fc sync                   # Activate new chords
```

### Power User
```bash
fc add "abc" "text1" --no-confirm
fc add "xyz" "text2" --no-confirm
fc undo 2                 # Oops, fix mistakes
fc list                   # Review chords
```

---

## ⚡ Pro Tips

1. **Start with suggestions:** `fc suggest` shows proven chords
2. **Use interactive mode first:** Learn the system with `fc add`
3. **Batch for bulk:** Prepare a file, import with `--batch`
4. **Undo is your friend:** Made a mistake? `fc undo`
5. **Profile pausing:** Impulse mode auto-pauses Karabiner profile

---

## 🔧 Troubleshooting

### Chord already exists
```bash
fc add
# When prompted, choose to replace it
```

### Made a mistake
```bash
fc undo                  # Fix it instantly
```

### Chords not working
```bash
fc activate              # Activate FreeChorder profile
fc refresh               # Reload all chords
```

### Need accessibility permissions
```bash
fc permissions           # Check and fix permissions
```

---

## 📊 What Each Command Does

| Command | What It Does | When To Use |
|---------|-------------|-------------|
| `fc add` | Add chord (interactive) | Learning, careful setup |
| `fc add X Y` | Quick add with preview | Fast but safe |
| `fc add X Y --no-confirm` | Instant add | Bulk operations |
| `fc add --batch` | Import from file | Initial setup |
| `fc undo` | Remove last chord | Fix mistakes |
| `fc suggest` | Show ideas | Getting started |
| `fc impulse` | Live chord creation | On-the-fly workflow |
| `fc sync` | Activate quick chords | After fast imports |
| `fc list` | Show all chords | Review library |
| `fc search` | Find specific chords | Find what you need |
| `fc refresh` | Update all chords | After config changes |
| `fc activate` | Enable profile | First setup |

---

## 🎓 Learning Path

### Level 1: Beginner (15 minutes)
1. Run `fc suggest`
2. Try `fc add` (interactive)
3. Press the chord keys in any app
4. Practice with `fc undo` if needed

### Level 2: Comfortable (30 minutes)
1. Create `my_chords.txt` file
2. Add 10-20 common chords
3. Import with `fc add --batch`
4. Try `fc impulse` mode

### Level 3: Power User (1 hour)
1. Use `--no-confirm` for speed
2. Organize chords by category
3. Adjust timing with `fc config`
4. Build custom chord collections

---

## 💡 Example Sessions

### Session 1: First Chord
```bash
$ fc add

🎯 Add New Chord
Enter keys: the

📝 Preview: e+h+t (3 keys, 75ms)
Enter output: the

✨ Preview:
   Press: e+h+t → 'the' 
   Save? y

✅ Created! Now active everywhere!
```

### Session 2: Batch Import
```bash
$ cat > quick.txt
the,the
and,and
wit,with

$ fc add --batch quick.txt
📦 Batch Add: 3 chords
✅ Added: 3 chords
```

### Session 3: Impulse Mode
```bash
$ fc impulse
🔄 Pausing FreeChorder profile...
🎹 Impulse Mode Active!

[Press h+e+y together]
🎯 Detected: h+e+y
Output: hey
✅ Saved!

[Press ESC to exit]
🔄 Resuming profile...
```

---

## 🎯 Quick Decision Tree

**Want to add ONE chord?**
- New user? → `fc add` (interactive)
- Experienced? → `fc add "keys" "output"`
- Super fast? → `fc add "keys" "output" --no-confirm`

**Want to add MANY chords?**
- Create file → `fc add --batch file.txt`
- Or use → `fc impulse` (on-the-fly)

**Made a mistake?**
- One chord → `fc undo`
- Multiple → `fc undo N`

**Just starting?**
- Get ideas → `fc suggest`
- Learn → `fc add` (try interactive)

---

## 📱 Keep This Handy

Bookmark this page or print it out. The most common commands:

```bash
fc add           # Add interactively
fc suggest       # Get ideas  
fc undo          # Fix mistake
fc list          # See all
fc impulse       # Create on-the-fly
```

That's it! You're ready to chord. 🎉

