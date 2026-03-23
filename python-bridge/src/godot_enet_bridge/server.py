"""
SandboxServer - Server for Godot ENet Sandbox communication.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional

import enet

logger = logging.getLogger(__name__)


class SandboxServer:
    """
    ENet server for accepting Godot Sandbox connections.
    
    Usage:
        server = SandboxServer(port=4000)
        await server.start()
        
        async for client, message in server.incoming_messages():
            print(f"Received: {message}")
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 4000,
        max_peers: int = 8,
        channels: int = 2,
    ):
        self.host = host
        self.port = port
        self.max_peers = max_peers
        self.channels = channels
        self._server: Optional[enet.Host] = None
        self._running = False
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._rpc_handlers: Dict[str, Callable] = {}
    
    async def start(self) -> None:
        """Start the server."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._start_sync,
        )
        self._running = True
        logger.info(f"Server started on {self.host}:{self.port}")
    
    def _start_sync(self) -> None:
        """Synchronous server startup."""
        self._server = enet.Host(enet.Address(self.host, self.port), self.max_peers, self.channels)
    
    async def stop(self) -> None:
        """Stop the server."""
        self._running = False
        if self._server:
            self._server.destroy()
        logger.info("Server stopped")
    
    def register_rpc(self, method: str, handler: Callable) -> None:
        """
        Register an RPC handler.
        
        Args:
            method: The method name clients can call
            handler: Function that takes params dict and returns result dict
        """
        self._rpc_handlers[method] = handler
    
    def _handle_rpc(self, method: str, params: dict) -> dict:
        """Handle an incoming RPC call."""
        if method not in self._rpc_handlers:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }
        
        try:
            result = self._rpc_handlers[method](params)
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": result,
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "error": {
                    "code": -32000,
                    "message": str(e),
                },
            }
    
    def _handle_packet(self, peer: enet.Peer, packet: enet.Packet) -> None:
        """Handle incoming packet."""
        try:
            data = packet.data
            if not data:
                return
            
            message = json.loads(data.decode("utf-8"))
            
            if "method" in message:
                # This is an RPC call
                response = self._handle_rpc(message["method"], message)
                response_data = json.dumps(response).encode("utf-8")
                response_packet = enet.Packet(response_data, enet.PACKET_FLAG_RELIABLE)
                peer.send(0, response_packet)
            elif "id" in message:
                # This is an RPC response (unexpected on server)
                logger.debug(f"Received unexpected response: {message}")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to decode packet: {e}")
        except Exception as e:
            logger.error(f"Error handling packet: {e}")
    
    async def incoming_messages(self):
        """
        Async generator for incoming messages.
        
        Usage:
            async for client_address, message in server.incoming_messages():
                print(f"From {client_address}: {message}")
        """
        while self._running:
            if not self._server:
                await asyncio.sleep(0.1)
                continue
            
            event = await asyncio.get_event_loop().run_in_executor(
                None,
                self._server.service,
                100,  # 100ms timeout
            )
            
            if event.type == enet.EVENT_TYPE_CONNECT:
                logger.info(f"Client connected: {event.peer.address}")
                yield (event.peer.address, {"type": "connect"})
            
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                self._handle_packet(event.peer, event.packet)
                # Put message in queue for manual polling
                try:
                    data = event.packet.data
                    if data:
                        message = json.loads(data.decode("utf-8"))
                        yield (event.peer.address, message)
                except:
                    pass
            
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                logger.info(f"Client disconnected: {event.peer.address}")
                yield (event.peer.address, {"type": "disconnect"})
    
    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to all connected clients."""
        if not self._server:
            return
        
        data = json.dumps(message).encode("utf-8")
        packet = enet.Packet(data, enet.PACKET_FLAG_RELIABLE)
        
        for peer in self._server.peers:
            if peer.state == enet.PEER_STATE_CONNECTED:
                peer.send(0, packet)
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
