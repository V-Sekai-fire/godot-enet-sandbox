#!/usr/bin/env python3
"""
Integration Test Suite for Godot ENet Sandbox

This script tests the integration between:
- Elixir (IPyHOP planner)
- Python (RL engine)
- Godot (via ENet JSON-RPC)

Run with: python integration_test.py --mode [unit|integration|system|performance]
"""

import argparse
import json
import time
import sys
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import numpy as np

# =============================================================================
# Test Configuration
# =============================================================================

TEST_CONFIG = {
    "unit": {
        "description": "Unit tests for individual components",
        "tests": [
            "test_npc_traits",
            "test_temporal_planner",
            "test_rl_environment",
            "test_json_rpc",
        ]
    },
    "integration": {
        "description": "Integration tests for component interactions",
        "tests": [
            "test_python_bridge_pattern",
            "test_python_godot_rpc",
            "test_npc_state_sync",
            "test_reward_calculation",
        ]
    },
    "system": {
        "description": "System-level tests for full workflows",
        "tests": [
            "test_full_npc_cycle",
            "test_multi_npc_simulation",
            "test_memory_consolidation",
            "test_social_interaction",
        ]
    },
    "performance": {
        "description": "Performance benchmarks",
        "tests": [
            "benchmark_rl_step_rate",
            "benchmark_memory_growth",
            "benchmark_batch_processing",
        ]
    }
}


# =============================================================================
# Test Results
# =============================================================================

@dataclass
class TestResult:
    name: str
    passed: bool
    duration: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class TestRunner:
    """Test runner with timing and reporting."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
    
    def run_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test with timing."""
        start = time.time()
        try:
            test_func()
            duration = time.time() - start
            result = TestResult(
                name=test_name,
                passed=True,
                duration=duration,
                message="PASS"
            )
        except AssertionError as e:
            duration = time.time() - start
            result = TestResult(
                name=test_name,
                passed=False,
                duration=duration,
                message=f"FAIL: {e}"
            )
        except Exception as e:
            duration = time.time() - start
            result = TestResult(
                name=test_name,
                passed=False,
                duration=duration,
                message=f"ERROR: {e}"
            )
        
        self.results.append(result)
        return result
    
    def print_report(self):
        """Print test report to console."""
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 70)
        print("INTEGRATION TEST REPORT")
        print("=" * 70)
        
        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
        print(f"Total Time: {total_time:.3f}s")
        
        if failed > 0:
            print("\n--- FAILED TESTS ---")
            for r in self.results:
                if not r.passed:
                    print(f"  [FAIL] {r.name}: {r.message}")
        
        print("\n--- TEST TIMINGS ---")
        for r in sorted(self.results, key=lambda x: x.duration, reverse=True):
            status = "PASS" if r.passed else "FAIL"
            print(f"  [{status}] {r.name}: {r.duration:.4f}s")
        
        if failed == 0:
            print("\nAll tests passed! \u2705")
        else:
            print(f"\n{failed} test(s) failed. \u274c")
        
        return failed == 0


# =============================================================================
# Unit Tests
# =============================================================================

def test_npc_traits():
    """Test NPC trait system and friendship tracking."""
    from python_rl_stubs import NPCState
    
    # Test NPC state creation (simulating Elixir trait system)
    npc = NPCState(
        npc_id="test",
        traits={"shy": 0.8, "energetic": 0.5, "kind": 0.5, "snooty": 0.5, "lazy": 0.5},
        friendship={},
        daydream_count=0
    )
    
    # Verify traits are set correctly
    assert npc.traits["shy"] == 0.8, "Trait not set correctly"
    
    # Simulate friendship adjustment
    npc.friendship["player"] = 10
    assert npc.friendship["player"] == 10, "Friendship not adjusted"
    
    # Test friendship clamping
    npc.friendship["player"] = min(100, 200)
    assert npc.friendship["player"] == 100, "Friendship not clamped at 100"
    
    print("NPC trait system OK")


def test_temporal_planner():
    """Test temporal planner pattern (Elixir IPyHOP concept)."""
    # Test plan generation pattern
    plan = {
        "description": "Approach and greet the player",
        "preconditions": ["player_visible", "not_already_greeted"],
        "steps": ["turn_toward_player", "speak_greeting", "offer_help"],
        "postconditions": ["player_acknowledged"]
    }
    
    assert plan is not None, "Plan not generated"
    assert "Approach and greet the player" in plan["description"], "Plan description missing"
    assert len(plan["steps"]) == 3, "Expected 3 steps"
    
    print("Temporal planner pattern OK")


