# FreeChorder - Complete Project Plan

## Project Overview

FreeChorder is a macOS terminal application that brings CharaChorder-like chord functionality to any keyboard using Karabiner-Elements as the backend. The application manages chord configurations while Karabiner-Elements handles the actual key remapping and chord replacement.

### Core Objectives
- Create a terminal-based chord management system
- Enable users to define keyboard chords (simultaneous key combinations) that output text or commands
- Integrate seamlessly with Karabiner-Elements for key interception and replacement
- Implement impulse chording for on-the-fly chord creation
- Provide efficient chord search and management capabilities

### Key Features
1. **Chord Management**: Add, remove, edit, and list chords
2. **Bidirectional Search**: Search by chord input or output text
3. **Impulse Chording**: Create chords in real-time while typing
4. **Import/Export**: Support for CharaChorder CSV format and custom formats
5. **Conflict Detection**: Prevent chord conflicts and ambiguities
6. **Statistics**: Track chord usage and effectiveness
7. **Backup/Restore**: Configuration management and versioning

## Technical Architecture

### Technology Stack
- **Language**: Python 3.9+ (for rapid development and cross-platform compatibility)
- **CLI Framework**: Click or Typer for modern CLI development
- **Configuration**: YAML/JSON for chord storage, JSON for Karabiner integration
- **Key Monitoring**: pynput for impulse chording mode
- **Testing**: pytest for unit and integration tests
- **Packaging**: PyInstaller for standalone distribution

### System Components

#### 1. Core Application (`freechorder.py`)
Main entry point handling CLI commands and orchestrating components.

#### 2. Chord Manager (`chord_manager.py`)
- Handles CRUD operations for chords
- Validates chord definitions
- Detects conflicts and ambiguities
- Manages chord library

#### 3. Karabiner Integration (`karabiner_bridge.py`)
- Generates Karabiner-Elements complex modifications
- Updates karabiner.json configuration
- Handles configuration reload
- Validates Karabiner installation

#### 4. Impulse Chord Handler (`impulse_handler.py`)
- Monitors keyboard input in impulse mode
- Captures chord combinations
- Prompts for output definition
- Adds new chords dynamically

#### 5. Search Engine (`search_engine.py`)
- Implements fuzzy search for chords and outputs
- Indexes chords for fast lookup
- Supports regex and pattern matching

#### 6. Configuration Manager (`config_manager.py`)
- Handles application settings
- Manages chord storage format
- Implements backup/restore functionality

#### 7. Statistics Tracker (`stats_tracker.py`)
- Records chord usage frequency
- Calculates typing speed improvements
- Generates usage reports

## Data Structures

### Chord Definition
```yaml
chord:
  id: "unique_id"
  input: 
    keys: ["a", "s", "d"]  # Keys pressed simultaneously
    modifier_keys: []       # Optional: ["cmd", "shift", "ctrl", "opt"]
  output:
    type: "text"           # or "command", "macro"
    value: "and"           # Text to output or command to execute
  metadata:
    created_at: "2025-09-27T10:00:00Z"
    usage_count: 42
    category: "common_words"
    notes: "User-defined notes"
```

### Karabiner Complex Modification Format
```json
{
  "description": "FreeChorder: a+s+d → and",
  "manipulators": [
    {
      "type": "basic",
      "from": {
        "simultaneous": [
          {"key_code": "a"},
          {"key_code": "s"},
          {"key_code": "d"}
        ],
        "simultaneous_options": {
          "key_down_order": "insensitive",
          "key_up_order": "insensitive",
          "key_up_when": "any"
        }
      },
      "to": [
        {
          "type": "string",
          "string": "and"
        }
      ]
    }
  ]
}
```

## Command Line Interface

### Basic Commands

