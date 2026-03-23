"""
Protocol utilities for Godot ENet Sandbox communication.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class JSONRPCMessage:
    """JSON-RPC 2.0 message structure."""
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, omitting None values."""
        return {k: v for k, v in {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": self.method,
            "params": self.params,
            "result": self.result,
            "error": self.error,
        }.items() if v is not None}
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JSONRPCMessage":
        """Create from dictionary."""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method"),
            params=data.get("params"),
            result=data.get("result"),
            error=data.get("error"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "JSONRPCMessage":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


def encode_message(
    method: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    id: Optional[int] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
) -> bytes:
    """
    Encode a JSON-RPC message to bytes.
    
    Args:
        method: RPC method name
        params: RPC parameters
        id: Request ID (None for notifications)
        result: RPC result (for responses)
        error: RPC error (for error responses)
    
    Returns:
        UTF-8 encoded message bytes
    """
    message = JSONRPCMessage(
        jsonrpc="2.0",
        id=id,
        method=method,
        params=params,
        result=result,
        error=error,
    )
    return message.to_json().encode("utf-8")


def decode_message(data: bytes) -> JSONRPCMessage:
    """
    Decode a JSON-RPC message from bytes.
    
    Args:
        data: UTF-8 encoded message bytes
    
    Returns:
        JSONRPCMessage instance
    """
    return JSONRPCMessage.from_json(data.decode("utf-8"))


class RPCError:
    """RPC error codes (JSON-RPC 2.0 standard)."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32000
    
    @staticmethod
    def parse_error(message: str) -> Dict[str, Any]:
        return {
            "code": RPCError.PARSE_ERROR,
            "message": message or "Parse error",
        }
    
    @staticmethod
    def invalid_request(message: str) -> Dict[str, Any]:
        return {
            "code": RPCError.INVALID_REQUEST,
            "message": message or "Invalid request",
        }
    
    @staticmethod
    def method_not_found(method: str) -> Dict[str, Any]:
        return {
            "code": RPCError.METHOD_NOT_FOUND,
            "message": f"Method not found: {method}",
        }
    
    @staticmethod
    def invalid_params(message: str) -> Dict[str, Any]:
        return {
            "code": RPCError.INVALID_PARAMS,
            "message": message or "Invalid params",
        }
    
    @staticmethod
    def internal_error(message: str) -> Dict[str, Any]:
        return {
            "code": RPCError.INTERNAL_ERROR,
            "message": message or "Internal error",
        }
