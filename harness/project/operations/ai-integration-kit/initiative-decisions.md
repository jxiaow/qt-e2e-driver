# Decision Log

> Status date: 2026-06-23

## DEC-001 Build-System Neutral Core

- Date: 2026-06-23
- Conclusion: keep shared adapter code build-system-neutral and put qmake/CMake/Visual Studio differences in recipes.
- Reason: target product repositories may use any of the three build systems.
- Impact: no automatic build-file patcher in the first integration kit.
- Reopen condition: after multiple real integrations show stable patch patterns.

## DEC-002 JSON Alias Catalog Source Of Truth

- Date: 2026-06-23
- Conclusion: prefer `tests/e2e/aliases.json` over long hand-written C++ registry blocks.
- Reason: alias data should not bloat production builds or pollute business code.
- Impact: next implementation priority is JSON loader/generator before DefaultWidgetDriver.
- Reopen condition: if product constraints forbid runtime JSON files, generated test-only C++ remains available.

## DEC-003 Compile Smoke Is Opt-In

- Date: 2026-06-23
- Conclusion: normal `python -m pytest` must not require Qt compiler tooling.
- Reason: contributors may not have qmake/MSVC/jom configured.
- Impact: real Qt compile smoke is controlled by `QT_E2E_RUN_QT_COMPILE=1`.
- Reopen condition: dedicated CI image provides Qt tooling consistently.

## DEC-004 Native Alias, H5 Locator

- Date: 2026-06-23
- Conclusion: alias the Qt webview container, not H5 internal elements.
- Reason: H5 content may be third-party or owned by another team, so its DOM should not become this project's stable alias contract.
- Impact: future WebView support should use local locators such as text, role, testid, or css under a `client.web(ui.some.webview)` style API. `qt-e2e-driver` owns recorder/locator infrastructure; product Qt apps own webview container registration; product tests own business flow helpers; H5 owners may optionally provide stable anchors.
- Reopen condition: if a product owns the H5 and can provide stable exported test IDs, those locators may be promoted to a product-specific helper, but not to the global Qt alias catalog by default.

## DEC-005 Human Excel Case Source

- Date: 2026-06-23
- Conclusion: test cases are authored by people in Excel natural language; the framework converts them into structured IR and pytest code.
- Reason: test authors should not be forced to write YAML, Python, or a strict DSL.
- Impact: case conversion requires confidence scoring, review reports, source row mapping, and safe action vocabulary.
- Reopen condition: if teams adopt a structured case authoring format later, support it as an additional importer without removing Excel support.

## DEC-006 Reports Must Serve Humans And AI

- Date: 2026-06-23
- Conclusion: report output must include both JSON and HTML; Markdown alone is insufficient.
- Reason: humans need visual inspection/filtering, while AI needs stable structured data for repair loops.
- Impact: conversion and execution reporting should produce `report.json`/`report.html`, screenshots, traces, per-case errors, and suggested fixes.
- Reopen condition: if a downstream reporting platform becomes mandatory, keep JSON as the canonical interchange format and generate platform-specific views from it.

## DEC-007 Scripts And Skills Separation

- Date: 2026-06-23
- Conclusion: scripts perform repeatable machine work; project skills describe AI operating procedures.
- Reason: scripts should be composable and testable without AI, while skills should guide when to run them, how to interpret outputs, and when to ask for review.
- Impact: UI scanning, alias suggestions, case validation, artifact collection, and compile smoke diagnostics belong in `scripts/`; repeated AI workflows belong in `harness/project/skills/`.
- Reopen condition: if agent-harness later defines a first-class project skills convention, adapt paths while keeping the same separation.

## DEC-008 Case Conversion Provenance And Privacy

- Date: 2026-06-23
- Conclusion: generated case IR must preserve original natural-language text, source row mapping, parser version, prompt version, and review confidence.
- Reason: people write cases in Excel, but generated code must remain auditable and repairable by both humans and AI.
- Impact: ambiguous, low-confidence, or policy-sensitive steps stop at review instead of being silently guessed; external AI parsing must respect product privacy boundaries.
- Reopen condition: if teams move to a structured authoring format, keep provenance fields for imported cases and generated code.

## DEC-009 Reports And Artifacts Are Sensitive

- Date: 2026-06-23
- Conclusion: screenshots, traces, HTML reports, and structured execution JSON are treated as sensitive test artifacts by default.
- Reason: failures may capture accounts, phone numbers, orders, payment data, or other personal/business data.
- Impact: reporting work must include redaction hooks, configurable retention, artifact paths, and explicit sharing boundaries; `report.json` remains canonical for AI repair loops.
- Reopen condition: if a centralized reporting platform takes over retention/redaction, keep local JSON schema compatible with that platform.

## DEC-010 Optional Dependencies Stay Out Of The Base Package

- Date: 2026-06-23
- Conclusion: Excel and rich report features use optional dependency groups instead of making the base driver heavier.
- Reason: scanner, doctor, and adapter users should not install spreadsheet or HTML-report dependencies unless they need case conversion/reporting.
- Impact: `.csv` support remains stdlib-friendly, `.xlsx` support can use an extra such as `openpyxl`, and missing extras fail with actionable messages.
- Reopen condition: if every supported workflow requires Excel/reporting, dependency groups can be revisited.
