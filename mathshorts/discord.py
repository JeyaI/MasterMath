"""The Discord side of the script loop (#28): a REST client on the standard library, nothing else.

Only `ms tick` and `ms discord hello` use it; jobs never see the token. Settings come from the
environment (see config/mathshorts.env.example):

    DISCORD_BOT_TOKEN       the bot's token
    MS_DISCORD_USER_ID      the only account whose reactions and replies count
    MS_DISCORD_CHANNEL_ID   the drafts channel; one thread per Short

`Client` is the interface `ms tick` needs; tests pass a fake with the same methods.
"""
from __future__ import annotations

import base64
import json
import os
import socket
import ssl
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path

API = "https://discord.com/api/v10"
GATEWAY = "gateway.discord.gg"
ACCEPT, CROSS, STOP = "✅", "❌", "🛑"
LIMIT = 2000                          # characters per message


class DiscordError(RuntimeError):
    pass


@dataclass
class Settings:
    token: str
    user_id: str
    channel_id: str

    @classmethod
    def from_env(cls) -> "Settings":
        names = ("DISCORD_BOT_TOKEN", "MS_DISCORD_USER_ID", "MS_DISCORD_CHANNEL_ID")
        missing = [n for n in names if not os.environ.get(n)]
        if missing:
            raise DiscordError(f"not set: {', '.join(missing)} (see config/mathshorts.env.example)")
        return cls(*(os.environ[n].strip() for n in names))


class Client:
    def __init__(self, settings: Settings):
        self.s = settings

    # --- transport -------------------------------------------------------------------
    def _call(self, method: str, path: str, body=None, files: dict[str, Path] | None = None):
        headers = {"Authorization": f"Bot {self.s.token}",
                   "User-Agent": "DiscordBot (https://github.com/mathshorts, 1.0)"}
        data = None
        if files:
            boundary = uuid.uuid4().hex
            parts = [_part(boundary, 'name="payload_json"', "application/json", json.dumps(body or {}).encode())]
            for i, (name, path_) in enumerate(files.items()):
                parts.append(_part(boundary, f'name="files[{i}]"; filename="{name}"', "text/markdown",
                                   Path(path_).read_bytes()))
            data = b"".join(parts) + f"--{boundary}--\r\n".encode()
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        elif body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        for attempt in range(3):
            req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    raw = r.read()
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as e:
                text = e.read().decode(errors="replace")
                if e.code == 429 and attempt < 2:
                    time.sleep(float(json.loads(text or "{}").get("retry_after", 1.0)) + 0.1)
                    continue
                raise DiscordError(f"{method} {path.split('?')[0]}: HTTP {e.code} {text[:200]}") from None
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:   # network blips: retry
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise DiscordError(f"{method} {path.split('?')[0]}: {e}") from None
        raise DiscordError(f"{method} {path}: rate limited")

    # --- what ms tick uses --------------------------------------------------------------
    def open_thread(self, title: str) -> str:
        """A starter message in the drafts channel and a thread on it; returns the thread id."""
        starter = self._call("POST", f"/channels/{self.s.channel_id}/messages", {"content": f"**{title}**"})
        thread = self._call("POST", f"/channels/{self.s.channel_id}/messages/{starter['id']}/threads",
                            {"name": title[:100], "auto_archive_duration": 10080})
        return thread["id"]

    def post(self, thread_id: str, content: str, files: dict[str, Path] | None = None,
             reactions: tuple[str, ...] = ()) -> str:
        msg = self._call("POST", f"/channels/{thread_id}/messages",
                         {"content": content[:LIMIT], "allowed_mentions": {"parse": []}}, files)
        for emoji in reactions:
            self.react(thread_id, msg["id"], emoji)
        return msg["id"]

    def react(self, channel_id: str, message_id: str, emoji: str) -> None:
        self._call("PUT", f"/channels/{channel_id}/messages/{message_id}/reactions/"
                          f"{urllib.parse.quote(emoji)}/@me")

    def reactors(self, channel_id: str, message_id: str, emoji: str) -> set[str]:
        users = self._call("GET", f"/channels/{channel_id}/messages/{message_id}/reactions/"
                                  f"{urllib.parse.quote(emoji)}?limit=100")
        return {u["id"] for u in users or []}

    def messages_after(self, channel_id: str, after: str | None) -> list[dict]:
        """Messages newer than `after`, oldest first."""
        out, cursor = [], after or "0"
        while True:
            page = self._call("GET", f"/channels/{channel_id}/messages?after={cursor}&limit=100") or []
            if not page:
                return out
            page.sort(key=lambda m: int(m["id"]))
            out += [{"id": m["id"], "author_id": m["author"]["id"], "bot": bool(m["author"].get("bot")),
                     "content": m.get("content", "")} for m in page]
            cursor = page[-1]["id"]
            if len(page) < 100:
                return out

    # --- setup check -----------------------------------------------------------------
    def hello(self, echo=print) -> None:
        """Check every permission ms tick needs, by using each one once."""
        try:
            me = self._call("GET", "/users/@me")
        except DiscordError as e:
            if "HTTP 401" in str(e):
                raise DiscordError("Discord rejected DISCORD_BOT_TOKEN. Use the token from Developer Portal > "
                                   "Bot > Reset Token (about 70 characters, two dots), not the OAuth2 client secret.") from None
            raise
        echo(f"  token ok: bot {me['username']}")
        ch = self._call("GET", f"/channels/{self.s.channel_id}")
        echo(f"  channel ok: #{ch.get('name')}")
        member = self._call("GET", f"/guilds/{ch['guild_id']}/members/{self.s.user_id}")
        echo(f"  user ok: {member['user']['username']} is in the server")
        identify_once(self.s.token)
        echo("  gateway ok (Discord wants one connection before a bot's first message)")
        thread = self.open_thread("ms discord hello")
        mid = self.post(thread, "Connected. This thread is only a setup check; delete it whenever.",
                        reactions=(ACCEPT,))
        if me["id"] not in self.reactors(thread, mid, ACCEPT):
            raise DiscordError("the bot's own reaction didn't show up")
        self.messages_after(thread, None)
        echo("  posting, threads, reactions and history ok")


