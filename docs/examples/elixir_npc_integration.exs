# Elixir NPC Integration Examples
# For Godot ENet Sandbox - Rope Bridge Project
#
# These examples demonstrate how to integrate Elixir (IPyHOP temporal planner)
# with Python RL and Godot GDScript for NPC behavior.
#
# NOTE: These are Elixir code examples. Run with `elixir elixir_npc_integration.exs`
# or compile with `elixirc`.

## Example 1: Basic NPC Trait System
#
# The 5-trait NPC system (shy, energetic, kind, snooty, lazy) with
# friendship tracking (0-100 scale) and daydream-based memory consolidation.

defmodule NPC.Traits do
  @traits [:shy, :energetic, :kind, :snooty, :lazy]
  @friendship_range 0..100

  defstruct traits: %{},
            friendship: %{},
            daydreams: [],
            last_interaction: nil

  def new(), do: %__MODULE__{}

  def set_trait(%__MODULE__{} = npc, trait, value) when trait in @traits do
    %{npc | traits: Map.put(npc.traits, trait, value)}
  end

  def adjust_friendship(%__MODULE__{} = npc, character_id, amount) do
    current = Map.get(npc.friendship, character_id, 50)
    new_friendship = clamp(current + amount, 0, 100)
    %{npc | friendship: Map.put(npc.friendship, character_id, new_friendship)}
  end

  def daydream(%__MODULE__{} = npc, memory_fragment) do
    %{npc | daydreams: [memory_fragment | npc.daydreams], last_interaction: System.system_time(:second)}
  end

  def export_for_rl(%__MODULE__{} = npc) do
    %{
      traits: npc.traits,
      friendship: npc.friendship,
      daydream_count: length(npc.daydreams)
    }
  end
end

## Example 2: Temporal Planner Integration (IPyHOP)
#
# The clean-room IPyHOP temporal planner for goal-directed NPC behavior.
#
# Goals are structured as temporal sequences with preconditions and effects.

defmodule NPC.Planner do
  @moduledoc """
  IPyHOP Temporal Planner integration for NPC goals.
  
  Goals are structured as temporal sequences with preconditions and effects.
  """

  defstruct [:current_goal, :plan, :executing_step]

  @goal_library %{
    greet_player: %{
      description: "Approach and greet the player",
      preconditions: [:player_visible, :not_already_greeted],
      steps: [:turn_toward_player, :speak_greeting, :offer_help],
      postconditions: [:player_acknowledged]
    },
    follow_player: %{
      description: "Follow the player at a respectful distance",
      preconditions: [:player_moving, :has_movement_ability],
      steps: [:calculate_trajectory, :move_along_path],
      postconditions: [:following_player]
    },
    daydream: %{
      description: "Enter daydream state for memory consolidation",
      preconditions: [:alone, :needs_memory_consolidation],
      steps: [:find_safe_location, :enter_daydream_state],
      postconditions: [:memory_consolidated]
    }
  }

  def select_goal(npc_state) do
    # Simple goal selection based on state
    cond do
      Map.get(npc_state, :player_visible) -> :greet_player
      Map.get(npc_state, :needs_memory_consolidation) -> :daydream
      Map.get(npc_state, :player_moving) -> :follow_player
      true -> nil
    end
  end

  def generate_plan(goal) when Map.has_key?(@goal_library, goal) do
    @goal_library[goal]
  end

  def validate_step?(plan, step, state) do
    # Check if step preconditions are met
    Enum.all?(plan.preconditions, &(&1 |> Map.get(state) || false))
  end
end

## Example 3: JSON-RPC API Bridge
#
# Communication bridge between Elixir (planner) and Python (RL engine).

defmodule NPC.Bridge do
  @endpoint "http://localhost:4000/rpc"

  def send_state_for_rl(npc_state) do
    case HTTPoison.post(@endpoint, Jason.encode!(npc_state), [{"Content-Type", "application/json"}]) do
      {:ok, %{status_code: 200, body: body}} ->
        {:ok, Jason.decode!(body)}
      {:ok, response} ->
        {:error, {:http_error, response.status_code, response.body}}
      {:error, reason} ->
        {:error, reason}
    end
  end

  def receive_action(action) do
    # Handle action from RL engine
    case action[:type] do
      :move -> apply_move_action(action[:params])
      :speak -> apply_speak_action(action[:params])
      :interact -> apply_interact_action(action[:params])
      _ -> {:error, :unknown_action}
    end
  end
end

## Example 4: Full NPC Update Cycle
#
# Complete update cycle: sense -> plan -> act -> learn

defmodule NPC.Cycle do
  def update(npc, world_state) do
    # 1. Sense the world
    sensed = sense_world(npc, world_state)

    # 2. Generate/update plan
    plan = NPC.Planner.generate_plan(sensed)

    # 3. Select next action
    {action, plan} = select_next_action(npc, plan, sensed)

    # 4. Execute action
    {npc, result} = execute_action(npc, action, world_state)

    # 5. Learn from outcome
    npc = learn_from_result(npc, action, result)

    {npc, action}
  end

  defp sense_world(npc, world_state) do
    %{
      player_visible: world_state[:player_position] != nil,
      player_moving: world_state[:player_velocity] != {0, 0, 0},
      alone: length(world_state[:nearby_characters]) == 0,
      needs_memory_consolidation: length(npc.daydreams) > 5
    }
  end

  defp select_next_action(npc, nil, _sensed), do: {:nop, %{}}

  defp select_next_action(npc, plan, sensed) do
    # Get next executable step from plan
    step = Enum.at(plan.steps, plan.executing_step || 0)
    {step, plan}
  end

  defp execute_action(npc, {:nop, _}, _), do: {npc, :no_op}

  defp execute_action(npc, {action, plan}, sensed) do
    case NPC.Planner.validate_step?(plan, action, sensed) do
      true -> apply(NPCActions, action, [npc, plan[:params]])
      false -> {npc, :invalid_action}
    end
  end

  defp apply_move_action(params), do: IO.puts("Moving: #{inspect(params)}")
  defp apply_speak_action(params), do: IO.puts("Speaking: #{inspect(params)}")
  defp apply_interact_action(params), do: IO.puts("Interacting: #{inspect(params)}")
end

## Example 5: Using the Cycle
#
# Example usage of the NPC update cycle

defmodule NPC.Example do
  def run_cycle do
    # Create an NPC
    npc = NPC.Traits.new()
      |> NPC.Traits.set_trait(:kind, 0.8)
      |> NPC.Traits.set_trait(:shy, 0.6)
      |> NPC.Traits.adjust_friendship(:player, 10)

    # Create a world state
    world_state = %{
      player_position: {10, 5, 3},
      player_velocity: {0, 0, 0},
      nearby_characters: []
    }

    # Run one update cycle
    {npc, action} = NPC.Cycle.update(npc, world_state)

    IO.puts("NPC updated. Next action: #{action}")
  end
end

# Run the example when compiled
# NPC.Example.run_cycle()
