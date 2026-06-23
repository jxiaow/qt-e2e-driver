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

### 3.10 Excel Case Converter

Test cases are authored by people in Excel using natural language. The framework should not require test authors to write YAML, Python, or a strict DSL.

Target flow:

```text
Excel natural-language case
  -> importer reads xlsx/csv
  -> AI/parser converts steps to structured IR
  -> resolver maps native targets to aliases and H5 steps to local locators
  -> low-confidence steps go to review
  -> generator emits pytest code
```

The source Excel can contain columns such as case ID, title, preconditions, steps, and expected result. The converter must preserve source file, sheet, row, original step text, parsed action, and confidence. If an LLM is used for natural-language parsing, the IR must also record parser name/version, prompt version, and enough provenance for review.

Low-confidence, ambiguous, or policy-sensitive steps must not be silently guessed. They should produce review items with reason codes such as `AMBIGUOUS_TARGET`, `UNKNOWN_ALIAS`, or `UNSUPPORTED_ACTION`.

Supported action vocabulary should start small and explicit:

- Native: `click`, `set_text`, `wait_text`, `wait_visible`, `wait_enabled`, `wait_idle`.
- WebView: `web.click_text`, `web.click_role`, `web.click_testid`, `web.click_css`, `web.set_text_css`, `web.wait_text`, `web.wait_url`.
- Assertions: `assert_text`, `assert_visible`, `assert_url_contains`.

Converter responsibilities:

- Read `.xlsx` and `.csv`.
- Preserve case ID, sheet name, row number, and original step text.
- Reject arbitrary Python injection.
- Reject raw Qt `objectName` targets.
- Emit structured IR before pytest code.
- Emit review reports for ambiguous or low-confidence steps.
- Keep the original natural-language text beside every parsed action.
- Make generated output reproducible enough for review by recording parser and prompt versions.
- Respect project privacy boundaries before sending Excel case text to an external model.

Non-goals:

- Do not require test authors to write a DSL.
- Do not claim fully automatic conversion for every natural-language sentence.
- Do not execute low-confidence parsed steps without review.
- Do not send sensitive case data to external AI services unless the product team explicitly allows it.

### 3.11 Dual-Format E2E Reports

Generated reports must serve two readers:

```text
Humans: inspect, filter, understand screenshots and failures
AI/tools: parse structured data and continue repair
```

Markdown alone is not enough. The primary outputs should be `report.json` and `report.html`.

There are two report phases:

- Conversion report: shows generated cases, review-needed cases, ambiguous targets, unknown aliases, unsupported actions, and low-confidence parsing.
- Execution report: maps pass/fail results back to source case, Excel sheet, row, and step; attaches screenshots, protocol traces, and structured errors.

Suggested artifact layout:

```text
artifacts/<run-id>/
  report.json
  report.html
  cases/
    payment_001.json
  errors/
    payment_001_step_2.json
  screenshots/
    payment_001_step_2.png
  traces/
    payment_001.protocol.jsonl
  generated/
    test_payment_001.py
  source/
    cases.xlsx
```

HTML report requirements:

- Summary counts: total, generated, needs review, passed, failed.
- Filters by sheet, case ID, status, and error code.
- Expandable case details.
- Original natural-language step text.
- Parsed action and confidence.
- Failed step highlighted.
- Screenshot displayed inline.
- Links to protocol traces and generated pytest code.
- Suggested fixes shown in human-readable form.

JSON report requirements:

- Stable schema version.
- Source file/sheet/row mapping.
- Case ID and step index mapping.
- Parsed IR.
- Execution status.
- Error code/message/phase.
- Artifact relative paths.
- Suggested fixes structured enough for an AI to act on.

Pytest mapping mechanism:

- Generated tests should embed `caseId`, source file, sheet, row, and step index metadata.
- Step helpers should write trace entries before and after each action.
- Exceptions should be captured with the active step context.
- Protocol errors, assertion failures, and conversion errors should map back to the same case/step model.

Privacy and retention policy:

- Screenshots and traces may contain account, phone, order, payment, or personal data.
- Reporting must support masking or redaction before artifacts are shared outside the test environment.
- Artifact retention should be configurable.
- `report.html` should be considered sensitive unless generated with redaction enabled.
- Protocol traces should avoid storing raw secret values where possible.

Screenshot policy:

- Native failure: capture the main window; optionally highlight the widget if geometry is known.
- H5 failure: capture the main window and the webview region when possible.
- If a candidate element exists but is hidden, include locator context and optional highlight geometry.
- If no element is found, still capture URL, title, screenshot, and trace.