def _part(boundary: str, disposition: str, ctype: str, payload: bytes) -> bytes:
    return (f"--{boundary}\r\nContent-Disposition: form-data; {disposition}\r\n"
            f"Content-Type: {ctype}\r\n\r\n").encode() + payload + b"\r\n"


# --- gateway: connect, identify, leave ---------------------------------------------------
def identify_once(token: str, timeout: float = 20) -> None:
    """A minimal websocket client: enough to receive READY once. ms tick itself only uses REST."""
    raw = socket.create_connection((GATEWAY, 443), timeout=timeout)
    sock = ssl.create_default_context().wrap_socket(raw, server_hostname=GATEWAY)
    try:
        key = base64.b64encode(os.urandom(16)).decode()
        sock.sendall((f"GET /?v=10&encoding=json HTTP/1.1\r\nHost: {GATEWAY}\r\nUpgrade: websocket\r\n"
                      f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = sock.recv(4096)
            if not chunk:
                raise DiscordError("gateway closed during the handshake")
            head += chunk
        status, rest = head.split(b"\r\n", 1)[0], head.split(b"\r\n\r\n", 1)[1]
        if b" 101 " not in status:
            raise DiscordError(f"gateway handshake: {status.decode(errors='replace')}")
        reader = _Frames(sock, rest)
        hello = json.loads(reader.next())
        if hello.get("op") != 10:
            raise DiscordError(f"gateway: expected HELLO, got op {hello.get('op')}")
        _send(sock, json.dumps({"op": 2, "d": {"token": token, "intents": 0,
                                               "properties": {"os": "linux", "browser": "ms", "device": "ms"}}}))
        while True:
            msg = json.loads(reader.next())
            if msg.get("op") == 0 and msg.get("t") == "READY":
                break
            if msg.get("op") == 9:
                raise DiscordError("gateway rejected the token (invalid session)")
        _send(sock, b"\x03\xe8", opcode=0x8)
    finally:
        sock.close()


def _send(sock, payload, opcode: int = 0x1) -> None:
    data = payload.encode() if isinstance(payload, str) else payload
    n = len(data)
    head = bytes([0x80 | opcode])
    if n < 126:
        head += bytes([0x80 | n])
    elif n < 65536:
        head += bytes([0x80 | 126]) + struct.pack(">H", n)
    else:
        head += bytes([0x80 | 127]) + struct.pack(">Q", n)
    mask = os.urandom(4)
    sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


class _Frames:
    def __init__(self, sock, buffered: bytes):
        self.sock, self.buf = sock, buffered

    def _take(self, n: int) -> bytes:
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise DiscordError("gateway closed the connection")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def next(self) -> str:
        message = b""
        while True:
            b0, b1 = self._take(2)
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._take(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._take(8))[0]
            payload = self._take(n)
            opcode = b0 & 0x0F
            if opcode == 0x8:
                code = struct.unpack(">H", payload[:2])[0] if len(payload) >= 2 else None
                raise DiscordError(f"gateway closed: {code} {payload[2:].decode(errors='replace')}")
            if opcode in (0x9, 0xA):          # ping / pong
                continue
            message += payload
            if b0 & 0x80:
                return message.decode()
