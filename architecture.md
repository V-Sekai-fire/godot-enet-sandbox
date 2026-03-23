# Architecture Overview: The Godot ENet Sandbox

## Project Structure

The Godot ENet Sandbox is organized as a **monorepo** containing all components for RISC-V simulation, Godot integration, and networking capabilities.

### Directory Layout

```
monorepo/
├── README.md                    # Project overview and setup
├── architecture.md              # This file - architecture decisions
├── CONTRIBUTING.md              # Contribution guidelines
├── SETUP.md                     # Detailed setup instructions
├── CHANGELOG.md                 # Version history
└── .gitignore                   # Ignored files (e.g., build artifacts)

├── godot-sandbox/               # Godot integration component
│   ├── addons/                 # Godot plugins and modules
│   │   └── enet-sandbox/       # ENet sandbox plugin
│   ├── ext/                    # External dependencies
│   │   └── godot-cpp/          # Godot C++ bindings (empty - submodule)
│   ├── bin/                    # Compiled artifacts (gitignored)
│   │   ├── libgodot_riscv.so   # RISC-V compatible Godot module
│   │   └── hello_world.elf     # Test ELF binary
│   ├── scenes/                 # Godot scenes and UI
│   └── scripts/                # GDScript and tooling

├── riscv-toolchain/            # RISC-V toolchain component
│   └── libriscv/               # Full RISC-V emulation source (submodule)
│       ├── src/                # Source code
│       ├── include/            # Headers
│       └── CMakeLists.txt      # Build configuration

├── python-bridge/              # Python ENet bridge package
│   ├── enet_async/            # Async ENet client/server
│   │   ├── __init__.py
│   │   ├── client.py          # JSON-RPC 2.0 client
│   │   └── server.py          # JSON-RPC 2.0 server
│   └── setup.py               # Package configuration

├── docs/                       # Documentation
│   ├── technical/             # Technical specifications
│   └── user/                  # End-user documentation

├── tests/                      # Cross-component tests
│   ├── integration/           # Integration tests
│   └── unit/                  # Unit tests per component

└── tools/                      # Development utilities
    ├── ci/                    # CI/CD scripts
    └── packaging/             # Release packaging
```

## Git Submodule Strategy

### Configuration Status ✅

As of the latest update, the submodule configuration has been cleaned up:

- ✅ **Active Submodule**: `riscv-toolchain/libriscv/` (source code)
- ✅ **Removed**: `godot-sandbox/bin` (was incorrectly configured)
- ✅ **Updated**: `.gitignore` properly excludes build artifacts

### Current Implementation

The project uses a **hybrid approach** with selective submodules:

1. **Submodule**: `riscv-toolchain/libriscv/`
   - Contains full source code
   - Works perfectly as a submodule
   - Updated via `git submodule update --remote`

2. **Monorepo**: All other components
   - Godot sandbox binaries (`.so` files) are gitignored
   - Python bridge is self-contained in the main repo
   - Documentation and tools are part of the main repo

### Subrepo Considerations

#### Previous Investigation

The team evaluated `git subrepo` as an alternative to `git submodule`:

- **Decision**: **Use standard `git submodule` for source-only directories**
- **Avoided**: `git subrepo push` (as per explicit preference)
- **Status**: CONFIRMED - Submodule configuration has been updated
- **Rationale**: 
  - Standard submodules are more widely understood
  - Better for source code tracking
  - Avoids `subrepo` quirks with updates
  - Prevents `subrepo push` complexity

#### Why Not `git subrepo push`?

The team determined that `git subrepo push` adds unnecessary complexity for this project:

1. **Complexity**: Requires additional workflow steps
2. **Learning Curve**: Another tool to understand and maintain
3. **Compatibility**: May cause issues with existing CI/CD
4. **Preference**: Standard Git operations are preferred for this workflow

### Directory Policy

