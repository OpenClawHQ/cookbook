# Webhook Listener Plugin

A plugin that starts a simple HTTP server to receive and process webhook payloads.

## What It Does

- Starts an HTTP server on a configurable host and port
- Receives webhook POST requests at `/webhook` endpoint
- Stores received payloads in memory
- Supports query filtering and retrieval of stored payloads
- Responds with confirmation when payloads are received

## Requirements

- Python 3.8+
- Network access to the configured port

## Configuration

Create a `config.yaml` file in your plugin directory:

```yaml
host: "127.0.0.1"
port: 8000
max_payloads: 100
```

Or pass them as environment variables:
- `WEBHOOK_HOST`: Server host (default: 127.0.0.1)
- `WEBHOOK_PORT`: Server port (default: 8000)
- `WEBHOOK_MAX_PAYLOADS`: Maximum payloads to store (default: 100)

## How to Run

```bash
# Install
pip install -e .

# Run
python -m plugin
```

The server will start and listen for webhooks at `http://localhost:8000/webhook`.

## Example Usage

```bash
# Send a webhook
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "push", "repository": "cookbook"}'

# Get all payloads
curl http://localhost:8000/payloads

# Get payloads with a specific event
curl "http://localhost:8000/payloads?event=push"

# Clear stored payloads
curl -X DELETE http://localhost:8000/payloads
```

## API Endpoints

### `POST /webhook`
Receive a webhook payload.

**Request Body:**
```json
{
    "event": "push",
    "repository": "cookbook",
    "branch": "main"
}
```

**Response:**
```json
{
    "status": "received",
    "id": 1,
    "timestamp": "2026-03-04T12:00:00Z"
}
```

### `GET /payloads`
Retrieve stored payloads. Optional query parameters filter by payload fields.

**Response:**
```json
{
    "count": 5,
    "payloads": [
        {
            "id": 1,
            "event": "push",
            "repository": "cookbook",
            "timestamp": "2026-03-04T12:00:00Z",
            "data": {"event": "push", "repository": "cookbook"}
        }
    ]
}
```

### `DELETE /payloads`
Clear all stored payloads.

**Response:**
```json
{
    "status": "cleared",
    "count": 5
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
    "status": "running",
    "payloads_stored": 5
}
```

## How It Works

1. When the plugin executes with action `start`, it creates an HTTP server
2. The server listens for POST requests to `/webhook`
3. Each webhook is stored with metadata (ID, timestamp)
4. You can retrieve and filter stored payloads via GET requests
5. The server runs until the plugin is shut down

## Under the Hood

This plugin uses only Python's standard library (`http.server`, `json`, `datetime`, `urllib.parse`). No external dependencies required.

## License

MIT License
