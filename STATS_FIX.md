# Stats Command Fix & Enhancement

## Problem Identified

The `fc stats` command was working but showing limited information:
- Only basic counts (total chords, total usage, categories)
- Usage count was always 0 (no tracking mechanism exists)
- No visual representation
- No breakdown by chord length or category
- No recently added chords

## Root Cause

The stats command relied heavily on `usage_count`, which is never incremented because:
1. Karabiner-Elements executes chords directly
2. There's no callback mechanism to FreeChorder when a chord is used
3. Usage tracking would require:
   - A background service monitoring clipboard/keystrokes
   - Or Karabiner shell command callbacks (adds latency)
   - Or manual logging (unreliable)

**Decision:** Instead of implementing complex usage tracking, make stats more useful with the data we DO have.

---

## Solution Implemented

### Enhanced Statistics Display

**New features:**
1. ✅ **Visual bars** - ASCII bar charts for distributions
2. ✅ **Chord length breakdown** - See 2-key vs 3-key vs 4-key chords
3. ✅ **Category distribution** - Visualize chord organization
4. ✅ **Recently added** - Last 5 chords with age
5. ✅ **Oldest/newest dates** - Timeline awareness
6. ✅ **Detailed view** - Full breakdown with `--detailed` flag
7. ✅ **Usage tip** - Explains why usage is 0

### Before (Old Stats):
```bash
$ fc stats

FreeChorder Statistics
==============================
Total chords: 23
Total usage: 0
Categories: 1

Most used chords:
  a+d+s → and (0x)
  e+h+t → the (0x)
```

### After (New Stats):
```bash
$ fc stats

============================================================
                  📊 FreeChorder Statistics                  
============================================================

📝 Overview:
   Total chords: 23
   Unique categories: 1
   Oldest chord: 2025-09-27
   Newest chord: 2025-10-01

🎹 Chord Length Distribution:
   2 keys:   5 chords ████ (21.7%)
   3 keys:  17 chords ██████████████ (73.9%)
   4 keys:   1 chords  (4.3%)

📂 Category Breakdown:
   impulse:  15 chords █████████████ (65.2%)
   Uncategorized:   8 chords ██████ (34.8%)

🆕 Recently Added (last 5):
   b+t+u → 'but' (today)
   d+o → 'do' (today)
   a+h+t → 'that' (3d ago)

💡 Tip: Usage tracking not yet implemented
   Future feature: Track which chords you use most

============================================================
💡 Use 'fc stats --detailed' for full breakdown
============================================================
```

---

## New Options

```bash
fc stats              # Standard statistics view
fc stats --detailed   # Full breakdown by category
fc stats -d           # Short form for detailed
```

---

## Technical Details

### Code Changes

**File:** `src/freechorder/cli/main.py`

1. **Added datetime import** for date calculations
2. **Enhanced stats calculation:**
   - Chord length distribution
   - Category counts
   - Oldest/newest chord tracking
   - Age calculation for recent chords

3. **Visual improvements:**
   - ASCII bar charts (`█` character)
   - Better formatting with emojis
   - Percentage displays
   - Centered headers

4. **Detailed mode:**
   - Shows all chords grouped by category
   - Sorted by chord length (longest first)
   - Limited to top 10 per category for readability

### Key Functions

```python
# Calculate distributions
chord_lengths = {}
categories_count = {}

for chord in all_chords:
    length = len([k for k in chord.input_keys 
                  if k not in ['cmd', 'shift', 'option', 'control']])
    chord_lengths[length] = chord_lengths.get(length, 0) + 1
    
    cat = chord.category or "Uncategorized"
    categories_count[cat] = categories_count.get(cat, 0) + 1
```

---

## What Statistics Show

### 1. Overview Section
- **Total chords:** Count of all chords
- **Unique categories:** Number of different categories
- **Oldest chord:** When you started using FreeChorder
- **Newest chord:** Most recent addition

### 2. Chord Length Distribution
- Shows how many 2-key, 3-key, 4-key chords you have
- Visual bar chart
- Percentage of total