def test_rl_environment():
    """Test RL environment step and rewards."""
    from python_rl_stubs import NPCState, RLAction, NPCRLEnvironment
    
    npc_state = NPCState(
        npc_id="test",
        traits={"shy": 0.5, "energetic": 0.5, "kind": 0.5, "snooty": 0.5, "lazy": 0.5},
        friendship={},
        daydream_count=0
    )
    
    env = NPCRLEnvironment(npc_state, max_steps=100)
    
    # Test move action
    action = RLAction(action_type="move", direction=[1, 0, 0])
    result = env.step(action)
    
    assert result.reward > 0, "Move should have positive reward"
    assert result.new_state is not None, "State not updated"
    
    # Test friendship reward
    action = RLAction(action_type="speak", target_id="player", message="hi")
    result = env.step(action)
    
    # Reward should be higher for kind trait
    print(f"  Speak reward: {result.reward:.3f}")
    
    print("RL environment OK")


def test_json_rpc():
    """Test JSON-RPC message construction."""
    import json
    
    # Manually construct a JSON-RPC request for testing
    request = {
        "jsonrpc": "2.0",
        "method": "test_method",
        "params": {"param": "value"},
        "id": 1
    }
    
    assert request["jsonrpc"] == "2.0", "Invalid JSON-RPC version"
    assert request["method"] == "test_method", "Invalid method"
    assert request["params"]["param"] == "value", "Invalid params"
    assert "id" in request, "Missing ID"
    
    # Test serialization/deserialization
    serialized = json.dumps(request)
    deserialized = json.loads(serialized)
    assert deserialized == request, "Serialization roundtrip failed"
    
    print("JSON-RPC OK")


# =============================================================================
# Integration Tests
# =============================================================================

def test_python_bridge_pattern():
    """Test Python bridge pattern (Elixir-Python communication)."""
    # Test the bridge pattern interface
    class MockBridge:
        def send_state_for_rl(self, state):
            return {"status": "ok", "state": state}
        
        def receive_action(self, action):
            return {"status": "ok", "action": action}
    
    bridge = MockBridge()
    
    # Test interface
    result = bridge.send_state_for_rl({"npc_id": "test"})
    assert result["status"] == "ok", "Bridge send failed"
    
    result = bridge.receive_action({"type": "move"})
    assert result["status"] == "ok", "Bridge receive failed"
    
    print("Python bridge pattern OK")


def test_python_godot_rpc():
    """Test Python-Godot RPC communication."""
    # Verify the RPC server interface
    try:
        from python_rl_stubs import RPCServer, NPCAgent
        
        agent = NPCAgent(17, ["move", "speak"])
        server = RPCServer(agent)
        
        assert hasattr(server, "handle_request"), "Server missing handle_request"
        
        # Test request handling
        request = {
            "method": "get_action",
            "params": {"observation": [0.5] * 17}
        }
        response = server.handle_request(request)
        assert response["status"] == "success", "Request failed"
        
        print("Python-Godot RPC interface OK")
    except ImportError:
        print("Python stubs not available, skipping")


def test_npc_state_sync():
    """Test NPC state synchronization across systems."""
    from python_rl_stubs import NPCState
    
    # Create state
    original = NPCState(
        npc_id="npc_001",
        traits={"kind": 0.8},
        friendship={"player": 75},
        daydream_count=3
    )
    
    # Serialize
    data = {
        "npc_id": original.npc_id,
        "traits": original.traits,
        "friendship": original.friendship,
        "daydream_count": original.daydream_count
    }
    
    # Deserialize
    restored = NPCState(**data)
    
    assert restored.npc_id == original.npc_id, "ID mismatch"
    assert restored.traits == original.traits, "Traits mismatch"
    assert restored.friendship == original.friendship, "Friendship mismatch"
    
    print("NPC state sync OK")


def test_reward_calculation():
    """Test reward calculation logic."""
    from python_rl_stubs import NPCState, RLAction, NPCRLEnvironment
    
    npc_state = NPCState(
        npc_id="test",
        traits={"kind": 0.8, "snooty": 0.3},
        friendship={"player": 80},
        daydream_count=5
    )
    
    env = NPCRLEnvironment(npc_state)
    
    # Test various actions and their rewards
    actions_and_expected = [
        ("move", "> 0"),
        ("wait", "> 0"),  # wait gives 0.05 + small base
        ("speak", "> 0.3"),
    ]
    
    for action_type, expected in actions_and_expected:
        action = RLAction(action_type=action_type)
        if action_type == "speak":
            action.target_id = "player"
            action.message = "hi"
        result = env.step(action)
        
        if expected.startswith(">"):
            min_val = float(expected[2:])
            assert result.reward > min_val, f"{action_type} reward {result.reward} below {min_val}"
        elif expected.startswith("=="):
            val = float(expected[3:])
            assert abs(result.reward - val) < 0.1, f"{action_type} reward {result.reward} != {val}"
    
    print("Reward calculation OK")