```bash
# Add a chord
freechorder add "asd" "and"
freechorder add "qwe" "the" --category common_words

# Remove a chord
freechorder remove "asd"
freechorder remove --output "and"  # Remove by output

# Search chords
freechorder search "and"           # Search in both input and output
freechorder search --input "asd"   # Search only in inputs
freechorder search --output "the"  # Search only in outputs

# List chords
freechorder list                   # List all chords
freechorder list --category common_words
freechorder list --sort usage      # Sort by usage count

# Edit chord
freechorder edit "asd" --output "AND"
freechorder edit "asd" --category articles

# Statistics
freechorder stats                  # Show overall statistics
freechorder stats --chord "asd"    # Stats for specific chord
```

### Advanced Commands

```bash
# Impulse chording mode
freechorder impulse               # Enter impulse mode
# Press ESC to exit, or define trigger key

# Import/Export
freechorder import chords.csv     # Import CharaChorder format
freechorder export my_chords.yaml # Export in FreeChorder format
freechorder export --format charachorder chords.csv

# Configuration
freechorder config --set impulse_trigger "cmd+i"
freechorder config --set chord_timeout 50ms
freechorder config --list

# Backup/Restore
freechorder backup                # Create timestamped backup
freechorder restore 2025-09-27    # Restore from date
freechorder restore --list        # List available backups

# Karabiner management
freechorder karabiner status      # Check Karabiner connection
freechorder karabiner reload      # Force reload configuration
freechorder karabiner validate    # Validate generated config
```

## Implementation Details

### Phase 1: Core Foundation (Week 1-2)

1. **Project Setup**
   - Initialize Python project with poetry/pip
   - Set up directory structure
   - Configure development environment
   - Set up Git repository

2. **Basic CLI Structure**
   - Implement command routing with Click/Typer
   - Create help system and documentation
   - Set up configuration file handling
   - Implement basic error handling

3. **Chord Data Model**
   - Design chord storage format
   - Implement CRUD operations
   - Create validation functions
   - Set up persistence layer

### Phase 2: Karabiner Integration (Week 3-4)

1. **Karabiner Configuration**
   - Study Karabiner-Elements JSON schema
   - Implement configuration generator
   - Create configuration updater
   - Handle configuration backup

2. **Complex Modifications**
   - Generate simultaneous key mappings
   - Handle modifier keys properly
   - Implement string output formatting
   - Test with various key combinations

3. **Configuration Management**
   - Locate karabiner.json file
   - Implement safe file updates
   - Add configuration validation
   - Handle Karabiner reload

### Phase 3: Advanced Features (Week 5-6)

1. **Impulse Chording**
   - Implement keyboard monitoring
   - Create chord detection algorithm
   - Build interactive prompt system
   - Add chord validation and conflict detection

2. **Search and Filter**
   - Implement fuzzy search algorithm
   - Add regex support
   - Create efficient indexing
   - Support complex queries

3. **Import/Export**
   - Parse CharaChorder CSV format
   - Implement format converters
   - Add validation and error handling
   - Support batch operations

### Phase 4: Polish and Optimization (Week 7-8)

1. **Performance Optimization**
   - Profile application performance
   - Optimize search algorithms
   - Improve startup time
   - Reduce memory footprint

2. **User Experience**
   - Add progress indicators
   - Improve error messages
   - Implement command suggestions
   - Add interactive tutorials

3. **Testing and Documentation**
   - Write comprehensive unit tests
   - Create integration tests
   - Document all features
   - Create video tutorials

## CharaChorder Compatibility

### Understanding CharaChorder Format
Based on the Device Manager, CharaChorder uses:
- CSV format for chord libraries
- Chord notation: "input1+input2+input3,output"
- Support for special characters and modifiers
- Categories and tags for organization

### Import Compatibility
- Parse CharaChorder CSV exports
- Convert chord notations
- Map special keys appropriately
- Preserve categories and metadata

## Impulse Chording Implementation

### Workflow
1. User activates impulse mode (hotkey or command)
2. System monitors keyboard input
3. User presses chord combination
4. System detects simultaneous keys
5. Prompt appears for output definition
6. User types desired output
7. Chord is saved and immediately active

