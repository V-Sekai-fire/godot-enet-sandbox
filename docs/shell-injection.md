# Shell Injection Pattern (Stage 1)

## Overview

Godot needs to receive LLM-generated plans without runtime Elixir/Python coordination. This document describes the **shell injection** pattern for Stage 1.

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│      LLM (Trainer)   │────►│   Shell Script      │────►│      Godot          │
│                     │     │   (Stage 1)         │     │   (Renderer)        │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### Cheap vs Nasty Analysis

| Aspect | Shell Script (Cheap) | ENet Data Flow (Nasty) |
|--------|---------------------|------------------------|
| **Encoding** | JSON or annotated GDScript | Binary ENet packets |
| **Model** | Synchronous request/reply | Asynchronous, credit-based |
| **Performance** | Doesn't matter (one-time) | Critical (millions/sec) |
| **Error Handling** | Normal errors expected | Silent discard or close |
| **Extensibility** | High - evolving plans | None - frozen protocol |

## Shell Script Interface

### Input (from LLM)
```json
{
  "plan_id": "uuid",
  "timestamp": "ISO8601",
  "actions": [
    {"type": "move", "entity": "npc_1", "x": 10, "y": 20},
    {"type": "dialogue", "entity": "npc_1", "text": "Hello, traveler."},
    {"type": "gift", "from": "player", "to": "npc_1", "item": "berry"}
  ]
}
```

### Output (to Godot)
```
# Godot reads from stdin or named pipe
{"status": "ok", "plan_id": "uuid"}
```

## Implementation Notes

1. **`godot_sandbox/`** provides the ENet server reference for how Godot expects messages
2. Shell script validates LLM output before injection
3. No runtime coordination - plans are pre-validated
4. Stage 2 will introduce IPyHOP-temporal planner

## File Locations

- Reference: `thirdparty/godot_sandbox/`
- Shell script: `tools/gdscript_injector.sh`
- Python bridge: `python-bridge/`

## Usage

### 1. Setup Python Bridge

```bash
cd python-bridge
pip install -e .
```

### 2. Start Godot with Sandbox

```bash
# In godot-sandbox project
godot --path . --editor
```

Or run the Godot scene directly.

### 3. Inject a Plan

```bash
# Validate and inject a generated plan
./tools/gdscript_injector.sh plan.json

# Output:
# {
#   "status": "ok",
#   "plan_id": "abc123",
#   "action_count": 3
# }
```

### 4. Verify in Godot

The injected plan should now be executing in Godot.

## Example Plan

```json
{
  "plan_id": "move_to_player_001",
  "timestamp": "2026-03-23T06:45:00Z",
  "actions": [
    {
      "type": "move",
      "entity": "npc_1",
      "x": 15,
      "y": 25,
      "speed": 2.0
    },
    {
      "type": "dialogue",
      "entity": "npc_1",
      "text": "The weather is lovely today, isn't it?",
      "wait_for_response": true
    },
    {
      "type": "state_change",
      "entity": "npc_1",
      "state": "friendly",
      "duration": 300
    }
  ]
}
```

## Stage 2: Planner Integration

Future work:
- Integrate [IPyHOP-temporal](https://github.com/V-Sekai-fire/IPyHOP-temporal) planner
- Planner generates plans in GDScript directly
- Shell script validates and injects

## Protocol Reference

See `thirdparty/godot_sandbox/` for the ENet JSON-RPC 2.0 protocol that Godot expects.
