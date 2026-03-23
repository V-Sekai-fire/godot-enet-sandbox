"""
SandboxClient - Client for Godot ENet Sandbox communication.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import enet

logger = logging.getLogger(__name__)


@dataclass
class RPCResponse:
    """Result of an RPC call."""
    id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    raw: Optional[bytes] = None


class SandboxClient:
    """
    ENet client for communicating with Godot Sandbox instances.
    
    Usage:
        client = SandboxClient(host="localhost", port=4000)
        await client.connect()
        response = await client.call("add_coins", args=[10])
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 4000,
        timeout: float = 5.0,
        max_retries: int = 3,
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self._peer: Optional[enet.Peer] = None
        self._host: Optional[enet.Host] = None
        self._connected = False
        self._request_id = 0
        self._pending: Dict[int, asyncio.Future] = {}
    
    async def connect(self) -> None:
        """Establish connection to the Godot sandbox server."""
        await asyncio.to_thread(self._connect_sync)
        self._connected = True
    
    def _connect_sync(self) -> None:
        """Synchronous connection setup (runs in thread)."""
        self._host = enet.Host(enet.Address(self.host, self.port), peer_count=1, channel_limit=2)
        # Connect to Godot server (which should be listening)
        self._peer = self._host.connect(enet.Address("localhost", self.port), channels=2, data=b"client")
        
        # Wait for connection to establish
        event = self._host.service(1000)  # 1 second timeout
        if event.type == enet.EVENT_TYPE_CONNECT:
            logger.info(f"Connected to Godot Sandbox at {self.host}:{self.port}")
        else:
            raise ConnectionError(f"Failed to connect: {event}")
    
    async def disconnect(self) -> None:
        """Close the connection."""
        if self._peer:
            self._peer.disconnect()
        if self._host:
            self._host.destroy()
        self._connected = False
    
    async def call(
        self,
        method: str,
        args: Optional[list] = None,
        params: Optional[dict] = None,
    ) -> RPCResponse:
        """
        Make an RPC call to the Godot sandbox.
        
        Args:
            method: The method name to call
            args: Positional arguments (deprecated, use params)
            params: Named parameters (recommended)
            
        Returns:
            RPCResponse with result or error
        """
        if args is not None and params is None:
            params = {"args": args}
        
        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {},
        }
        
        return await self._send_request(request)
    
    async def notify(
        self,
        method: str,
        params: Optional[dict] = None,
    ) -> None:
        """
        Send a notification (no response expected).
        
        Args:
            method: The method name
            params: Parameters for the method
        """
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }
        await asyncio.to_thread(self._send_sync, request)
    
    def _send_sync(self, request: dict) -> None:
        """Synchronous send (runs in thread)."""
        data = json.dumps(request).encode("utf-8")
        packet = enet.Packet(data, enet.PACKET_FLAG_RELIABLE)
        self._peer.send(0, packet)
    
    async def _send_request(self, request: dict) -> RPCResponse:
        """Send request and wait for response."""
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        request_id = request["id"]
        self._pending[request_id] = future
        
        await asyncio.to_thread(self._send_sync, request)
        
        try:
            return await asyncio.wait_for(future, timeout=self.timeout)
        except asyncio.TimeoutError:
            future.cancel()
            raise TimeoutError(f"RPC call timed out after {self.timeout}s")
    
    def _handle_packet(self, packet: enet.Packet) -> None:
        """Handle incoming packet from Godot server."""
        try:
            data = packet.data
            if not data:
                return
            
            message = json.loads(data.decode("utf-8"))
            
            if "id" in message and message["id"] in self._pending:
                # This is a response to our request
                future = self._pending.pop(message["id"])
                if not future.done():
                    future.set_result(RPCResponse(
                        id=message["id"],
                        result=message.get("result"),
                        error=message.get("error"),
                        raw=data,
                    ))
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to decode packet: {e}")
        except Exception as e:
            logger.error(f"Error handling packet: {e}")
    
    async def poll(self) -> Optional[RPCResponse]:
        """Poll for incoming messages (call this in a loop)."""
        if not self._host:
            return None
        
        event = await asyncio.to_thread(self._host.service, 0)
        if event.type == enet.EVENT_TYPE_RECEIVE:
            self._handle_packet(event.packet)
        return None
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
