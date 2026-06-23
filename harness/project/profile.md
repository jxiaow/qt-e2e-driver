# Project Profile

## Stack

- **Type**: Single Python package with vendorable Qt/C++ adapter sources.
- **Frontend**: None.
- **Backend**: None.
- **Build**: `setuptools` through `pyproject.toml`; tests run with `pytest`.
- **Runtime dependencies**: Python package has no required third-party runtime dependencies.
- **Optional tooling**: Qt/qmake/jom/MSVC may be used for adapter compile smoke; normal pytest must not require a Qt compiler.

## Repository Shape

```text
src/qt_e2e_driver/        Python client, alias catalog, scanner, doctor
include/qt_e2e_driver/    Public Qt adapter headers
src/qt/                   Vendorable Qt adapter sources
docs/                     Protocol, integration, adapter, and AI playbook docs
docs/recipes/             qmake, CMake, Visual Studio integration recipes
examples/python/          pytest usage example
examples/qt_compile_smoke/ qmake adapter compile fixture
tests/                    Python and source-contract tests
harness/core/             agent-harness submodule
harness/project/          project-specific harness profile and rules
```

## Product Chain Map

- Python protocol client: sends newline-delimited JSON commands and validates responses.
- Alias catalog contract: validates runtime alias metadata and exposes `UiAliases`.
- Qt adapter contract: exposes `AliasRegistry`, `TestServer`, and future test-only adapter helpers.
- AI integration kit: scanner, doctor, playbook, build recipes, and harness operations backlog.
- Documentation and examples: keep product integration guidance aligned with implemented behavior.

## Module Placement

| Type | Path |
| --- | --- |
| Python client behavior | `src/qt_e2e_driver/client.py` |
| Alias catalog validation | `src/qt_e2e_driver/catalog.py` |
| Scanner / doctor CLI | `src/qt_e2e_driver/scanner.py`, `src/qt_e2e_driver/doctor.py` |
| New Python CLI | `src/qt_e2e_driver/` plus `[project.scripts]` in `pyproject.toml` |
| Public Qt adapter API | `include/qt_e2e_driver/` |
| Qt adapter implementation | `src/qt/` |
| Protocol and integration docs | `docs/` |
| Build-system recipes | `docs/recipes/` |
| Python tests | `tests/test_*.py` |
| Qt compile smoke fixture | `examples/qt_compile_smoke/` |

## High-Risk Changes

- `src/qt_e2e_driver/client.py`: protocol parsing and failure semantics.
- `src/qt_e2e_driver/catalog.py`: alias validation and `UiAliases` behavior.
- `docs/PROTOCOL.md`: must stay aligned with Python client and Qt server behavior.
- `include/qt_e2e_driver/*.h` and `src/qt/*.cpp`: vendorable adapter boundary; production/test gates matter.
- `pyproject.toml`: package metadata, Python version, scripts, and pytest config.
- `docs/AI_INTEGRATION_PLAYBOOK.md` and `harness/project/operations/ai-integration-kit/`: agent-facing integration workflow and active backlog.

## Active Rules

| Rule | Applicable Scenario |
| --- | --- |
| `protocol-contract` | Any change to client requests/responses, errors, alias catalog shape, or protocol docs |
| `qt-adapter-boundary` | Any change under `include/qt_e2e_driver/`, `src/qt/`, Qt recipes, or compile smoke |
| `ai-integration-kit` | Any change to scanner, doctor, AI playbook, hardening plans, recipes, or alias catalog workflow |

## Reading Sets

| Task Type | Rules to Read |
| --- | --- |
| New feature | `ai-integration-kit` plus `protocol-contract` if protocol-facing |
| Bug fix | Relevant rule for the touched area; always read `protocol-contract` for client/catalog bugs |
| Refactor | Rule matching the refactored module plus `qt-adapter-boundary` for C++ files |
| UI adjustment | No stable UI entry point found; use standard workflow and docs only |
| Cross-module change | `protocol-contract` + `qt-adapter-boundary` + `ai-integration-kit` |

## Project Hard Constraints

- Do not make Python tests depend on raw Qt `objectName` values; tests should use stable aliases.
- Do not add Qt test server behavior to production builds; Qt adapter/server code must stay behind explicit test-only gates.
- Do not bind the Qt test server to public network interfaces; localhost-only is required.
- Do not replace JSON alias catalog direction with long hand-written business-code registry blocks.
- Keep normal `python -m pytest` independent from a configured Qt compiler; real Qt compile checks must remain opt-in or environment-gated.
- Keep protocol docs, Python client behavior, and Qt adapter behavior aligned when changing commands or failure shapes.