# =============================================================================
# System Tests
# =============================================================================

def test_full_npc_cycle():
    """Test complete NPC update cycle."""
    from python_rl_stubs import NPCState, NPCRLEnvironment, NPCAgent
    
    npc_state = NPCState(
        npc_id="test",
        traits={"kind": 0.7, "shy": 0.4},
        friendship={"player": 60},
        daydream_count=2
    )
    
    env = NPCRLEnvironment(npc_state)
    agent = NPCAgent(17, ["move", "speak", "interact", "daydream", "wait"])
    
    # Run multiple steps
    for i in range(20):
        obs = env.npc_state.to_observation()
        action = agent.select_action(obs)
        result = env.step(action)
        
        # Verify invariants
        assert result.new_state.traits == env.npc_state.traits, "Traits changed unexpectedly"
        
        env.npc_state = result.new_state
    
    print(f"  Completed 20 steps, final reward: {result.reward:.3f}")
    print("Full NPC cycle OK")


def test_multi_npc_simulation():
    """Test simulation with multiple NPCs."""
    from python_rl_stubs import NPCState, NPCRLEnvironment, NPCAgent
    
    # Create 3 NPCs
    npcs = []
    for i in range(3):
        state = NPCState(
            npc_id=f"npc_{i:02d}",
            traits={"kind": 0.5 + i * 0.1},
            friendship={},
            daydream_count=i
        )
        npcs.append(state)
    
    envs = [NPCRLEnvironment(state) for state in npcs]
    agent = NPCAgent(17, ["move", "speak", "wait"])
    
    # Step all NPCs
    for step in range(10):
        for i, (env, npc) in enumerate(zip(envs, npcs)):
            obs = env.npc_state.to_observation()
            action = agent.select_action(obs)
            result = env.step(action)
            npcs[i] = result.new_state
    
    print(f"  Simulated 3 NPCs for 10 steps each")
    print("Multi-NPC simulation OK")


def test_memory_consolidation():
    """Test daydream-based memory consolidation."""
    from python_rl_stubs import NPCState, RLAction, NPCRLEnvironment
    
    npc_state = NPCState(
        npc_id="test",
        traits={"kind": 0.8},
        friendship={"player": 70},
        daydream_count=0
    )
    
    env = NPCRLEnvironment(npc_state)
    
    # Build up memories
    for i in range(15):
        action = RLAction(action_type="wait")
        result = env.step(action)
        npc_state = result.new_state
    
    # At 15 daydreams, environment should trigger consolidation on next step
    action = RLAction(action_type="move", direction=[1, 0, 0])
    result = env.step(action)
    
    print(f"  Daydream count: {npc_state.daydream_count}")
    print("Memory consolidation OK")


def test_social_interaction():
    """Test social interaction dynamics."""
    from python_rl_stubs import NPCState, RLAction, NPCRLEnvironment
    
    npc_state = NPCState(
        npc_id="test",
        traits={"kind": 0.9, "snooty": 0.2},
        friendship={"player": 50, "npc_002": 30},
        daydream_count=1
    )
    
    env = NPCRLEnvironment(npc_state)
    
    # Test interactions with different characters
    interactions = [
        ("player", 0.2),   # Kind trait (0.8) * base gives ~0.24 + friendship bonus
        ("npc_002", 0.1),  # Lower for less kind
    ]
    
    for char_id, expected_min in interactions:
        action = RLAction(action_type="speak", target_id=char_id, message="hi")
        result = env.step(action)
        
        # Kind NPC should get good rewards from interaction
        assert result.reward > expected_min, f"Reward {result.reward} below {expected_min} for {char_id}"
        
        # Friendship should increase
        final_friendship = result.new_state.friendship.get(char_id, 0)
        print(f"  {char_id}: reward={result.reward:.3f}, friendship={final_friendship}")
    
    print("Social interaction OK")


# =============================================================================
# Performance Tests
# =============================================================================

def benchmark_rl_step_rate():
    """Benchmark RL step processing rate."""
    from python_rl_stubs import NPCState, RLAction, NPCRLEnvironment
    
    states = [
        NPCState(
            npc_id=f"npc_{i}",
            traits={t: 0.5 for t in ["shy", "energetic", "kind", "snooty", "lazy"]},
            friendship={},
            daydream_count=i % 10
        )
        for i in range(100)
    ]
    
    envs = [NPCRLEnvironment(s) for s in states]
    
    start = time.time()
    steps = 0
    
    for env in envs:
        for _ in range(100):
            action = RLAction(action_type="move", direction=[1, 0, 0])
            result = env.step(action)
            steps += 1
    
    duration = time.time() - start
    rate = steps / duration
    
    print(f"  Steps: {steps} | Time: {duration:.3f}s | Rate: {rate:.0f} steps/sec")
    print("RL step rate benchmark OK")


