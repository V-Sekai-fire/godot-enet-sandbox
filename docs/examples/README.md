# Documentation Examples

This directory contains example code, templates, and integration stubs for the Godot ENet Sandbox project. These examples demonstrate how to integrate the various components of your system:

- **Elixir** - IPyHOP temporal planner for NPC goals
- **Python** - RL training environment and inference server
- **Godot** - ENet networking and GDScript integration

## Structure

```
docs/examples/
├── elixir_npc_integration.exs    # Elixir NPC trait system and planner  
├── elixir_npc_integration.exs.md # Elixir examples documentation
├── python_rl_stubs.py            # Python RL environment and agent
├── godot_gdscript_networking.gd  # Godot ENet JSON-RPC client
├── integration_test.py           # Integration test suite
└── README.md                     # This file
```

## Usage

### Running Examples

```bash
# Run all unit tests
python integration_test.py --mode unit

# Run integration tests
python integration_test.py --mode integration

# Run specific test
python integration_test.py --mode unit --test test_npc_traits

# Run performance benchmarks
python integration_test.py --mode performance
```

### Testing

```bash
# Run the integration test suite
python docs/examples/integration_test.py --mode system

# Run with verbose output
python docs/examples/integration_test.py --mode unit --verbose
```

### Development Workflow

1. **Develop in Elixir**: Edit `elixir_npc_integration.exs` for NPC logic
2. **Test Python bridge**: Use `python_rl_stubs.py` to verify communication
3. **Integrate with Godot**: Update `godot_gdscript_networking.gd` for client
4. **Run integration tests**: Verify everything works together

## Components

### Elixir NPC Integration (`elixir_npc_integration.exs`)

Demonstrates:
- 5-trait NPC system (shy, energetic, kind, snooty, lazy)
- Friendship tracking (0-100 scale)
- Daydream-based memory consolidation
- IPyHOP temporal planner for goal-directed behavior
- JSON-RPC bridge to Python RL engine

### Python RL Stubs (`python_rl_stubs.py`)

Provides:
- `NPCState` dataclass for NPC state representation
- `RLAction` dataclass for action space
- `NPCRLEnvironment` - RL environment interface
- `NPCAgent` - Stub RL agent (replace with trained model)
- `RPCServer` - JSON-RPC server for Godot communication
- Training loop and metrics collection

### Godot Networking (`godot_gdscript_networking.gd`)

Implements:
- ENet client connection to Python server
- JSON-RPC 2.0 message handling
- RPC request/response pattern
- Server event handling and NPC action dispatch
- Heartbeat and connection management

## Testing Strategy

The examples include tests at multiple levels:

| Level | Description | Tests |
|-------|-------------|-------|
| Unit | Individual components | Trait system, planner, RL env |
| Integration | Component interactions | Bridge, RPC, state sync |
| System | Full workflows | NPC cycle, multi-NPC, memory |
| Performance | Benchmarks | Step rate, latency, batch |

## Related Documentation

- [API Reference](docs/api.md) - JSON-RPC methods and protocol
- [Architecture](docs/architecture.md) - System component breakdown
- [Build Guide](docs/build/README.md) - Setup and deployment
- [Testing Guide](docs/testing/README.md) - Testing strategy and CI

## License

These examples are provided as part of the Godot ENet Sandbox project for reference and integration purposes.