Failure code families:

- Conversion: `CASE_PARSE_ERROR`, `AMBIGUOUS_TARGET`, `UNKNOWN_ALIAS`, `UNSUPPORTED_ACTION`.
- Execution native: `E2E_CONNECTION_ERROR`, `NOT_FOUND`, `NOT_READY`, `NO_HANDLER`, `ASSERTION_FAILED`.
- Execution web: `WEB_NOT_FOUND`, `WEB_MULTIPLE_MATCHES`, `WEB_NOT_VISIBLE`, `WEB_TIMEOUT`, `WEB_JS_ERROR`.

Principle:

```text
A failure report must answer:
- Which case failed?
- Which Excel row and step failed?
- What was the original natural-language step?
- What did it parse into?
- What exact error occurred?
- What did the UI look like?
- What should a human or AI try next?
```
### 3.12 Automation Scripts And Project Skills

Some repeated work should be automated as scripts, while AI-specific operating procedures should live as project skills.

Use this separation:

```text
scripts = executable tools for repeatable machine work
skills = AI operating procedures for when and how to use the tools
rules = constraints and boundaries
operations = future work and progress tracking
docs = implemented public behavior only
```

Recommended scripts:

Every script should document input files, output files, exit codes, whether it may modify source files, and JSON schema version for machine-readable outputs.

| Script | Purpose |
| --- | --- |
| `scripts/scan_qt_ui.py` | Scan `.ui` files, `setObjectName(...)`, likely entry points, `QWebEngineView`, and existing alias data; output structured JSON. |
| `scripts/suggest_aliases.py` | Convert scan results into draft alias suggestions with confidence and reasons. |
| `scripts/validate_cases.py` | Validate Excel-converted IR for missing targets, unknown aliases, low confidence, and unsupported actions. |
| `scripts/collect_artifacts.py` | Collect screenshots, traces, generated tests, source cases, and report files into a stable run directory. |
| `scripts/qt_compile_smoke.ps1` | Configure Qt/MSVC build environment and run adapter compile smoke with clear diagnostics. |

Recommended project skills:

| Skill | Purpose |
| --- | --- |
| `harness/project/skills/scan-ui-and-aliases.md` | Teach AI how to scan a product UI, read scan output, create alias suggestions, and avoid silently confirming aliases. |
| `harness/project/skills/convert-excel-cases.md` | Teach AI how to convert Excel natural-language cases into IR, review low-confidence steps, and generate pytest. |
| `harness/project/skills/debug-e2e-failure.md` | Teach AI how to read `report.json`, screenshots, traces, and structured errors to decide the next repair. |
| `harness/project/skills/webview-locator-recording.md` | Teach AI and humans how to record H5 locators and choose among `testid`, `role`, `text`, and `css`. |

Scripts should be usable without an AI. Skills should not duplicate script implementation details; they should describe workflow, inputs, outputs, review gates, and common mistakes.

Example workflow:

```text
AI reads scan-ui-and-aliases skill
  -> runs scan_qt_ui.py
  -> reviews scan-report.json
  -> runs suggest_aliases.py
  -> produces alias-suggestions.json/html
  -> asks for review only on low-confidence or business-semantic decisions
```


Recorder-to-case relationship:

- WebView recorder outputs locator candidates with confidence and evidence.
- Case conversion may reference recorder candidates when a natural-language H5 step is low confidence.
- A human or AI review step chooses the locator before executable pytest is generated.
- Recorder output should not directly rewrite Excel or product code without explicit confirmation.

Non-goals:

- Do not make scripts silently edit product source files.
- Do not put project-specific business flows in shared scripts.
- Do not treat skills as verified product documentation.

### 3.13 Optional Dependencies

The base Python package should remain lightweight. Features that need extra dependencies should use optional extras.

Planned dependency policy:

- `.csv` import should use the Python standard library.
- `.xlsx` import should use an optional dependency such as `openpyxl` under an extra like `case`.
- HTML reporting should prefer stdlib rendering first; richer renderers must be optional.
- Missing optional dependencies should fail with actionable messages, not break the core client.

Example future install shapes:

```text
pip install -e .[test]
pip install -e .[case]
pip install -e .[report]
```

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
10. Excel case converter.
11. Dual-format E2E reports.
12. Automation scripts for repeatable UI/case/report work.
13. Project skills for repeated AI E2E workflows.
14. Optional dependency policy for Excel/report features.

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
