# AI Integration Kit Hardening Design

> Status date: 2026-06-23
>
> This is an operations design document, not public product documentation. It describes planned and partially implemented work. Do not treat any item here as available until the execution board marks its work package done and tests verify it.

## 1. Purpose

The integration kit should help an AI coding agent connect `qt-e2e-driver` to real Qt desktop products without guessing architecture, polluting production code, or claiming unverified integration success.

The current usable foundation includes:

- `qt-e2e-scan` for project discovery.
- `qt-e2e-doctor` for basic static checks and optional live `health` / `list-aliases` checks.
- A vendorable `AliasRegistry` and `TestServer` template.
- qmake/CMake/Visual Studio recipes.
- An AI playbook that documents only implemented behavior.

The hardening work below is the intended next shape.

## 2. Core Direction

Do not put large hand-written alias registries into product business files.

The desired future model is:

```text
product/
  src/
    main.cpp
    e2e/
      E2ETestServerBootstrap.cpp
      E2EAliasRegistry.cpp      # optional generated test-only file
  tests/
    e2e/
      aliases.json              # preferred source of truth
```

`tests/e2e/aliases.json` should become the preferred alias source of truth. The Qt app loads this file into `AliasRegistry` only when both gates are open:

```text
Build gate: ENABLE_TEST_SERVER
Run gate:   --test-mode
```

For hermetic CI builds or products that cannot load external test resources, the same JSON catalog may be converted into a generated test-only C++ file.

This preserves the important testing contract: Python tests use stable aliases and never raw Qt `objectName` values.

## 3. Planned Work Areas

### 3.1 JSON Alias Catalog Loader And Generator

Add C++ and Python support for JSON alias catalogs.

Expected behavior:

- C++ can parse a JSON catalog into `AliasRegistry`.
- Python can validate the same JSON using `AliasCatalog`.
- A CLI can generate deterministic test-only C++ from JSON when needed.
- Malformed catalogs fail before any UI action runs.

Preferred JSON shape:

```json
{
  "aliases": [
    {
      "alias": "login.account",
      "objectName": "inputAccount",
      "page": "login",
      "owner": "login",
      "classHint": "QLineEdit",
      "role": "input",
      "required": true,
      "description": "Login account input"
    }
  ]
}
```

Non-goals:

- Do not automatically rewrite product build files in this step.
- Do not silently infer final business aliases without review.
- Do not make production builds carry alias data.

### 3.2 DefaultWidgetDriver

Add a reusable Qt-side `DefaultWidgetDriver`.

It should:

- Find widgets by `AliasEntry::objectName` across visible top-level windows.
- Check visibility and enabled state before acting.
- Return consistent runtime errors such as `NOT_FOUND`, `NOT_READY`, and `NO_HANDLER`.
- Support common controls:
  - `QLineEdit`, `QTextEdit`, `QPlainTextEdit` for `setText` and `getText`.
  - `QAbstractButton` for `click`.
  - `QLabel` for `getText`.
- Use real UI paths such as `QTest::mouseClick` where appropriate.
- Allow products to wrap or replace behavior for custom widgets and hit targets.

Non-goals:

- Do not call product slots directly.
- Do not emit business signals directly.
- Do not claim support for every custom widget.

### 3.3 Doctor As Integration Report

Expand `qt-e2e-doctor` from marker checks into a repair-oriented report.

Static checks should include:

- Adapter files are present.
- `ENABLE_TEST_SERVER` exists.
- `--test-mode` exists.
- Server startup is localhost-only.
- JSON alias catalog exists and validates when the project uses catalog loading.
- Obvious production config leakage is flagged when detectable.

Live checks should include:

- `health` succeeds.
- `list-aliases` succeeds.
- Alias count.
- Required alias count.
- Deprecated alias count.
- Risky duplicate `objectName` mappings where visible from the catalog.

Output should remain deterministic enough for AI repair loops:

```text
run doctor -> read failing check -> patch -> rerun doctor
```

### 3.4 Alias Suggestions

Extend scanner output with opt-in alias suggestions.

Suggested command shape:

```powershell
qt-e2e-scan C:\path\to\product --suggest-aliases
```

Expected behavior:

- Read `.ui` filenames and widget names.
- Read source-created `setObjectName(...)` values.
- Produce draft aliases with confidence.
- Never directly patch product code.

Examples:

| Source | Draft Alias |
| --- | --- |
| `Login.ui` + `inputAccount` | `login.account` |
| `Settings.ui` + `checkAutoStart` | `settings.autoStart` |
| `Login.ui` + `btnLogin` | low-confidence `login.login` or `login.submit` |

The output is a review aid, not a final authority. A human or project owner should approve business alias names.

### 3.5 AI Task Prompt

Add a copy-ready prompt for agents under `docs/prompts/` once the described workflow is implemented.

It should instruct the AI to:

- Run `qt-e2e-scan`.
- Pick the matching qmake/CMake/Visual Studio recipe.
- Add test-only gates.
- Use alias catalog data, not raw object names in Python.
- Run `qt-e2e-doctor`.
- Write one smoke pytest.
- Report registered aliases and remaining gaps.

Do not publish a prompt that asks agents to use unavailable JSON loader/generator behavior before those pieces exist.

### 3.6 Compile Smoke Script

Add a script such as:

```text
scripts/qt_compile_smoke.ps1
```

It should accept:

- Qt bin path.
- Visual Studio developer command path on Windows.
- Architecture.
- Build directory.

It should diagnose:

