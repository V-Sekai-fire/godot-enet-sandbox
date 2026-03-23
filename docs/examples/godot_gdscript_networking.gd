# Godot GDScript Networking Examples for ENet Sandbox
#
# These examples demonstrate networking integration between Godot and
# the Python ENet server via JSON-RPC 2.0 over ENet transport.
#
# See: docs/api.md for full API reference

extends Node

# =============================================================================
# Constants
# =============================================================================

const SERVER_HOST := "localhost"
const SERVER_PORT := 5555
const PING_INTERVAL := 30.0  # seconds

# =============================================================================
# Network Manager
# =============================================================================

var enet_peer: ENetPeer = null
var is_connected := false
var request_id := 1
var pending_requests := {}
var heartbeat_timer := 0.0

# =============================================================================
# JSON-RPC 2.0 Utilities
# =============================================================================

func json_rpc_request(method: String, params: Dictionary = {}) -> Dictionary:
    """Create a JSON-RPC 2.0 request dictionary."""
    var request := {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }
    request_id += 1
    return request

func json_rpc_notification(method: String, params: Dictionary = {}) -> Dictionary:
    """Create a JSON-RPC 2.0 notification (no ID)."""
    return {
        "jsonrpc": "2.0",
        "method": method,
        "params": params
    }

func parse_json_rpc_response(data: Dictionary) -> Dictionary:
    """Parse JSON-RPC response and handle errors."""
    if data.has("error"):
        push_error("JSON-RPC Error: %s" % [data["error"]])
        return {}
    return data.get("result", {})

# =============================================================================
# Connection Management
# =============================================================================

func _ready():
    print("Initializing Godot ENet Network Manager")
    
    # Initialize ENet
    var err := ENet.create()
    if err != OK:
        push_error("ENet initialization failed: %s" % [err])
        return
    
    # Create host (client mode)
    err = ENet.create_host("0.0.0.0", 0, 1)
    if err != OK:
        push_error("ENet host creation failed: %s" % [err])
        return
    
    print("ENet initialized. Connecting to server...")
    connect_to_server()


func _exit_tree():
    """Clean up on node exit."""
    disconnect_from_server()
    ENet.destroy()


func connect_to_server():
    """Connect to the Python ENet server."""
    if is_connected:
        return
    
    var address := ENetAddress.create()
    address.host = SERVER_HOST
    address.port = SERVER_PORT
    
    enet_peer = ENet.connect(address)
    if enet_peer == null:
        push_error("Failed to connect to server")
        return
    
    is_connected = true
    print("Connected to Python ENet server at %s:%d" % [SERVER_HOST, SERVER_PORT])
    
    # Send initial handshake
    var handshake := json_rpc_request("handshake", {
        "godot_version": OS.get_version(),
        "protocol_version": "1.0",
        "scene_name": get_tree().current_scene.name
    })
    send_rpc(handshake)


func disconnect_from_server():
    """Disconnect from the server."""
    if not is_connected:
        return
    
    if enet_peer:
        enet_peer.destroy()
        enet_peer = null
    
    is_connected = false
    print("Disconnected from server")


# =============================================================================
# RPC Communication
# =============================================================================

func send_rpc(data: Dictionary) -> bool:
    """Send a JSON-RPC message to the server."""
    if not is_connected or enet_peer == null:
        push_error("Not connected to server")
        return false
    
    var err = enet_peer.send(ENetPacket.create(JSON.stringify(data), 1))
    if err != OK:
        push_error("Failed to send packet: %s" % [err])
        return false
    
    if data.has("id"):
        pending_requests[data["id"]] = data
    
    return true


func send_rpc_async(method: String, params: Dictionary, callback: Callable) -> void:
    """
    Send an RPC request and invoke callback when response arrives.
    
    Usage:
        send_rpc_async("execute_step", {"action": "move", "direction": [1, 0, 0]}, 
            func(result): print(result))
    """
    var request := json_rpc_request(method, params)
    pending_requests[request["id"]] = {
        "callback": callback,
        "method": method
    }
    send_rpc(request)


func send_notification(method: String, params: Dictionary) -> void:
    """Send a JSON-RPC notification (fire-and-forget)."""
    var notification := json_rpc_notification(method, params)
    send_rpc(notification)


# =============================================================================
# RPC Response Handling
# =============================================================================

func handle_packet(packet: ENetPacket) -> void:
    """Handle incoming ENet packet."""
    var data := JSON.new().parse(packet.get_data())
    
    if data == null:
        push_error("Failed to parse packet data")
        return
    
    # Handle batch responses
    if data is Array:
        for item in data:
            handle_single_response(item)
    else:
        handle_single_response(data)


