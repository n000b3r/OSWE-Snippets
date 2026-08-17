#!/usr/bin/env python3
"""
WebSocket helper for targets that expose a command interface over WSS/WS.

Requires: pip install websocket-client

Usage (copy ws_recv_all into your exploit script):

FOR HTTPS SITE:
    ws = websocket.create_connection("wss://target/ws_endpoint", sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.settimeout(RECV_TIMEOUT)
    ws.send(json.dumps({"cmd": "whoami"}))
    output = ws_recv_all(ws)
    print(output)
    ws.close()

FOR HTTP SITE:
    rhost = urlparse(base_url).netloc
    ws = websocket.create_connection(f"ws://{rhost}/send-message?token={token}&group_id=13", header=[f"Cookie: token={token}; username={username}; group=13; group_name=Public Discussion"])
    ws.settimeout(RECV_TIMEOUT)
    ws.send("hi there, from script")
    output = ws_recv_all(ws)
    print(output)
    ws.close()
"""

import json
import re
import websocket
import ssl

# ==============================================================================
# WS RESPONSE DRAINER (copy this section into your main script)
# ==============================================================================

RECV_TIMEOUT = 0.75  # seconds — increase if large outputs are being truncated

_ANSI = re.compile(r'\x1b\[[0-9;]*m')

def _strip_ansi(text: str) -> str:
    return _ANSI.sub('', text).strip()

def ws_recv_all(ws, payload_key: str = "payload", filter_key: str = None, filter_val: str = None,) -> str:
    """
    Drain all response frames from a WebSocket connection for a single command.

    Reads until WebSocketTimeoutException, which signals no more frames are coming.
    Strips ANSI colour codes from each frame before returning.

    Args:
        ws          : Open websocket-client connection with a timeout set.
        payload_key : Key in the JSON frame that holds the output text.
        filter_key  : Optional key to filter on (e.g. "type").
        filter_val  : Skip frames where filter_key != filter_val (e.g. heartbeats).

    Returns:
        All output lines joined by newline.

    Example (app sends {"type": "response", "payload": "..."}):
        output = ws_recv_all(ws, payload_key="payload", filter_key="type", filter_val="response")
    """
    lines = []
    while True:
        try:
            raw_msg = ws.recv()
            
            # Try to parse as JSON
            try:
                msg = json.loads(raw_msg)
                if filter_key and msg.get(filter_key) != filter_val:
                    continue
                text = _strip_ansi(msg.get(payload_key, ""))
                
            # If it's not JSON, just treat the raw message as the output
            except json.decoder.JSONDecodeError:
                text = _strip_ansi(raw_msg)

            if text:
                lines.append(text)
                
        except websocket.WebSocketTimeoutException:
            break
            
    return "\n".join(lines)