- Missing `qmake`.
- Missing C++ compiler.
- Missing `jom`, `nmake`, or `make`.
- qmake generation failures.
- adapter compile failures.

The pytest compile smoke remains opt-in. The script is for local/CI environments that want stronger Qt compilation verification.

### 3.7 Protocol Failure Diagnostics

Standardize richer failure data from Qt-side runtime operations.

Recommended failure shape:

```json
{
  "ok": false,
  "code": "NOT_FOUND",
  "message": "widget not found",
  "data": {
    "alias": "login.account",
    "objectName": "inputAccount",
    "classHint": "QLineEdit",
    "visible": false,
    "enabled": false,
    "availableCandidates": ["inputUser", "inputPassword"]
  }
}
```

Purpose:

- Help humans identify alias drift.
- Help AI distinguish object lookup failures from readiness failures.
- Keep failures close to the real integration cause.

### 3.8 Standard Pytest Fixtures

Add reusable pytest fixtures when the protocol and doctor behavior are stable.

Potential fixtures:

- `qt_e2e_client`
- `qt_e2e_catalog`
- `qt_ui`

Configuration:

- `QT_E2E_HOST`
- `QT_E2E_PORT`
- `QT_E2E_TIMEOUT`

The fixtures should reduce smoke-test boilerplate without hiding connection or catalog failures.

### 3.9 WebView Locator Driver

Support Qt applications that embed H5 content through widgets such as `QWebEngineView`.

Core boundary:

```text
Qt native controls: stable aliases
H5 internal elements: local locators
```

Only the Qt webview container should be part of the alias catalog:

```python
ui.payment.webview
```

Elements inside the H5 page should not become global aliases, especially when the H5 page is third-party or owned by another team. Tests should use local locators instead:

```python
web = client.web(ui.payment.webview)

web.click_text("Submit")
web.click_role("button", name="Submit")
web.click_testid("submit-payment")
web.click_css("button[type=submit]")
```

Planned protocol shape:

```json
{
  "command": "web-click",
  "name": "payment.webview",
  "locator": {
    "type": "text",
    "value": "Submit"
  }
}
```

Locator types should be explicit:

- `testid`: preferred when the H5 owner can provide stable test anchors.
- `role`: preferred when accessible role/name are stable.
- `text`: useful but language and copy changes can break it.
- `css`: escape hatch; usually the most brittle.

Default matching should be strict:

- zero matches -> `WEB_NOT_FOUND`
- multiple matches -> `WEB_MULTIPLE_MATCHES`
- hidden element -> `WEB_NOT_VISIBLE`
- JavaScript timeout -> `WEB_TIMEOUT`

Qt-side behavior:

- Find the webview by its Qt alias and `objectName`.
- Execute JavaScript inside the webview main frame.
- Return structured web failure codes.
- Do not store H5 locators in `AliasCatalog`.

Non-goals:

- Do not claim stability for third-party H5 DOM structures.
- Do not support complex cross-origin iframe automation as a first-class feature.
- Do not replace Playwright or the H5 team's own tests for full web application coverage.

Recommended testing posture:

- For third-party H5, prefer integration checks: webview visible, URL/host, load finished, callback/bridge result.
- Use locators only when the product flow genuinely requires clicking or reading an internal H5 element.
- Treat locator-based H5 tests as more brittle than native alias tests.

Final responsibility split:

| Owner | Responsibility |
| --- | --- |
| `qt-e2e-driver` | Provide WebView recorder, locator execution protocol, Python WebView API, Qt `QWebEngineView` driver, locator failure codes, and recorder output format. |
| Product Qt app | Register only the Qt webview container alias, set or expose a stable `objectName`, and wire the shared WebView driver or a resolver for custom wrapper widgets. |
| Product E2E tests | Own business flow helpers such as `PaymentWebFlow`; helpers may compose locators but should live in the product test suite, not this shared library. |
| H5 owner | Optionally provide stable `data-testid`, accessible role/name, or other test anchors; this is helpful but not required for basic recorder/locator usage. |

The shared library must not contain product-specific flows. A future generic API may look like:

```python
web = client.web(ui.payment.webview)
web.click_role("button", name="Submit")
```

Product tests may wrap it:

```python
class PaymentWebFlow:
    def __init__(self, web):
        self.web = web

    def submit(self):
        self.web.click_role("button", name="Submit")
```

This keeps the stable Qt boundary in the alias catalog while allowing H5 interactions without turning third-party DOM details into project-wide aliases.

## 4. Implementation Order

Follow the execution board. The current intended order is:

1. JSON alias catalog loader/generator.
2. DefaultWidgetDriver.
3. Doctor static report expansion.
4. Doctor live report expansion.
5. Alias suggestions.
6. AI task prompt.
7. Compile smoke script.
8. Failure diagnostics and pytest fixtures.
9. WebView locator driver.

If implementation uncovers a dependency conflict, update `initiative-board.md` and `initiative-decisions.md` before proceeding.

## 5. Verification Expectations

Every work package should have:

- Failing tests first.
- Targeted tests passing.
- Full `python -m pytest` passing.
- Harness checks passing when Markdown operations or rules change.
- Real Qt compile smoke when a configured Qt compiler environment is available.

If real Qt compile is skipped, record the reason in `initiative-matrix.md`.

## 6. Anti-Drift Notes

- `docs/` should describe implemented behavior only.
- Future plans belong in this operations directory.
- Do not move this file back to `docs/` until every described capability is implemented or clearly split into implemented docs.
- Do not compress this design down to only the board table; the rationale and non-goals here are part of the implementation contract.