func handle_single_response(data: Dictionary) -> void:
    """Handle a single JSON-RPC response."""
    if data.has("id"):
        # This is a response to a request
        var request_id = data["id"]
        if pending_requests.has(request_id):
            var request_info = pending_requests[request_id]
            pending_requests.erase(request_id)
            
            if request_info is Dictionary and request_info.has("callback"):
                request_info["callback"].call(data.get("result"))
    else:
        # This is a notification from server
        handle_server_notification(data)


func handle_server_notification(data: Dictionary) -> void:
    """Handle unsolicited notifications from server."""
    if data["method"] == "event":
        # Broadcast event to all interested nodes
        var event := data["params"]
        emit_signal("server_event", event)
    elif data["method"] == "npc_action":
        # Handle NPC action broadcast
        var action := data["params"]
        handle_npc_action(action)


func handle_npc_action(action: Dictionary) -> void:
    """Handle NPC action from server."""
    var npc_id := action.get("npc_id", "unknown")
    var action_type := action.get("action_type", "unknown")
    var params := action.get("params", {})
    
    print("NPC Action: %s -> %s" % [npc_id, action_type])
    
    # Dispatch action to appropriate handler
    match action_type:
        "move":
            var direction = Vector3(params["direction"])
            move_npc(npc_id, direction)
        "speak":
            var message = params.get("message", "")
            speak(npc_id, message)
        "interact":
            var target = params.get("target", "")
            interact(npc_id, target)
        "emote":
            var emote = params.get("emote", "wave")
            play_emote(npc_id, emote)
        _:
            print("Unknown action type: %s" % action_type)


# =============================================================================
# API Methods - Client-Server Communication
# =============================================================================

func handshake() -> void:
    """Send handshake to server."""
    send_rpc(json_rpc_request("handshake"))


func load_binary(resource_path: String) -> void:
    """
    Load a binary resource (mesh, texture, etc.) from server.
    
    The server will stream the binary data over the ENet connection.
    """
    send_rpc(json_rpc_request("load_binary", {
        "path": resource_path,
        "expected_size": 0  # Will be set by server based on actual size
    }))


func execute_step(step_data: Dictionary) -> void:
    """
    Execute a single simulation step for an NPC.
    
    step_data should include:
    - npc_id: The NPC to step
    - action: The action to take
    - params: Action parameters
    """
    send_rpc(json_rpc_request("execute_step", step_data))


func set_npc_state(npc_id: String, state: Dictionary) -> void:
    """Update NPC state on server."""
    send_rpc(json_rpc_request("set_state", {
        "npc_id": npc_id,
        "state": state
    }))


func get_npc_state(npc_id: String, callback: Callable) -> void:
    """Request NPC state from server."""
    send_rpc_async("get_state", {"npc_id": npc_id}, callback)


func subscribe_to_events() -> void:
    """Subscribe to server events."""
    send_notification("subscribe", {
        "events": ["npc_actions", "player_actions", "world_state"]
    })


# =============================================================================
# Example Usage
# =============================================================================

# Example 1: Request and display NPC state
func example_get_npc_state(npc_id: String):
    get_npc_state(npc_id, func(result):
        print("NPC State: %s" % [JSON.stringify(result)])
    )


# Example 2: Execute a step with player interaction
func example_player_interaction(player_id: String, action: String):
    execute_step({
        "npc_id": "npc_001",
        "action": action,
        "target_id": player_id,
        "params": {
            "message": "Hello! How are you today?"
        }
    })


# Example 3: Batch multiple NPC updates
func example_batch_npc_updates(npc_states: Array):
    # Send multiple state updates in one batch
    var requests = []
    for state in npc_states:
        requests.append(json_rpc_request("set_state", state))
    
    # Send as batch
    var batch_data = JSON.stringify(requests)
    enet_peer.send(ENetPacket.create(batch_data, 1))


# =============================================================================
# Heartbeat / Connection Management
# =============================================================================

func _process(delta: float) -> void:
    if not is_connected or enet_peer == null:
        return
    
    # Handle incoming packets
    var packet
    while (packet = enet_peer.receive()):
        handle_packet(packet)
    
    # Send heartbeat
    heartbeat_timer += delta
    if heartbeat_timer >= PING_INTERVAL:
        heartbeat_timer = 0.0
        send_notification("heartbeat", {
            "timestamp": Time.get_unix_time_from_system(),
            "godot_scene": get_tree().current_scene.name
        })


# =============================================================================
# Error Handling
# =============================================================================

signal void connection_lost()
signal void connection_restored()

func handle_connection_error():
    is_connected = false
    emit_signal("connection_lost")
    # Attempt reconnection after delay
    yield(get_tree().create_timer(5.0), "timeout")
    connect_to_server()
    if is_connected:
        emit_signal("connection_restored")
