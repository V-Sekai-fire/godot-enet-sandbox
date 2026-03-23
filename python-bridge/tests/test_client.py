"""Tests for SandboxClient."""

import pytest
import asyncio
from godot_enet_bridge import SandboxClient, JSONRPCMessage


@pytest.mark.asyncio
class TestSandboxClient:
    """Test cases for SandboxClient."""
    
    async def test_message_encoding(self):
        """Test JSON-RPC message encoding/decoding."""
        message = JSONRPCMessage(
            jsonrpc="2.0",
            id=1,
            method="test_method",
            params={"key": "value"},
        )
        
        encoded = message.to_json().encode("utf-8")
        decoded = JSONRPCMessage.from_json(encoded.decode("utf-8"))
        
        assert decoded.id == 1
        assert decoded.method == "test_method"
        assert decoded.params == {"key": "value"}
    
    async def test_client_creation(self):
        """Test client can be created."""
        client = SandboxClient(host="localhost", port=4000)
        assert client.host == "localhost"
        assert client.port == 4000
        assert not client._connected
