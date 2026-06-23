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
