# Verification Matrix

> Status date: 2026-06-23

## Verification Levels

| Level | Meaning |
| --- | --- |
| `format` | Format check |
| `lint` | Static rule check |
| `compile` | Compilation or syntax-level check |
| `test` | Unit test / contract test |
| `smoke` | Manual or semi-automated critical path verification |
| `real` | Real environment / real device integration |

## Current Records

| Work package | Scope | Level | Command / Method | Result | Uncovered items |
| --- | --- | --- | --- | --- | --- |
| AIKIT-01 | Scanner/doctor foundation | `test` | `python -m pytest tests/test_scanner.py tests/test_doctor.py -q` | pass in latest full run | Real product project variations |
| AIKIT-02 | TestServer template | `test` | `python -m pytest tests/test_qt_test_server_contract.py -q` | pass in latest full run | Real Qt compilation of all kits |
| AIKIT-03 | Playbook and recipes | `test` | `python -m pytest tests/test_docs_integration_kit.py -q` | pass in latest full run | Real user adoption feedback |
| AIKIT-04 | Compile smoke fixture | `test` | `python -m pytest tests/test_qt_compile_smoke_fixture.py -q` | pass with compile test skipped by default | Local MSVC/qmake environment did not complete real compile |
| AIKIT-05 | JSON catalog loader/generator | `test` | not run | not implemented | All behavior uncovered |
| AIKIT-13 | WebView locator driver | `test` | not run | not implemented | H5 locator behavior, QWebEngine integration, and third-party H5 risks uncovered |

## Current Verification Conclusion

- Strongest verification so far: `python -m pytest` with 42 passing tests and one expected compile-smoke skip.
- Biggest gap: no real product integration, no implemented JSON alias catalog loader, and no WebView locator driver yet.
