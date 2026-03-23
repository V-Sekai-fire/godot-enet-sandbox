# Testing Strategy

**Project:** Godot ENet Sandbox  
**Last Updated:** March 2026

---

## Table of Contents

1. [Test Levels](#test-levels)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [RISC-V Emulator Tests](#risc-v-emulator-tests)
5. [Performance Tests](#performance-tests)
6. [Test Reporting](#test-reporting)

---

## Test Levels

| Level | Scope | Tools | Location |
|-------|-------|-------|----------|
| Unit | Individual functions | pytest | `python-bridge/tests/` |
| Integration | Component interactions | pytest + Godot | `godot-sandbox/tests/` |
| System | Full system | Integration tests | `tests/` |
| Performance | Benchmarks | Custom | `benchmarks/` |

---

## Unit Tests

### Python Bridge Tests

```bash
# Run all tests
cd python-bridge
pytest tests/

# Run with coverage
pytest tests/ --cov=godot_enet_bridge --cov-report=html

# Run specific test
pytest tests/test_client.py
```

### RISC-V Emulator Tests

```bash
cd riscv-toolchain/libriscv/build
ctest --output-on-failure

# Run specific test
ctest -R riscv_tests -V
```

---

## Integration Tests

### Godot + Python Bridge Tests

Integration tests verify the full round-trip:
1. Python client connects to Godot server
2. RPC calls are properly routed
3. Memory and state sync correctly
4. Exception handling works

```bash
# Start Godot scene
# Run Python integration tests
cd python-bridge
tests/integration/run.sh
```

### Test Categories

| Category | Description |
|----------|-------------|
| `rpc` | JSON-RPC message handling |
| `memory` | Memory read/write operations |
| `execution` | VM execution steps |
| `network` | ENet connectivity |
| `protocol` | DTLS encryption |

---

## RISC-V Emulator Tests

### Test Suite Structure

```
riscv-toolchain/libriscv/tests/
├── Catch2/               # Test framework
├── src/                  # Test sources
└── CMakeLists.txt        # Test configuration
```

### Running Tests

```bash
# From build directory
cd riscv-toolchain/libriscv/build

# List available tests
ctest -N

# Run all tests
ctest

# Run specific test
ctest -R riscv_emulator
```

### Test Examples

- `test_load_elf` - ELF loading and parsing
- `test_rv64i_instructions` - Instruction execution
- `test_memory_protection` - Memory isolation
- `test_exception_handling` - Exception triggers
- `test_step_determinism` - Deterministic execution

---

## Performance Tests

### Benchmark Suite

```bash
cd python-bridge/benchmarks
python benchmark_rpc.py
python benchmark_memory.py
python benchmark_execution.py
```

### Key Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| RPC latency | < 5ms | Round-trip time |
| Step rate | > 1000/s | Steps per second |
| Memory usage | < 10MB | Per VM |
| Bandwidth | < 1 Mbps | For typical workload |

### BMP 8-Soldier Benchmark

The `bmp-benchmark` test measures performance with 8 soldiers in a combat scenario:

```
$ python tests/bmp_benchmark.py
========================================
BMP 8-Soldier Benchmark
========================================
Bandwidth:     0.233 Mbps
Latency:       ~1ms per step
Step Rate:     ~1000 steps/sec
Memory:        ~10MB per VM
C³ Error:      < 5mm at 100m
========================================
```

---

## Test Reporting

### JUnit Reports

Tests can output JUnit XML for CI integration:

```bash
pytest tests/ --junitxml=test-results/python.xml
ctest --output-junit riscv-results.xml
```

### Coverage Reports

```bash
# Python coverage
cd python-bridge
pytest --cov=godot_enet_bridge --cov-report=xml

# C++ coverage (requires gcov)
cd riscv-toolchain/libriscv/build
cmake .. -DCMAKE_CXX_FLAGS="--coverage"
make
ctest
lcov --capture --directory . --output-file coverage.info
```

### GitHub Actions Integration

Test results are automatically uploaded in CI:
- Python test results to Codecov
- C++ coverage to Coveralls
- Performance benchmarks to GitHub Pages

---

## Test Environment Setup

### Local Development

```bash
# Install test dependencies
cd python-bridge
pip install pytest pytest-cov

# Run full test suite
./scripts/test_all.sh
```

### CI Environment

GitHub Actions workflows automatically:
1. Check out code
2. Set up Python and Godot
3. Run unit tests
4. Run integration tests (if Godot available)
5. Upload coverage reports
6. Publish benchmarks

---

## Known Test Issues

| Issue | Workaround | Status |
|-------|------------|--------|
| Godot headless mode | Use Xvfb on Linux | Open |
| macOS CI runners | Use GitHub-hosted | Open |
| Windows builds | Cross-compile from Ubuntu | Open |

---

## Contributing Tests

When adding new functionality:

1. Add unit tests for new Python code
2. Add C++ tests for new RISC-V features
3. Update integration tests if API changes
4. Add performance benchmarks for new algorithms
5. Ensure tests pass before merging
