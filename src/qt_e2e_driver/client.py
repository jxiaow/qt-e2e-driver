from __future__ import annotations

import json
import socket
import time
from typing import Any

from .catalog import AliasCatalog
from .errors import E2EConnectionError, E2EInfraError


class QtE2EClient:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 19527,
        timeout: float = 5.0,
        max_response_bytes: int = 1024 * 1024,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if max_response_bytes <= 0:
            raise ValueError("max_response_bytes must be greater than 0")

        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_response_bytes = max_response_bytes

    def request(self, command: str, **params: Any) -> dict[str, Any]:
        payload = {"command": command, **params}
        try:
            with socket.create_connection(
                (self.host, self.port), timeout=self.timeout
            ) as sock:
                sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
                raw = self._read_line(sock, command)
        except OSError as exc:
            raise E2EConnectionError(
                f"E2E_CONNECTION_ERROR: {self.host}:{self.port} command={command}"
            ) from exc

        if not raw:
            raise E2EInfraError(f"E2E_INFRA_ERROR: empty response for {command}")

        try:
            response = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise E2EInfraError(
                f"E2E_INFRA_ERROR: invalid JSON response for {command}"
            ) from exc

        if not isinstance(response, dict):
            raise E2EInfraError(
                f"E2E_INFRA_ERROR: response must be a JSON object for {command}"
            )

        if not response.get("ok", False):
            code = response.get("code", "E2E_INFRA_ERROR")
            message = response.get("message", "command failed")
            raise E2EInfraError(f"{code}: {message}; command={command}")
        return response

    def load_alias_catalog(self) -> AliasCatalog:
        return AliasCatalog.from_payload(
            self._data("list-aliases", self.request("list-aliases"))
        )

    def health(self) -> dict[str, Any]:
        return self._data("health", self.request("health"))

    def wait_until_ready(
        self, timeout: float = 10.0, interval: float = 0.1
    ) -> dict[str, Any]:
        if timeout < 0:
            raise ValueError("timeout must be greater than or equal to 0")
        if interval <= 0:
            raise ValueError("interval must be greater than 0")

        deadline = time.monotonic() + timeout
        while True:
            try:
                return self.health()
            except E2EConnectionError as exc:
                if time.monotonic() >= deadline:
                    raise E2EConnectionError(
                        "E2E_CONNECTION_ERROR: timed out waiting for "
                        f"{self.host}:{self.port} after {timeout:g}s"
                    ) from exc
                time.sleep(interval)

    def wait_idle(self, timeout_ms: int = 5000) -> dict[str, Any]:
        if timeout_ms < 0:
            raise ValueError("timeout_ms must be greater than or equal to 0")
        return self._data("wait-idle", self.request("wait-idle", timeoutMs=timeout_ms))

    def query(self, alias: str) -> dict[str, Any]:
        return self._data("query", self.request("query", name=alias))

    def click(self, alias: str) -> dict[str, Any]:
        return self._data("click", self.request("click", name=alias))

    def set_text(self, alias: str, value: str) -> dict[str, Any]:
        return self._data(
            "set-text", self.request("set-text", name=alias, value=value)
        )

    def get_text(self, alias: str) -> str:
        data = self._data("get-text", self.request("get-text", name=alias))
        return str(data.get("text", ""))

    def _read_line(self, sock: socket.socket, command: str) -> bytes:
        chunks: list[bytes] = []
        size = 0
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break

            newline_index = chunk.find(b"\n")
            if newline_index >= 0:
                chunks.append(chunk[:newline_index])
                size += newline_index
                if size > self.max_response_bytes:
                    raise E2EInfraError(
                        f"E2E_INFRA_ERROR: response too large for {command}"
                    )
                break

            chunks.append(chunk)
            size += len(chunk)
            if size > self.max_response_bytes:
                raise E2EInfraError(
                    f"E2E_INFRA_ERROR: response too large for {command}"
                )
        return b"".join(chunks)

    @staticmethod
    def _data(command: str, response: dict[str, Any]) -> dict[str, Any]:
        data = response.get("data")
        if not isinstance(data, dict):
            raise E2EInfraError(f"E2E_INFRA_ERROR: missing data for {command}")
        return data
