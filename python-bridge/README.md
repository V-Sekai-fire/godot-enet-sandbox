# Godot ENet Sandbox - Python Bridge

A Python networking bridge for communicating with Godot ENet Sandbox instances.

## Overview

This package provides a Python interface for the Godot ENet Sandbox, enabling:

- UDP communication via ENet protocol
- JSON-RPC 2.0 message handling
- Sandbox program control and monitoring
- Multi-client server support

## Installation

```bash
pip install godot-enet-bridge
```

Or install from source:

```bash
cd python-bridge
pip install -e .
```

## Quick Start

### Server Mode

```python
from godot_enet_bridge import SandboxServer

server = SandboxServer(port=4000)
server.start()

# Handle incoming connections
for client in server.accept_clients():
    print(f"Client connected: {client}")
    # Handle RPC calls, state sync, etc.
```

### Client Mode

```python
from godot_enet_bridge import SandboxClient

client = SandboxClient(host="localhost", port=4000)
client.connect()

# Call remote functions
result = client.call("add_coins", args=[10])
print(f"Coins: {result}")

# Send custom JSON-RPC
response = client.rpc({"method": "get_state", "params": {}})
```

## Protocol

The bridge uses JSON-RPC 2.0 over ENet UDP:

### Message Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "function_name",
  "params": {"arg1": "value1", "arg2": "value2"}
}
```

### Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {"data": "response_value"}
}
```

## API Reference

See the [API Documentation](docs/api.md) for complete details on:
- `SandboxClient` - Connect and call remote methods
- `SandboxServer` - Host a sandbox instance
- JSON-RPC methods - `execute_step`, `load_binary`, `read_memory`, etc.
- Data types and message formats

## Examples

See [docs/examples/](docs/examples/) for sample code and usage patterns.

## License

MIT License - see [LICENSE](LICENSE) for details.
