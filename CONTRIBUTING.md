# Contributing to The Godot ENet Sandbox

Thank you for your interest in contributing! This document outlines the process for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Make your changes** with tests
5. **Push to your fork** and submit a pull request

## Development Setup

### Prerequisites

- Godot 4.3+ (for testing the plugin)
- CMake 3.15+
- Python 3.8+ (for bridge development)
- RISC-V toolchain (optional, for cross-compilation)

### Setting Up the Godot Project

```bash
cd godot-sandbox
# Copy the plugin to a test project
cp -r addons/ ~/godot-test-project/addons/
```

### Building from Source

```bash
cd godot-sandbox
mkdir build && cd build
cmake ..
cmake --build .
```

## Code Style

### C++ Code

- **Tabs**: Use tabs for indentation (Godot convention)
- **Braces**: Opening braces on same line
- **Naming**: camelCase for variables, PascalCase for types

### Python Code

- **Formatter**: Use `black` with 100 line length
- **Type Hints**: Use Python type hints
- **Imports**: Standard library first, then third-party

### GDScript

Follow Godot's [GDScript style guide](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html).

## Testing

### Unit Tests

```bash
# Python bridge tests
cd python-bridge
pytest

# RISC-V toolchain tests (if built)
cd riscv-toolchain/libriscv/build
ctest .
```

### Integration Tests

```bash
# Full integration requires:
# 1. Built .so file in godot-sandbox/bin/
# 2. Running Python bridge
# 3. Godot scene running

# Run Python bridge tests with integration flag
cd python-bridge
echo "{"integrations": {"godot": true, "riscv": true}}" > test_config.json
pytest --integration
```

## Commit Message Format

Use imperative, present tense for commit messages:

```
Correct RPC timeout handling
Add binary translation support
Update API documentation
Update dependencies
```

## Pull Request Guidelines

1. **Title**: Clear, descriptive title
2. **Description**: Explain the changes and why
3. **Tests**: Include tests for new features
4. **Docs**: Update documentation if needed
5. **Changelog**: Add entry to CHANGELOG.md

## Code Review Process

All submissions go through code review. Please be patient and address feedback promptly.

## Reporting Issues

When reporting issues, please include:

- Godot version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Any relevant logs

## License

By contributing, you agree to license your contributions under the MIT License.