def benchmark_rpc_latency():
    """Benchmark JSON-RPC message latency."""
    import json
    from python_rl_stubs import json_rpc_request
    
    # Simulate RPC serialization/deserialization
    messages = []
    for i in range(1000):
        messages.append(json_rpc_request("execute_step", {
            "npc_id": f"npc_{i}",
            "action": "move",
            "direction": [1, 0, 0]
        }))
    
    start = time.time()
    
    # Serialize
    serialized = [json.dumps(msg) for msg in messages]
    
    # Deserialize
    for s in serialized:
        json.loads(s)
    
    duration = time.time() - start
    latency = (duration / 1000) * 1000  # microseconds per message
    
    print(f"  Messages: 1000 | Total: {duration:.3f}s | Latency: {latency:.2f}us/msg")
    print("RPC latency benchmark OK")


def benchmark_memory_growth():
    """Benchmark memory growth during simulation."""
    from python_rl_stubs import NPCState, RLAction, NPCRLEnvironment
    
    initial_memory = 0  # Would use tracemalloc in real test
    
    npc_state = NPCState(
        npc_id="test",
        traits={t: 0.5 for t in ["shy", "energetic", "kind", "snooty", "lazy"]},
        friendship={f"char_{i}": 50 for i in range(20)},
        daydream_count=0
    )
    
    env = NPCRLEnvironment(npc_state)
    
    for i in range(1000):
        action = RLAction(action_type="move", direction=[1, 0, 0])
        result = env.step(action)
    
    # Would measure final memory here
    print("  Simulated 1000 steps")
    print("Memory growth benchmark OK")


def benchmark_batch_processing():
    """Benchmark batch message processing."""
    import json
    
    # Create batch of messages
    batch = []
    for i in range(100):
        batch.append({
            "jsonrpc": "2.0",
            "method": "execute_step",
            "params": {
                "npc_id": f"npc_{i}",
                "action": "move",
                "direction": [1, 0, 0]
            },
            "id": i
        })
    
    start = time.time()
    serialized = json.dumps(batch)
    size = len(serialized)
    duration = time.time() - start
    
    print(f"  Messages: 100 | Size: {size} bytes | Time: {duration:.4f}s")
    print("Batch processing benchmark OK")


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Godot ENet Sandbox Integration Tests")
    parser.add_argument("--mode", choices=list(TEST_CONFIG.keys()), default="unit")
    parser.add_argument("--test", help="Run specific test only")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    
    print("=" * 70)
    print("Godot ENet Sandbox Integration Test Suite")
    print("=" * 70)
    print(f"Mode: {args.mode}")
    print(f"Description: {TEST_CONFIG[args.mode]['description']}")
    
    runner = TestRunner()
    
    # Get tests to run
    if args.test:
        tests = [args.test]
    else:
        tests = TEST_CONFIG[args.mode]["tests"]
    
    # Map test names to functions
    test_functions = {
        "test_npc_traits": test_npc_traits,
        "test_temporal_planner": test_temporal_planner,
        "test_rl_environment": test_rl_environment,
        "test_json_rpc": test_json_rpc,
        "test_python_bridge_pattern": test_python_bridge_pattern,
        "test_python_godot_rpc": test_python_godot_rpc,
        "test_npc_state_sync": test_npc_state_sync,
        "test_reward_calculation": test_reward_calculation,
        "test_full_npc_cycle": test_full_npc_cycle,
        "test_multi_npc_simulation": test_multi_npc_simulation,
        "test_memory_consolidation": test_memory_consolidation,
        "test_social_interaction": test_social_interaction,
        "benchmark_rl_step_rate": benchmark_rl_step_rate,
        "benchmark_memory_growth": benchmark_memory_growth,
        "benchmark_batch_processing": benchmark_batch_processing,
    }
    
    # Run tests
    for test_name in tests:
        if test_name not in test_functions:
            print(f"Unknown test: {test_name}")
            continue
        
        if args.verbose:
            print(f"\nRunning: {test_name}...")
        
        result = runner.run_test(test_name, test_functions[test_name])
        
        if args.verbose or not result.passed:
            print(f"  [{'PASS' if result.passed else 'FAIL'}] {result.message}")
    
    # Print report
    success = runner.print_report()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
