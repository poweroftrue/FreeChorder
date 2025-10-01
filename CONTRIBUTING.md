# Contributing to FreeChorder

First off, thank you for considering contributing to FreeChorder! It's people like you that make FreeChorder such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** to demonstrate the steps
- **Describe the behavior you observed** and what you expected
- **Include your environment details**: macOS version, Python version, Karabiner-Elements version
- **Include relevant logs or error messages**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most FreeChorder users
- **List any alternatives you've considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if you've added code that should be tested
4. **Ensure the test suite passes**
5. **Update documentation** if needed
6. **Write a clear commit message**

## Development Setup

### Prerequisites

- macOS 10.15 or later
- Python 3.9 or later
- Karabiner-Elements installed
- Git

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/freechorder.git
cd freechorder

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=freechorder

# Run specific test file
pytest tests/test_chord_manager.py
```

### Code Style

We follow PEP 8 with some modifications:

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to all functions and classes

Format your code before committing:

```bash
# Format with black
black src/

# Check style with flake8
flake8 src/
```

## Project Structure

```
freechorder/
├── src/freechorder/
│   ├── cli/              # CLI interface and commands
│   ├── core/             # Core business logic
│   ├── karabiner/        # Karabiner-Elements integration
│   └── utils/            # Utility functions
├── tests/                # Test files
├── examples/             # Example chord files
└── docs/                 # Documentation
```

## Coding Guidelines

### Python Code

- Write clear, self-documenting code
- Use type hints where appropriate
- Follow the Single Responsibility Principle
- Keep functions small and focused
- Avoid global variables

Example:

```python
def add_chord(input_keys: str, output_text: str, category: str = None) -> bool:
    """
    Add a new chord to the library.
    
    Args:
        input_keys: Keys to press simultaneously (e.g., "asd")
        output_text: Text to output when chord is triggered
        category: Optional category for organization
        
    Returns:
        True if chord was added successfully, False otherwise
        
    Raises:
        ChordConflictError: If chord already exists
    """
    # Implementation
    pass
```

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:

```
Add dynamic chord sensitivity based on key count

- Implement variable timeout for different chord lengths
- Add configuration option for sensitivity adjustment
- Update all existing chords when config changes

Fixes #123
```

### Branch Naming

- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation updates
- `refactor/` for code refactoring

Examples:
- `feature/add-cloud-sync`
- `fix/chord-timeout-bug`
- `docs/update-installation-guide`

## Testing Guidelines

### What to Test

- All new features must have tests
- Bug fixes should include regression tests
- Aim for 80%+ code coverage

### Test Structure

```python
import pytest
from freechorder.core.chord_manager import ChordManager

class TestChordManager:
    """Tests for ChordManager class."""
    
    def test_add_chord_success(self):
        """Test adding a valid chord."""
        manager = ChordManager()
        result = manager.add_chord("asd", "and")
        assert result is True
        
    def test_add_chord_conflict(self):
        """Test adding a conflicting chord raises error."""
        manager = ChordManager()
        manager.add_chord("asd", "and")
        
        with pytest.raises(ChordConflictError):
            manager.add_chord("asd", "different")
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update QUICK_REFERENCE.md for new commands

## Community

- Join discussions in GitHub Issues
- Help answer questions from other users
- Share your chord libraries and workflows
- Suggest improvements and new features

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

## Questions?

Feel free to:
- Open an issue for questions
- Reach out to maintainers
- Check existing documentation

Thank you for contributing to FreeChorder! 🎹

