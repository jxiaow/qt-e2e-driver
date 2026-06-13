from __future__ import annotations

import json
import socket
from typing import Any

import pytest

import qt_e2e_driver.client as client_module
from qt_e2e_driver import E2EConnectionError, E2EInfraError, QtE2EClient


class FakeSocket:
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks
        self.sent = b""

    def __enter__(self) -> "FakeSocket":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def sendall(self, data: bytes) -> None:
        self.sent += data

    def recv(self, size: int) -> bytes:
        if not self._chunks:
            return b""
        chunk = self._chunks.pop(0)
        if len(chunk) <= size:
            return chunk
        self._chunks.insert(0, chunk[size:])
        return chunk[:size]


def install_response(monkeypatch: pytest.MonkeyPatch, *chunks: bytes) -> FakeSocket:
    fake = FakeSocket(list(chunks))

    def create_connection(address: tuple[str, int], timeout: float) -> FakeSocket:
        fake.address = address  # type: ignore[attr-defined]
        fake.timeout = timeout  # type: ignore[attr-defined]
        return fake

    monkeypatch.setattr(socket, "create_connection", create_connection)
    return fake


def json_line(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload) + "\n").encode("utf-8")


def test_request_sends_newline_delimited_json(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = install_response(monkeypatch, json_line({"ok": True, "data": {"pong": True}}))
    client = QtE2EClient("127.0.0.1", 19527, timeout=1.5)

    response = client.request("health")

    assert response == {"ok": True, "data": {"pong": True}}
    assert fake.address == ("127.0.0.1", 19527)  # type: ignore[attr-defined]
    assert fake.timeout == 1.5  # type: ignore[attr-defined]
    assert fake.sent == b'{"command": "health"}\n'


def test_request_rejects_non_object_json_response(monkeypatch: pytest.MonkeyPatch) -> None:
    install_response(monkeypatch, b'["ok"]\n')
    client = QtE2EClient()

    with pytest.raises(E2EInfraError, match="response must be a JSON object"):
        client.request("health")


def test_request_rejects_empty_response(monkeypatch: pytest.MonkeyPatch) -> None:
    install_response(monkeypatch, b"")
    client = QtE2EClient()

    with pytest.raises(E2EInfraError, match="empty response for health"):
        client.request("health")


def test_request_rejects_response_over_size_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    install_response(monkeypatch, b'{"ok": true, "data": {"message": "too long"}}\n')
    client = QtE2EClient(max_response_bytes=16)

    with pytest.raises(E2EInfraError, match="response too large for health"):
        client.request("health")


def test_client_rejects_invalid_timeout() -> None:
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        QtE2EClient(timeout=0)


def test_client_rejects_invalid_response_limit() -> None:
    with pytest.raises(ValueError, match="max_response_bytes must be greater than 0"):
        QtE2EClient(max_response_bytes=0)


def test_query_reports_missing_data(monkeypatch: pytest.MonkeyPatch) -> None:
    install_response(monkeypatch, json_line({"ok": True}))
    client = QtE2EClient()

    with pytest.raises(E2EInfraError, match="missing data for query"):
        client.query("login.account")


def test_health_and_wait_idle_send_common_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[bytes] = []
    responses = [
        json_line({"ok": True, "data": {"status": "ok"}}),
        json_line({"ok": True, "data": {"idle": True}}),
    ]

    class SequencedSocket(FakeSocket):
        def sendall(self, data: bytes) -> None:
            sent.append(data)

    def create_connection(address: tuple[str, int], timeout: float) -> SequencedSocket:
        return SequencedSocket([responses.pop(0)])

    monkeypatch.setattr(socket, "create_connection", create_connection)
    client = QtE2EClient()

    assert client.health() == {"status": "ok"}
    assert client.wait_idle(timeout_ms=250) == {"idle": True}
    assert sent == [
        b'{"command": "health"}\n',
        b'{"command": "wait-idle", "timeoutMs": 250}\n',
    ]


def test_wait_until_ready_retries_until_health_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = QtE2EClient()
    attempts = 0
    sleeps: list[float] = []

    def health() -> dict[str, Any]:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise E2EConnectionError("server not listening yet")
        return {"status": "ok"}

    monkeypatch.setattr(client, "health", health)
    monkeypatch.setattr(client_module.time, "monotonic", iter([0.0, 0.1, 0.2]).__next__)
    monkeypatch.setattr(client_module.time, "sleep", sleeps.append)

    assert client.wait_until_ready(timeout=1.0, interval=0.05) == {"status": "ok"}
    assert attempts == 3
    assert sleeps == [0.05, 0.05]


def test_wait_until_ready_times_out_with_endpoint_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = QtE2EClient("127.0.0.1", 19527)

    def health() -> dict[str, Any]:
        raise E2EConnectionError("server not listening yet")

    monkeypatch.setattr(client, "health", health)
    monkeypatch.setattr(client_module.time, "monotonic", iter([0.0, 0.2, 0.4]).__next__)
    monkeypatch.setattr(client_module.time, "sleep", lambda seconds: None)

    with pytest.raises(E2EConnectionError, match="timed out waiting"):
        client.wait_until_ready(timeout=0.3, interval=0.1)


def test_wait_until_ready_rejects_invalid_arguments() -> None:
    client = QtE2EClient()

    with pytest.raises(ValueError, match="timeout must be greater than or equal to 0"):
        client.wait_until_ready(timeout=-1)
    with pytest.raises(ValueError, match="interval must be greater than 0"):
        client.wait_until_ready(interval=0)


def test_wait_idle_rejects_invalid_timeout() -> None:
    client = QtE2EClient()

    with pytest.raises(ValueError, match="timeout_ms must be greater than or equal to 0"):
        client.wait_idle(timeout_ms=-1)