### Technical Considerations
- Use pynput for cross-platform key monitoring
- Implement debouncing for key detection
- Handle system permissions for key monitoring
- Provide visual/audio feedback

## Error Handling and Edge Cases

### Common Scenarios
1. **Conflicting Chords**: Detect when new chord conflicts with existing
2. **Ambiguous Inputs**: Handle chords that are subsets of others
3. **System Keys**: Prevent interference with system shortcuts
4. **Invalid Characters**: Handle special characters properly
5. **Performance Impact**: Monitor for system slowdown

### Error Messages
- Clear, actionable error messages
- Suggestions for conflict resolution
- Help references for common issues
- Debug mode for troubleshooting

## Security Considerations

1. **Input Validation**: Sanitize all user inputs
2. **File Permissions**: Respect system file permissions
3. **Privilege Escalation**: Avoid requiring admin rights
4. **Data Privacy**: Don't log sensitive information
5. **Update Security**: Implement secure update mechanism

## Performance Requirements

- Chord detection: < 50ms latency
- Search operations: < 100ms for 10,000 chords
- Configuration reload: < 500ms
- Memory usage: < 50MB baseline
- CPU usage: < 5% during monitoring

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock external dependencies
- Achieve 80%+ code coverage
- Test edge cases thoroughly

### Integration Tests
- Test Karabiner integration
- Verify configuration updates
- Test import/export functionality
- Validate chord detection

### User Acceptance Tests
- Test with real users
- Gather feedback on UX
- Measure typing improvements
- Validate feature completeness

## Distribution Plan

### Packaging Options
1. **Homebrew Formula**: Primary distribution method
2. **PyPI Package**: For Python users
3. **Standalone Binary**: Using PyInstaller
4. **Source Distribution**: GitHub releases

### Installation Process
```bash
# Homebrew (recommended)
brew tap freechorder/tap
brew install freechorder

# PyPI
pip install freechorder

# From source
git clone https://github.com/username/freechorder
cd freechorder
pip install -e .
```

## Future Enhancements

### Version 2.0 Features
1. **GUI Application**: Native macOS app with SwiftUI
2. **Cloud Sync**: Sync chords across devices
3. **Machine Learning**: Suggest chords based on typing patterns
4. **Multi-language**: Support for non-English languages
5. **Collaborative Libraries**: Share chord libraries with community

### Platform Expansion
1. **Linux Support**: Using alternative to Karabiner
2. **Windows Support**: Using AutoHotkey backend
3. **Mobile Companion**: iOS/Android apps for management

## Resources and References

### Documentation
- Karabiner-Elements Docs: https://karabiner-elements.pqrs.org/docs/
- CharaChorder Docs: https://docs.charachorder.com/
- CharaChorder Device Manager: https://github.com/CharaChorder/DeviceManager

### Key Configuration Files
- Karabiner config: `~/.config/karabiner/karabiner.json`
- FreeChorder config: `~/.config/freechorder/config.yaml`
- Chord library: `~/.config/freechorder/chords.yaml`

### Development Tools
- Python 3.9+: https://www.python.org/
- Click: https://click.palletsprojects.com/
- pynput: https://pynput.readthedocs.io/
- PyYAML: https://pyyaml.org/

## Success Metrics

1. **Functionality**: All CharaChorder features replicated
2. **Performance**: Meeting all performance requirements
3. **Usability**: Positive user feedback and adoption
4. **Reliability**: < 1% crash rate in production
5. **Community**: Active user base and contributors

## Timeline

- **Week 1-2**: Core foundation and basic CRUD
- **Week 3-4**: Karabiner integration complete
- **Week 5-6**: Advanced features implemented
- **Week 7-8**: Testing, polish, and documentation
- **Week 9**: Beta release and user testing
- **Week 10**: Production release

This plan provides a comprehensive roadmap for building FreeChorder. Each phase builds upon the previous one, ensuring a solid foundation while delivering incremental value. The modular architecture allows for easy extension and maintenance.