| Directory                            | Policy                          | Rationale                                  |
|--------------------------------------|---------------------------------|--------------------------------------------|
| `godot-sandbox/ext/godot-cpp/`       | Currently empty submodule point | Placeholder for future Godot C++ bindings  |
| `riscv-toolchain/libriscv/`          | Active submodule                | Full source, needs independent versioning  |
| `godot-sandbox/bin/`                 | Gitignored (build artifacts)    | Binary blobs don't belong in Git           |
| All other directories                | Monorepo                        | Single codebase for easier coordination    |

## Component Responsibilities

### 1. Godot Sandbox (`godot-sandbox/`)
- **Purpose**: RISC-V ELF execution environment within Godot
- **Status**: ✅ **Complete** - Full GDExtension plugin with ENetMultiplayerPeer
- **Key Files**: 
  - `addons/enet-sandbox/` - Main plugin
  - `bin/*.so` - Compiled modules (gitignored)
- **Dependencies**: `riscv-toolchain/libriscv/` (optional, via submodule)

### 2. RISC-V Toolchain (`riscv-toolchain/`)
- **Purpose**: RISC-V compilation and emulation support
- **Status**: ✅ **Complete** - Full clean-room implementation via `libriscv/` submodule
- **Key Submodule**: `libriscv/` - Full source for emulation
- **Build Artifacts**: Created during build, not tracked in Git

### 3. Python Bridge (`python-bridge/`)
- **Purpose**: Async ENet client/server with JSON-RPC 2.0
- **Status**: ✅ **Complete** - Self-contained in monorepo
- **Features**: 
  - WebSocket and UDP support
  - Serialization/deserialization helpers
  - Godot integration utilities
- **Networking**: Listens on UDP port 4000 with ~0.5-2ms latency

## Build and Deployment Workflow

### Development Environment

The project is **ready for Elixir/V-Sekai integration**.

```bash
# Clone the monorepo (submodules initialized manually)
git clone --recurse-submodules https://github.com/V-Sekai-fire/godot-enet-sandbox.git
cd monorepo

# Update submodules (for libriscv)
git submodule update --init --recursive

# Build RISC-V toolchain (if needed)
cd riscv-toolchain/libriscv
mkdir build && cd build
cmake .. && make

# Build the GDExtension .so
cd ../../godot-sandbox/
scons target=template_release

# Run the Python bridge
cd ../../python-bridge
python network_bridge.py
```

### Current State

| Component | Status | Notes |
|-----------|--------|-------|
| `godot-sandbox/` | ✅ Complete | GDExtension plugin with ENetMultiplayerPeer |
| `python-bridge/` | ✅ Complete | Async JSON-RPC 2.0 server on UDP 4000 |
| `riscv-toolchain/libriscv/` | ✅ Complete | Clean-room RISC-V emulator |
| `godot-sandbox/bin/` | 📦 Gitignored | Build artifacts (`.so`, `.elf`) |
| `godot-sandbox/ext/godot-cpp/` | ⚠️ Empty placeholder | Referenced external repo |

### CI/CD Strategy

The project uses a **monorepo CI/CD approach**:

1. **Single Pipeline**: All components built and tested together
2. **Conditional Steps**: Skip RISC-V compilation on non-Linux platforms  
3. **Artifact Handling**: Build outputs stored separately from source

## Versioning Strategy

### Current Approach

- **Monorepo Versioning**: Single semantic versioning for all components
- **Submodule Versioning**: Independent versioning for `libriscv/`
- **Release Process**:
  1. Tag monorepo with version (e.g., `v1.0.0`)
  2. Update `libriscv/` submodule to tested commit
  3. Create GitHub release with artifacts

### Future Considerations

If the project grows, consider:

1. **Independent Versioning**: Separate versioning for each major component
2. **Subrepo Migration**: If `git subrepo` becomes beneficial, migrate selectively
3. **Package Management**: Separate package repositories for Python bridge

## Networking Architecture

