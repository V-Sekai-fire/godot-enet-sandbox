# Godot ENet Python Bridge - API Reference

## Overview

This document describes the **ENet Python Bridge API** - a Python implementation that emulates Godot's `ENetMultiplayerPeer` protocol for seamless RPC communication between Godot and Python AI/RL servers.

## Architecture

The bridge uses **raw UDP ENet protocol** to communicate with Godot's native `ENetMultiplayerPeer`:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Godot Client  │──────│  Python ENet    │──────│  AI/RL Server   │
│  (ENetPeer)     │      │  Bridge         │      │  (Python)       │
└─────────────────┘      └─────────────────┘      └─────────────────┘
     ENetMultiplayerPeer          Raw ENet          JSON-RPC / API
```

### Key Features

- **Native ENet Protocol**: Uses Godot's actual ENet packet format (not a custom protocol)
- **UDP Transport**: Low-latency UDP networking
- **RPC Integration**: Automatic `@rpc` function routing
- **Multiplayer Support**: Multiple Godot clients can connect simultaneously
- **JSON Payloads**: Easy-to-use JSON message format

## Packet Format

### Godot ENet Header

Godot wraps ENet packets with a custom header:

```c
// Packet structure (6-byte header + variable payload)
struct GodotENetPacket {
    uint32_t peer_id;      // 4 bytes, little-endian (Godot peer ID)
    uint8_t  channel;      // 1 byte - channel ID (0-255)
    uint8_t  flags;        // 1 byte - packet flags
    uint8_t  payload[];    // Variable length (up to 65535 - 6 bytes)
};
```

### Header Fields

| Field | Size | Description |
|-------|------|-------------|
| `peer_id` | 4 bytes | Godot-assigned peer ID (uint32, little-endian) |
| `channel` | 1 byte | Channel number (0-255) |
| `flags` | 1 byte | Packet reliability flags |
| `payload` | variable | JSON payload data |

### Flags Byte

```c
// Channel bits (0-2)
#define CHANNEL_MASK      0x07

// Reliability flags
#define FLAG_RELIABLE     0x01  // Bit 0 - reliable delivery
#define FLAG_UNSEQUENCED  0x02  // Bit 1 - no ordering guarantees
#define FLAG_UNRELIABLE   0x00  // No bits set - unreliable

// Ordering flags
#define FLAG_HAS_ORDERING 0x04  // Bit 2 - ordered channel
```

### Packet Types

| Type | Value | Description |
|------|-------|-------------|
| `RELIABLE` | 0 | Reliable, ordered delivery |
| `UNRELIABLE` | 1 | Unreliable delivery |
| `UNRELIABLE_ORDERED` | 2 | Ordered but unreliable |
| `RELIABLE_ORDERED` | 3 | Reliable and ordered |

## System Channels

Godot reserves the first 2 channels for system use:

| Channel | Purpose |
|---------|---------|
| 0 | RPC sync (reliable) |
| 1 | RPC (reliable) |
| 2+ | User-defined |

## API Reference

### Python ENet Bridge Server

The Python bridge runs an ENet UDP server that listens for Godot connections.

#### Starting the Server

```bash
# Basic usage (port 4000)
python -m python_godot_enet.enet_server

# Custom port
python -m python_godot_enet.enet_server --port 4001

# With DTLS encryption (requires pyenet-dlts)
python -m python_godot_enet.enet_server --dtls --cert cert.pem --key key.pem
```

#### Server Options

| Option | Description |
|--------|-------------|
| `--host HOST` | Bind host (default: 127.0.0.1) |
| `--port PORT` | Bind port (default: 4000) |
| `--dtls` | Enable DTLS encryption |
| `--cert FILE` | Certificate file for DTLS |
| `--key FILE` | Private key file for DTLS |
| `--ca FILE` | CA certificate for client verification |
| `--verbose` | Enable verbose logging |

### RPC Methods

#### Godot → Python (Client to Server)

These methods are called from Godot using `@rpc` decorators:

| Method | Direction | Description |
|--------|-----------|-------------|
| `create_npc(id, pos, personality)` | Godot→Py | Spawn a new NPC |
| `destroy_npc(id)` | Godot→Py | Destroy an NPC |
| `set_npc_position(id, pos)` | Godot→Py | Update NPC position |
| `set_npc_animation(id, anim)` | Godot→Py | Play NPC animation |
| `set_npc_mood(id, mood)` | Godot→Py | Update NPC mood/emotion |
| `player_action(action, params)` | Godot→Py | Player performed an action |
| `heartbeat()` | Godot↔Py | Connection health check |

#### Python → Godot (Server to Clients)

These methods are called from Python to update Godot clients:

| Method | Direction | Description |
|--------|-----------|-------------|
| `sync_npc_state(state)` | Py→Godot | Broadcast NPC state update |
| `broadcast(event, data)` | Py→Godot | Send event to all connected clients |

### Message Types

#### NPC Command

```json
{
  "type": "npc_command",
  "npc_id": "npc_001",
  "action": "create",
  "params": {
    "position": {"x": 0.0, "y": 0.0, "z": 0.0},
    "personality": "kind",
    "traits": {"shy": 0.3, "energetic": 0.7}
  }
}
```

#### Player Action

```json
{
  "type": "player_action",
  "player_id": 1,
  "action": "interact",
  "params": {
    "target": "npc_001",
    "item": "gift",
    "value": 10
  }
}
```

#### NPC State Sync

```json
{
  "type": "npc_state_sync",
  "npc_id": "npc_001",
  "state": {
    "position": {"x": 1.5, "y": 0.0, "z": 2.3},
    "animation": "wave",
    "mood": "happy",
    "facing": {"x": 1.0, "z": 0.0}
  }
}
```

#### RPC Response

```json
{
  "result": {"status": "created", "npc_id": "npc_001"},
  "id": 123
}
```

## Godot Integration

### Python Bridge GDScript

```gdscript
# python_bridge.gd - Connects to Python ENet server

