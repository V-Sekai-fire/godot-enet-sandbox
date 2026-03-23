# Elixir NPC Integration Examples

This file documents the Elixir code examples in `elixir_npc_integration.exs`.

## Overview

The Elixir examples demonstrate the IPyHOP temporal planner integration for NPC behavior in the Godot ENet Sandbox project.

## File Contents

### 1. NPC.Traits Module

Implements the 5-trait NPC system:
- `shy` - Preference for distance from others
- `energetic` - Cost of movement
- `kind` - Reward from helpful interactions  
- `snooty` - Penalty for social interaction
- `lazy` - Preference for inaction

**Key Functions:**
- `new()` - Create a new NPC
- `set_trait/3` - Set a trait value
- `adjust_friendship/3` - Modify friendship (0-100 scale)
- `daydream/2` - Record a memory fragment
- `export_for_rl/1` - Serialize state for Python RL

### 2. NPC.Planner Module

Implements the IPyHOP temporal planner:

**Goal Structure:**
```elixir
%{
  description: "Human-readable description",
  preconditions: [:player_visible, ...],  # When goal is valid
  steps: [:step1, :step2, :step3],       # Temporal sequence
  postconditions: [:result1, ...]         # After completion
}
```

**Available Goals:**
- `:greet_player` - Approach and greet
- `:follow_player` - Track player movement
- `:daydream` - Memory consolidation

### 3. NPC.Bridge Module

Provides JSON-RPC communication to Python:
- `send_state_for_rl/1` - Send NPC state for RL inference
- `receive_action/1` - Receive action from RL engine

### 4. NPC.Cycle Module

Complete update cycle:
1. **Sense** - Gather world state
2. **Plan** - Select goal and generate plan
3. **Act** - Execute next step
4. **Learn** - Update based on results

### 5. Example Usage

```elixir
# Create NPC with traits
npc = NPC.Traits.new()
  |> NPC.Traits.set_trait(:kind, 0.8)
  |> NPC.Traits.set_trait(:shy, 0.6)
  |> NPC.Traits.adjust_friendship(:player, 10)

# Update cycle
world_state = %{player_visible: true, player_moving: false, ...}
{npc, action} = NPC.Cycle.update(npc, world_state)
```

## Running

Compile and run the examples:

```bash
# Compile
elixirc elixir_npc_integration.exs

# Run (uncomment NPC.Example.run_cycle() in file)
elixir elixir_npc_integration.exs
```

## Testing

The examples can be tested with the integration test suite:

```bash
python integration_test.py --mode unit
```

## Related

- [Python RL Stubs](python_rl_stubs.py) - RL environment interface
- [Godot Networking](godot_gdscript_networking.gd) - Client implementation
- [Integration Tests](integration_test.py) - Test suite