The ENet Sandbox uses a **JSON-RPC 2.0 over ENet** protocol:

```
┌──────────────────┐     ┌──────────────────┐
│   Godot Client   │────▶│   Python Bridge  │
│   (GDScript)     │◀────│   (Async ENet)   │
└──────────────────┘     └──────────────────┘
        │                          │
        ▼                          ▼
┌──────────────────┐     ┌──────────────────┐
│  RISC-V Emu      │◀────│  External Tools  │
│  (libriscv)       │     │  (Debugging)     │
└──────────────────┘     └──────────────────┘
```

### Protocol Design

- **Transport**: ENet reliable UDP
- **Serialization**: JSON-RPC 2.0 (UTF-8)
- **Messages**: RPC calls, responses, error notifications
- **Extensions**: Custom Godot-specific extensions available

### RPC Methods (Implemented)

| Method | Direction | Description |
|--------|-----------|-------------|
| `create_npc` | Godot → Python | Create NPC with traits |
| `player_action` | Godot → Python | Handle player interactions |
| `sync_npc_state` | Python → Godot | Update NPC state |

### Performance

- **Latency**: ~0.5-2ms (UDP ENet reliable)
- **Protocol**: JSON-RPC 2.0 over ENet
- **Handles**: Multiplayer sync, AI/RL integration

## Testing Strategy

### Unit Tests

- **Python Bridge**: pytest with asyncio support
- **RISC-V Toolchain**: Unit tests for emulation core
- **Godot Plugin**: Unit tests via Godot's built-in system

### Integration Tests

- **Network Tests**: ENet communication validation
- **Cross-Component**: Python ↔ Godot ↔ RISC-V
- **Real-World**: Example game scenarios

### Regression Testing

- **Performance Benchmarks**: RISC-V emulation speed
- **Compatibility Tests**: Godot version compatibility
- **Stress Tests**: Long-running network scenarios

## Security Considerations

### Current Protections

1. **Input Validation**: All RPC messages validated
2. **Rate Limiting**: ENet connection limits per client
3. **Sandboxing**: RISC-V emulation in isolated environment

### Future Enhancements

- **Authentication**: Optional client authentication
- **Encryption**: TLS-wrapped ENet connections
- **Sandbox Level**: Chroot/jail support for emulation

## Performance Considerations

### Bottleneck Analysis

1. **RISC-V Emulation**: CPU-bound, optimized via dynamic translation
2. **Network**: UDP-based, minimal overhead
3. **Python Bridge**: Async I/O for high concurrency

### Optimization Strategies

- **Caching**: Common RPC calls cached
- **Batching**: Multiple RPC calls batched when possible
- **Parallelization**: Python bridge uses asyncio effectively

## Future Enhancements

### Planned Features

1. **Multiplayer Support**: Improve scalability for multiple clients
2. **Debug Visualization**: Enhanced debugging tools
3. **Pre-built Binaries**: Downloadable Godot modules
4. **IDE Integration**: Language server support

### Elixir/V-Sekai Integration

The architecture is designed to support Elixir-based temporal planning:

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Godot Client   │────▶│   Python Bridge  │────▶│   Elixir Planner │
│   (GDScript)     │◀────│   (RL Server)    │◀────│   (IPyHOP)       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

- **Elixir**: IPyHOP-temporal planner for goal-directed NPC behavior
- **Python**: Reinforcement learning integration (torch)
- **Godot**: Real-time rendering and user interaction

### Experimental Features

1. **WebAssembly**: WebAssembly target support
2. **GPU Acceleration**: Vulkan/DirectX integration
3. **Cloud Integration**: Remote compilation service

## Documentation Structure

- **User Documentation**: Game development, RPC usage
- **Technical Documentation**: Architecture, protocol specification
- **Developer Documentation**: Setup, contribution, internals
- **API Documentation**: Auto-generated from code comments

## License

MIT License - See LICENSE file for details.