**Why this matters:**
- 2-key chords: Fast but prone to accidental triggers
- 3-key chords: Sweet spot (most common)
- 4+ key chords: Complex but reliable

### 3. Category Breakdown
- Top 5 categories by chord count
- Visual distribution
- Helps organize your library

### 4. Recently Added
- Last 5 chords with age
- Quick check on recent activity
- Useful for reviewing new additions

### 5. Usage Tracking (Future)
- Currently shows a tip explaining it's not implemented
- Future: Could track via background service

---

## Usage Examples

### Check Overall Stats
```bash
$ fc stats
# Quick overview with distributions
```

### Deep Dive
```bash
$ fc stats --detailed
# See every chord organized by category
```

### Check After Batch Import
```bash
$ fc add --batch chords.txt
$ fc stats
# See how the distribution changed
```

---

## Use Cases

### 1. Library Health Check
See if you have good balance between chord lengths:
```bash
$ fc stats
# Look at "Chord Length Distribution"
# Ideally: mostly 3-key, some 2-key, few 4-key
```

### 2. Organization Review
Check if chords are properly categorized:
```bash
$ fc stats
# Look at "Category Breakdown"
# Too many "Uncategorized"? Time to organize!
```

### 3. Activity Tracking
See recent additions:
```bash
$ fc stats
# Look at "Recently Added"
# Spot any mistakes? Use fc undo
```

### 4. Before/After Comparison
Track changes after bulk operations:
```bash
$ fc stats > before.txt
$ fc add --batch new_chords.txt
$ fc stats > after.txt
$ diff before.txt after.txt
```

---

## Future Enhancements (Possible)

### Usage Tracking Options:

**Option 1: Background Service (Complex)**
- Monitor clipboard for chord outputs
- Cross-reference with chord database
- Pros: Automatic
- Cons: Resource intensive, privacy concerns

**Option 2: Karabiner Callbacks (Medium)**
- Add shell command to each chord rule
- Log to file when chord triggers
- Pros: Accurate
- Cons: Adds latency (~50ms per chord)

**Option 3: Manual Logging (Simple)**
- Add `fc log <chord>` command
- User manually logs important chords
- Pros: No overhead
- Cons: Relies on user discipline

**Option 4: Periodic Surveys (Hybrid)**
- Show random chord occasionally
- Ask "Did you use this?"
- Build usage profile over time
- Pros: Low overhead, no privacy issues
- Cons: Not real-time

**Recommendation:** Start with Option 3 (manual logging) if usage tracking is desired.

---

## Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| Visual appeal | Plain text | Emojis, bars, formatting |
| Information | 4 metrics | 10+ metrics |
| Breakdown | None | Length + Category |
| Recent activity | None | Last 5 chords |
| Timeline | None | Oldest/newest dates |
| Detailed view | None | `--detailed` flag |
| Usage info | Confusing zeros | Clear explanation |
| Actionability | Low | High (see distributions) |

---

## Tips for Users

### 1. Run Stats After Changes
```bash
fc add --batch chords.txt
fc stats  # See what you added
```

### 2. Check Length Distribution
If you see:
- Too many 2-key chords → May trigger accidentally
- Too many 4-key chords → Harder to remember
- Mostly 3-key chords → Good balance! ✅

### 3. Organize with Categories
```bash
fc stats  # See "Uncategorized" count
# If high, add categories to chords
fc add "abc" "text" --category "programming"
```

### 4. Review Recent Additions
```bash
fc stats | grep "Recently Added" -A 6
# Quick check without full output
```

---

## Summary

✅ **Fixed:** Stats command now shows useful information even without usage tracking
✅ **Enhanced:** Visual bars, distributions, recent activity
✅ **Added:** Detailed view with `--detailed` flag
✅ **Improved:** Better formatting and explanations
✅ **Future-ready:** Structure in place for usage tracking if implemented

**Bottom line:** The stats command is no longer just showing zeros - it's a powerful tool for understanding your chord library!

