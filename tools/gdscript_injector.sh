#!/bin/bash
# gdscript_injector.sh - Shell injection for LLM-generated plans
#
# Usage: ./gdscript_injector.sh <plan.json>
#
# Reads plan from JSON file or stdin, validates via Python,
# and injects into Godot via python-bridge ENet client.
#
# Stage 1: LLM generates plan -> Shell validates -> Python bridge sends to Godot
# Stage 2: Godot receives via ENet (reference: thirdparty/godot_sandbox/)
# Stage 3: Future - IPyHOP-temporal planner integration

set -euo pipefail

# --- Configuration ---
GODOT_IP="127.0.0.1"
GODOT_PORT=4000
PYTHON_BRIDGE_CMD="python3 -m godot_enet_bridge.client"

# --- Helpers ---
usage() {
    echo "Usage: $0 <plan.json>" >&2
    echo "       $0 -h" >&2
    echo "" >&2
    echo "Stage 1: LLM generates plan" >&2
    echo "Stage 2: Shell validates plan" >&2
    echo "Stage 3: Python bridge sends to Godot via ENet" >&2
    exit 1
}

validate_plan() {
    local plan_file="$1"
    python3 -c "
import json, sys
try:
    with open('$plan_file') as f:
        plan = json.load(f)
    
    # Validate required fields
    assert 'plan_id' in plan, 'Missing plan_id'
    assert 'actions' in plan, 'Missing actions'
    assert isinstance(plan['actions'], list), 'actions must be a list'
    
    # Validate each action
    for i, action in enumerate(plan['actions']):
        assert 'type' in action, f'Action {i}: missing type'
        valid_types = ['move', 'dialogue', 'gift', 'animation', 'state_change']
        assert action['type'] in valid_types, f'Action {i}: invalid type {action[\"type\"]}'
    
    print(json.dumps({'status': 'ok', 'plan_id': plan['plan_id'], 'action_count': len(plan['actions'])}, indent=2))
    sys.exit(0)
    
except Exception as e:
    print(json.dumps({'status': 'error', 'error': str(e)}), file=sys.stderr)
    sys.exit(1)
"
}

send_to_godot() {
    local plan_file="$1"
    
    # Use python-bridge to send the plan
    # The bridge handles ENet UDP + JSON-RPC 2.0
    if command -v python3 &>/dev/null; then
        python3 -m godot_enet_bridge.client send --host "$GODOT_IP" --port "$GODOT_PORT" --data "@$plan_file"
    else
        echo "ERROR: python3 not found. Install python-bridge first:" >&2
        echo "  cd python-bridge && pip install -e ." >&2
        exit 1
    fi
}

# --- Main ---
main() {
    local plan_file=""
    local verbose=false
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help) usage ;;
            -v|--verbose) verbose=true ; shift ;;
            -) plan_file="$(mktemp)"; cat > "$plan_file"; break ;;
            *.json) plan_file="$1"; shift ;;
            *) echo "ERROR: Unknown argument: $1" >&2; usage ;;
        esac
    done
    
    [ -z "$plan_file" ] && usage
    [ ! -f "$plan_file" ] && echo "ERROR: Plan file not found: $plan_file" >&2 && exit 1
    
    # Validate
    if [ "$verbose" = true ]; then
        echo "[1/3] Validating plan..."
    fi
    result=$(validate_plan "$plan_file")
    echo "$result"
    
    # Inject to Godot
    if [ "$verbose" = true ]; then
        echo "[2/3] Sending to Godot via python-bridge..."
    fi
    send_to_godot "$plan_file"
    
    if [ "$verbose" = true ]; then
        echo "[3/3] Plan injected successfully."
        echo "      Godot should now execute the plan."
    fi
}

main "$@"
