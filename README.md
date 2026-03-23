# The Godot ENet Sandbox - Monorepo

A complete Godot 4.7 ENet sandbox with RISC-V integration, Python bridge, and JSON-RPC protocol.

## Structure

```
monorepo/
├── godot-sandbox/           # Godot 4.7 project (source + binaries)
│   ├── bin/                 # Build artifacts (libgodot_riscv.so, hello_world.elf)
│   ├── ext/godot-cpp/       # godot-cpp interface (referenced, not vendored)
│   └── project.godot        # Godot project file
├── python-bridge/           # Python ENet bridge (async JSON-RPC 2.0 client/server)
├── riscv-toolchain/         # RISC-V toolchain
│   └── libriscv/            # libriscv source (clean-room implementation)
├── docs/                    # Documentation
│   └── protocol.md          # JSON-RPC API specification
└── .github/workflows/       # CI/CD workflows
```

## Components

| Directory | Purpose | Status |
|-----------|---------|--------|
| `godot-sandbox/` | Godot 4.7 ENet sandbox scene | ✅ Complete |
| `godot-sandbox/bin/` | Compiled `.so` + `.elf` binaries | 📦 Gitignored |
| `godot-sandbox/ext/godot-cpp/` | godot-cpp GDExtension interface | ⚠️ Referenced external |
| `python-bridge/` | Python async ENet bridge | ✅ Complete |
| `riscv-toolchain/libriscv/` | RISC-V emulator (clean-room) | ✅ Complete |
| `docs/` | Documentation | ✅ Complete |
| `tests/` | Unit/integration tests | 📋 Pending |

## Quick Start

### Prerequisites
- Godot 4.7 (headless)
- Python 3.11+
- ENet library
- RISC-V toolchain

### Build

```bash
# Build the RISC-V hello_world.elf
cd riscv-toolchain/libriscv
mkdir -p build && cd build
cmake ..
make -j$(nproc)

# Build the GDExtension .so
cd ../../godot-sandbox/
scons target=template_release

# Run the Python bridge
cd ../../python-bridge
python network_bridge.py
```

### Run

1. Open `godot-sandbox/` in Godot 4.7
2. Run the scene (F5)
3. The Python bridge connects via ENet UDP on port 4000

## Quick Start

### Prerequisites
- Godot 4.7 (headless)
- Python 3.11+
- ENet library
- RISC-V toolchain

### Build

```bash
# Build the RISC-V hello_world.elf
cd riscv-toolchain/libriscv
mkdir -p build && cd build
cmake ..
make -j$(nproc)

# Build the GDExtension .so
cd ../../godot-sandbox/
scons target=template_release

# Run the Python bridge
cd ../../python-bridge
python network_bridge.py
```

### Run

1. Open `godot-sandbox/` in Godot 4.7
2. Run the scene (F5)
3. The Python bridge connects via ENet UDP on port 4000

## License

MIT License - see LICENSE file for details.

## Publishing to GitHub

```bash
# Initialize repo
git init
git add .
git commit -m "Initial monorepo: Godot ENet Sandbox"

# Add remote (replace with your repo)
git remote add origin https://github.com/V-Sekai-fire/godot-enet-sandbox.git

# Create remote repo on GitHub
gh repo create V-Sekai-fire/godot-enet-sandbox --public --push --source=. --description="Godot 4.7 ENet Sandbox with RISC-V integration and Python bridge"

# Push
git push -u origin master
```