var enet_peer: ENetMultiplayerPeer

func _ready():
    enet_peer = ENetMultiplayerPeer.new()
    
    var err = enet_peer.create_client(
        "127.0.0.1",  # Python bridge host
        4000,          # Python bridge port
        1,             # channel_count
        1024000,       # in_bandwidth
        1024000        # out_bandwidth
    )
    
    if err != OK:
        push_error("Failed to create ENet client")
        return
    
    multiplayer.multiplayer_peer = enet_peer

# Receive NPC state from Python
@rpc("any_peer", sync=true)
func sync_npc_state(state: Dictionary):
    var npc_id = state.get("npc_id", "unknown")
    print("NPC update: %s" % npc_id)

# Send command to Python
func send_npc_command(npc_id: String, action: String, params: Dictionary = {}):
    var cmd = {
        "type": "npc_command",
        "npc_id": npc_id,
        "action": action,
        "params": params
    }
    remote_sync(cmd)
```

### RPC Decorator Options

```gdscript
# Reliable sync (channel 1)
@rpc("any_peer", sync=true)

# Unreliable (channel 0 - for frequent updates)
@rpc("any_peer", sync=false, unreliable=true)

# Ordered delivery
@rpc("any_peer", sync=false, ordered=true)
```

## Python Integration

### AIBridge Base Class

```python
from python_godot_enet import AIBridge

class MyAIBridge(AIBridge):
    async def call_ai(self, method: str, **kwargs):
        # Integrate with your AI/RL server
        if method == "npc_command":
            return await self.handle_npc_command(**kwargs)
        elif method == "player_action":
            return await self.handle_player_action(**kwargs)
        
    async def handle_npc_command(self, npc_id: str, action: str, params: dict):
        # Your AI logic here
        return {"status": "handled", "npc_id": npc_id}
```

### Local AI Bridge

```python
from python_godot_enet import LocalAIBridge

class LocalAIBackend:
    async def create_npc(self, npc_id: str, position: dict, personality: str):
        # Your AI implementation
        return {"status": "created"}

bridge = LocalAIBridge(LocalAIBackend())
server.set_ai_server(bridge)
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "message": "Error description",
    "code": -32000
  },
  "id": 123
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| -32000 | Internal error |
| -32601 | Method not found |
| -32602 | Invalid params |

## Performance

| Metric | Value |
|--------|-------|
| Latency (loopback) | ~0.5-2ms |
| Throughput | ~5000 msg/s |
| Recommended max peers | 32 |
| Max packet size | 65535 bytes |

## Testing

### Manual Test with netcat

```bash
# Send a test packet to the bridge
# Format: [peer_id:4][channel:1][flags:1][payload]
echo -n -e '\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00{"type":"heartbeat"}' | nc -u -w1 127.0.0.1 4000
```

Packet breakdown:
- `\x01\x00\x00\x00` = peer_id = 1
- `\x00` = channel = 0
- `\x00` = flags = 0 (unreliable)
- `{"type":"heartbeat"}` = JSON payload

### Python Test Client

```python
import socket
import struct
import json

def send_test_packet(host="127.0.0.1", port=4000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Build packet: peer_id=1, channel=0, flags=0, payload={"type":"heartbeat"}
    peer_id = 1
    channel = 0
    flags = 0
    payload = json.dumps({"type": "heartbeat"}).encode('utf-8')
    
    header = struct.pack("<IBB", peer_id, channel, flags)
    packet = header + payload
    
    sock.sendto(packet, (host, port))
    print(f"Sent {len(packet)} bytes to {host}:{port}")
    
    sock.close()
```

## Security

### DTLS Encryption

For encrypted connections, use `pyenet-dlts`:

```python
from python_godot_enet import ENetServer, DTLSConfig

config = DTLSConfig(
    certfile="server.crt",
    keyfile="server.key",
    verify_client=False
)

server = ENetServer(port=4000)
# Configure DTLS via pyenet-dlts
```

### Firewall Configuration

| Port | Protocol | Purpose |
|------|----------|---------|
| 4000 | UDP | ENet traffic |
| 4000 | TCP | Control (optional) |

## Troubleshooting

### Connection Issues

1. **Check server is running**: `netstat -anu | grep 4000`
2. **Verify firewall**: UDP port 4000 must be open
3. **Check host/port**: Godot and Python must agree on port
4. **Enable verbose logging**: `--verbose` flag on server

### Packet Format Errors

1. **Byte order**: Use little-endian (`<I` format in struct)
2. **Header size**: Must be exactly 6 bytes
3. **Payload**: Must be valid JSON (unless using raw binary)

### Performance Problems

1. **Reduce message rate**: Batch updates where possible
2. **Use unreliable channel**: For frequent position updates
3. **Increase bandwidth**: Adjust `in_bandwidth`/`out_bandwidth`

## References

- [Godot ENet Module Source](https://github.com/godotengine/godot/blob/master/modules/enet/)
- [ENet Protocol Documentation](http://enet.bespin.org/)
- [pyenet-dlts](https://github.com/duachien/pyenet-dlts) - Python ENet with DTLS
- [Godot Multiplayer API](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
