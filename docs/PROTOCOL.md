# Protocol

The driver uses newline-delimited JSON over a localhost TCP connection.

The Python client reads one response line per request and rejects responses that are empty, not valid JSON, not a JSON object, missing required `data`, or larger than its configured `max_response_bytes` limit. The default limit is 1 MiB.

## Request

```json
{"command":"query","name":"login.account"}
```

## Response

```json
{"ok":true,"data":{"alias":"login.account","visible":true,"enabled":true}}
```

Failures must use a stable code:

```json
{"ok":false,"code":"NOT_FOUND","message":"widget not found","data":{"alias":"login.account"}}
```

## Commands

| Command | Parameters | Purpose |
| --- | --- | --- |
| `health` | none | Prove the test server is listening. |
| `list-aliases` | none | Return the runtime alias catalog. Python must call this before tests run. |
| `query` | `name` | Return registry metadata and runtime widget state. |
| `set-text` | `name`, `value` | Set text through the correct widget handler. |
| `get-text` | `name` | Read text through the correct widget handler. |
| `click` | `name` | Click a widget center or a named `hitTarget`. |
| `wait-idle` | `timeoutMs` | Process Qt events for a bounded interval. |

## Fail-Fast Boundary

Python owns contract validation before a UI action is sent:

| Stage | Error |
| --- | --- |
| Cannot connect to the endpoint | `E2E_CONNECTION_ERROR` |
| Endpoint returns empty, malformed, non-object, missing-data, or oversized response | `E2E_INFRA_ERROR` |
| `list-aliases` returns `ok=false` | `E2E_INFRA_ERROR` |
| Catalog payload is missing `aliases`, has non-object entries, omits `objectName`, has invalid boolean fields, or has invalid `hitTargets` | `InvalidAliasCatalog` |
| Catalog is empty | `EMPTY_ALIAS_CATALOG` |
| Test accesses an alias absent from the catalog | `UNKNOWN_ALIAS_IN_CATALOG` |

Qt owns runtime widget validation:

| Stage | Error |
| --- | --- |
| Alias exists but QWidget cannot be found | `NOT_FOUND` |
| QWidget exists but is hidden or disabled | `NOT_READY` |
| Widget type has no operation handler | `NO_HANDLER` |
| `hitTarget` is not registered for the widget | `UNKNOWN_HIT_TARGET` |
| `hitTarget` resolves outside the widget rect | `BAD_HIT_POINT` |
