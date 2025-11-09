# Test Scripts Directory

This directory contains test scripts for the MyBella application.

## Usage

Place your testing scripts here. Example structure:

```
test/
├── __init__.py
├── test_auth.py          # Authentication tests
├── test_voice_calls.py   # Voice calling tests
├── test_chat.py          # Chat functionality tests
├── test_personas.py      # Persona management tests
└── integration_tests.py  # Full integration tests
```

## Test Categories

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Fast execution

### Integration Tests
- Test component interactions
- Database operations
- API endpoint testing

### End-to-End Tests
- Full user workflow testing
- Real-time communication testing
- Voice calling integration

## Running Tests

```bash
# Run all tests
python -m pytest backend/scripts/test/

# Run specific test file
python -m pytest backend/scripts/test/test_auth.py

# Run with coverage
python -m pytest --cov=backend backend/scripts/test/
```

## Test Framework

Recommended testing libraries:
- `pytest` - Main testing framework
- `pytest-flask` - Flask testing utilities
- `pytest-socketio` - Socket.IO testing
- `unittest.mock` - Mocking utilities