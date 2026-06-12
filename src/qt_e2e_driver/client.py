from __future__ import annotations

import json
import socket
from typing import Any

from .catalog import AliasCatalog
from .errors import E2EConnectionError, E2EInfraError


class QtE2EClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 19527, timeout: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def request(self, command: str, **params: Any) -> dict[str, Any]:
        payload = {"command": command, **params}
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
                raw = self._read_line(sock)
        except OSError as exc:
            raise E2EConnectionError(
                f"E2E_CONNECTION_ERROR: {self.host}:{self.port} command={command}"
            ) from exc

        try:
            response = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise E2EInfraError(f"E2E_INFRA_ERROR: invalid JSON response for {command}") from exc

        if not response.get("ok", False):
            code = response.get("code", "E2E_INFRA_ERROR")
            message = response.get("message", "command failed")
            raise E2EInfraError(f"{code}: {message}; command={command}")
        return response

    def load_alias_catalog(self) -> AliasCatalog:
        response = self.request("list-aliases")
        return AliasCatalog.from_payload(response.get("data", {}))

    def query(self, alias: str) -> dict[str, Any]:
        return self.request("query", name=alias)["data"]

    def click(self, alias: str) -> dict[str, Any]:
        return self.request("click", name=alias)["data"]

    def set_text(self, alias: str, value: str) -> dict[str, Any]:
        return self.request("set-text", name=alias, value=value)["data"]

    def get_text(self, alias: str) -> str:
        data = self.request("get-text", name=alias)["data"]
        return str(data.get("text", ""))

    @staticmethod
    def _read_line(sock: socket.socket) -> bytes:
        chunks: list[bytes] = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            if b"\n" in chunk:
                break
        return b"".join(chunks).split(b"\n", 1)[0]
