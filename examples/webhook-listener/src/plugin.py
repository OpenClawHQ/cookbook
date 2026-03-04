"""
Webhook Listener Plugin

A working example plugin that starts an HTTP server to receive webhook payloads.
Uses only Python standard library (http.server, json, datetime).
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import threading


class PluginConfig(dict):
    """Configuration container for plugins."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class PluginBase(ABC):
    """Abstract base class for all plugins."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin with configuration.

        Args:
            config: Dictionary of configuration parameters
        """
        self.config = PluginConfig(config or {})
        self.setup()

    @abstractmethod
    def setup(self):
        """Called once during initialization. Store or validate configuration."""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the plugin with the given context.

        Args:
            context: Dictionary containing action and parameters

        Returns:
            Result of the plugin execution
        """
        pass


class WebhookStore:
    """Thread-safe storage for webhook payloads."""

    def __init__(self, max_payloads: int = 100):
        self.payloads = []
        self.max_payloads = max_payloads
        self.next_id = 1

    def add(self, data: Dict[str, Any]) -> int:
        """Add a payload and return its ID."""
        payload = {
            "id": self.next_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data,
        }
        self.payloads.append(payload)

        # Keep only the most recent payloads
        if len(self.payloads) > self.max_payloads:
            self.payloads.pop(0)

        self.next_id += 1
        return payload["id"]

    def get_all(self, filters: Optional[Dict[str, str]] = None) -> list:
        """Get all payloads, optionally filtered."""
        if not filters:
            return self.payloads

        filtered = []
        for payload in self.payloads:
            match = True
            for key, value in filters.items():
                if key not in payload["data"] or str(payload["data"][key]) != value:
                    match = False
                    break
            if match:
                filtered.append(payload)

        return filtered

    def clear(self) -> int:
        """Clear all payloads and return count."""
        count = len(self.payloads)
        self.payloads.clear()
        return count


class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the webhook server."""

    def do_POST(self):
        """Handle POST requests to /webhook."""
        if self.path == "/webhook":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                payload = json.loads(body) if body else {}
                webhook_id = self.server.webhook_store.add(payload)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                response = {
                    "status": "received",
                    "id": webhook_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))

            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                response = {"error": "Invalid JSON"}
                self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_GET(self):
        """Handle GET requests for retrieving payloads and health checks."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        # Convert query params to simple dict
        filters = {k: v[0] for k, v in query_params.items() if v}

        if path == "/payloads":
            payloads = self.server.webhook_store.get_all(filters if filters else None)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {"count": len(payloads), "payloads": payloads}
            self.wfile.write(json.dumps(response).encode("utf-8"))

        elif path == "/health":
            count = len(self.server.webhook_store.payloads)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {"status": "running", "payloads_stored": count}
            self.wfile.write(json.dumps(response).encode("utf-8"))

        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_DELETE(self):
        """Handle DELETE requests to clear payloads."""
        if self.path == "/payloads":
            count = self.server.webhook_store.clear()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {"status": "cleared", "count": count}
            self.wfile.write(json.dumps(response).encode("utf-8"))

        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class WebhookListener(PluginBase):
    """
    A plugin that starts an HTTP server to receive and process webhook payloads.
    """

    def setup(self):
        """Initialize webhook listener configuration."""
        self.host = self.config.get("host") or os.getenv("WEBHOOK_HOST", "127.0.0.1")
        self.port = int(
            self.config.get("port") or os.getenv("WEBHOOK_PORT", "8000")
        )
        self.max_payloads = int(
            self.config.get("max_payloads")
            or os.getenv("WEBHOOK_MAX_PAYLOADS", "100")
        )

        self.webhook_store = WebhookStore(self.max_payloads)
        self.server = None
        self.server_thread = None

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action based on context["action"].

        Supported actions:
        - start: Start the webhook server
        - get_payloads: Get stored payloads
        - get_health: Get server health status
        - clear_payloads: Clear stored payloads
        """
        action = context.get("action")

        if action == "start":
            return self._start_server()
        elif action == "get_payloads":
            return self._get_payloads(context)
        elif action == "get_health":
            return self._get_health()
        elif action == "clear_payloads":
            return self._clear_payloads()
        else:
            return {"error": f"Unknown action: {action}"}

    def _start_server(self) -> Dict[str, Any]:
        """Start the webhook server in a background thread."""
        if self.server is not None:
            return {"status": "already_running", "url": f"http://{self.host}:{self.port}/webhook"}

        try:
            # Create server with our custom store
            self.server = HTTPServer((self.host, self.port), WebhookHandler)
            self.server.webhook_store = self.webhook_store

            # Start server in background thread
            self.server_thread = threading.Thread(
                target=self.server.serve_forever, daemon=True
            )
            self.server_thread.start()

            return {
                "status": "started",
                "url": f"http://{self.host}:{self.port}/webhook",
                "health_check": f"http://{self.host}:{self.port}/health",
            }

        except Exception as e:
            return {"error": f"Failed to start server: {str(e)}"}

    def _get_payloads(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get stored payloads with optional filtering."""
        filters = context.get("filters")
        payloads = self.webhook_store.get_all(filters)

        return {"count": len(payloads), "payloads": payloads}

    def _get_health(self) -> Dict[str, Any]:
        """Get server health status."""
        count = len(self.webhook_store.payloads)

        return {
            "status": "running" if self.server else "stopped",
            "payloads_stored": count,
            "url": f"http://{self.host}:{self.port}/webhook" if self.server else None,
        }

    def _clear_payloads(self) -> Dict[str, Any]:
        """Clear all stored payloads."""
        count = self.webhook_store.clear()

        return {"status": "cleared", "count": count}


if __name__ == "__main__":
    # Example usage
    config = {
        "host": "127.0.0.1",
        "port": 8000,
    }

    plugin = WebhookListener(config)

    print("Starting webhook listener...")
    result = plugin.execute({"action": "start"})
    print(json.dumps(result, indent=2))

    print("\nServer is running. Send webhooks to the URL above.")
    print("Example: curl -X POST http://127.0.0.1:8000/webhook -H 'Content-Type: application/json' -d '{\"event\": \"test\"}'")

    # Keep the server running
    try:
        plugin.server_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down...")
        if plugin.server:
            plugin.server.shutdown()
