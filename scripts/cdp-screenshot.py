#!/usr/bin/env python3
"""
Full-page screenshot via Chrome DevTools Protocol.
Uses only Python stdlib - no external dependencies.

Usage: cdp-screenshot.py URL OUTPUT [WIDTH]
"""

import sys
import os
import socket
import hashlib
import base64
import struct
import json
import subprocess
import time
import urllib.request
import platform
import random

# ============================================================================
# Minimal WebSocket Client (stdlib only)
# ============================================================================

class SimpleWebSocket:
    """Minimal WebSocket client using only Python stdlib."""

    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, url):
        """Connect to WebSocket URL (ws://host:port/path)."""
        # Parse URL
        if url.startswith("ws://"):
            url = url[5:]
        host_port, path = url.split("/", 1)
        path = "/" + path

        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 80

        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)
        self.sock.connect((host, port))

        # WebSocket handshake
        key = base64.b64encode(random.randbytes(16)).decode()
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"\r\n"
        )
        self.sock.sendall(handshake.encode())

        # Read response
        response = b""
        while b"\r\n\r\n" not in response:
            response += self.sock.recv(1024)

        if b"101" not in response:
            raise Exception(f"WebSocket handshake failed: {response[:100]}")

    def send(self, message):
        """Send a text message."""
        payload = message.encode('utf-8')
        length = len(payload)

        # Build frame header
        header = bytearray()
        header.append(0x81)  # FIN + text opcode

        # Mask bit + length
        if length < 126:
            header.append(0x80 | length)  # 0x80 = mask bit
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack(">H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack(">Q", length))

        # Mask key (required for client->server)
        mask = random.randbytes(4)
        header.extend(mask)

        # Mask payload
        masked = bytearray(length)
        for i in range(length):
            masked[i] = payload[i] ^ mask[i % 4]

        self.sock.sendall(bytes(header) + bytes(masked))

    def recv(self):
        """Receive a message."""
        # Read frame header
        header = self._recv_exact(2)

        fin = (header[0] >> 7) & 1
        opcode = header[0] & 0x0F
        masked = (header[1] >> 7) & 1
        length = header[1] & 0x7F

        # Extended length
        if length == 126:
            length = struct.unpack(">H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self._recv_exact(8))[0]

        # Mask key (server shouldn't mask, but handle it)
        mask = self._recv_exact(4) if masked else None

        # Payload
        payload = self._recv_exact(length)

        if mask:
            payload = bytes(payload[i] ^ mask[i % 4] for i in range(length))

        if opcode == 0x01:  # Text
            return payload.decode('utf-8')
        elif opcode == 0x08:  # Close
            return None
        else:
            return payload

    def _recv_exact(self, n):
        """Receive exactly n bytes."""
        data = bytearray()
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise Exception("Connection closed")
            data.extend(chunk)
        return bytes(data)

    def close(self):
        """Close the connection."""
        try:
            # Send close frame
            self.sock.sendall(b'\x88\x80' + random.randbytes(4))
        except:
            pass
        self.sock.close()

# ============================================================================
# Chrome Control
# ============================================================================

def find_free_port():
    """Find an available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def get_chrome_path():
    """Find Chrome executable."""
    system = platform.system()

    if system == 'Darwin':
        paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
        ]
        for p in paths:
            if os.path.exists(p):
                return p
    elif system == 'Windows':
        # Windows Chrome paths
        paths = [
            os.path.expandvars(r'%ProgramFiles%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%LocalAppData%\Google\Chrome\Application\chrome.exe'),
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        # Try shutil.which as fallback
        import shutil
        for name in ['chrome', 'chrome.exe']:
            path = shutil.which(name)
            if path:
                return path
    else:
        # Linux
        import shutil
        for name in ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']:
            path = shutil.which(name)
            if path:
                return path
    return None

def capture_fullpage(url, output, width=1280, format='png'):
    """Capture full-page screenshot using CDP."""
    port = find_free_port()
    chrome = get_chrome_path()

    if not chrome:
        print("Chrome not found", file=sys.stderr)
        return False

    # Start Chrome with debugging
    proc = subprocess.Popen([
        chrome,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--hide-scrollbars',
        f'--remote-debugging-port={port}',
        f'--window-size={width},800',
        url
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        # Wait for Chrome to start
        time.sleep(3)

        # Get page WebSocket URL
        for _ in range(10):
            try:
                pages = json.loads(urllib.request.urlopen(
                    f'http://localhost:{port}/json',
                    timeout=5
                ).read())
                break
            except:
                time.sleep(0.5)
        else:
            print("Could not connect to Chrome", file=sys.stderr)
            return False

        ws_url = None
        for p in pages:
            if p.get('type') == 'page':
                ws_url = p.get('webSocketDebuggerUrl')
                break

        if not ws_url:
            print("No page found", file=sys.stderr)
            return False

        # Connect via WebSocket
        ws = SimpleWebSocket(ws_url)
        msg_id = 1

        def send_command(method, params=None):
            nonlocal msg_id
            cmd = {'id': msg_id, 'method': method}
            if params:
                cmd['params'] = params
            ws.send(json.dumps(cmd))
            msg_id += 1

            # Wait for response with matching id
            while True:
                response = ws.recv()
                if response is None:
                    raise Exception("Connection closed")
                data = json.loads(response)
                if data.get('id') == msg_id - 1:
                    if 'error' in data:
                        raise Exception(data['error'])
                    return data.get('result', {})

        # Wait for page to be ready
        time.sleep(1)

        # Get layout metrics
        metrics = send_command('Page.getLayoutMetrics')
        content_height = int(metrics['contentSize']['height'])
        content_width = int(metrics['contentSize']['width'])

        # Set viewport to full page size
        send_command('Emulation.setDeviceMetricsOverride', {
            'width': width,
            'height': content_height,
            'deviceScaleFactor': 1,
            'mobile': False
        })

        # Small delay for render
        time.sleep(0.5)

        # Capture screenshot
        img_format = 'jpeg' if format == 'jpg' else format
        screenshot_params = {
            'format': img_format,
            'captureBeyondViewport': True,
            'fromSurface': True
        }
        if img_format == 'jpeg':
            screenshot_params['quality'] = 85

        result = send_command('Page.captureScreenshot', screenshot_params)

        # Save image
        img_data = base64.b64decode(result['data'])
        with open(output, 'wb') as f:
            f.write(img_data)

        ws.close()

        print(output)  # Output path for script parsing
        print(f"Captured {width}x{content_height}", file=sys.stderr)
        return True

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: cdp-screenshot.py URL OUTPUT [WIDTH] [FORMAT]", file=sys.stderr)
        print("  WIDTH: viewport width (default: 1280)", file=sys.stderr)
        print("  FORMAT: png or jpg (default: png)", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    output = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    fmt = sys.argv[4] if len(sys.argv) > 4 else 'png'

    success = capture_fullpage(url, output, width, fmt)
    sys.exit(0 if success else 1)
