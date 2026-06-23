# Protocol Contract

## Goal

Prevent drift between the Python client, alias catalog validation, Qt adapter behavior, and protocol documentation.

## Repo Facts

- Python client code lives in `src/qt_e2e_driver/client.py`.
- Alias catalog validation lives in `src/qt_e2e_driver/catalog.py`.
- Protocol documentation lives in `docs/PROTOCOL.md`.
- Qt server template lives in `include/qt_e2e_driver/TestServer.h` and `src/qt/TestServer.cpp`.
- Protocol tests live in `tests/test_client.py`, `tests/test_catalog.py`, and source-contract tests under `tests/`.

## Core Rules

- Every protocol response consumed by Python must be a JSON object with stable `ok` and `data` behavior.
- Python must fail fast on empty, malformed, non-object, missing-data, and oversized responses.
- Alias catalog shape must remain runtime-owned by the Qt app or test catalog, not duplicated in Python test code.
- If a command, field, or error code changes, update `docs/PROTOCOL.md` and tests in the same task.
- Do not hide protocol failures behind broad exceptions that remove command or endpoint context.

## Design Checklist

- Which command or catalog field is changing?
- Is the change backward-compatible for existing Python tests?
- Does the Qt adapter need matching behavior or documentation?
- What exact failure should users see when integration is wrong?

## Implementation Checklist

- Add or update tests before changing behavior.
- Run targeted tests for `client.py` and `catalog.py` when touched.
- Run full `python -m pytest` before closing.
- Confirm `docs/PROTOCOL.md` still describes implemented behavior.

## Common Smells

- Python tests access `objectName` directly.
- Docs mention a command or field that no test covers.
- The Qt adapter returns failures without actionable `code`, `message`, or `data`.
- A new response parser accepts malformed data silently.
