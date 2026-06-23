# Current Initiative Plan

> Status date: 2026-06-23

This initiative tracks the AI-assisted integration kit and its hardening path.

- [Hardening Design](./hardening-design.md): implementation intent, rationale, non-goals, and anti-drift notes
- [Execution Board](./initiative-board.md): single source of truth for backlog and status
- [Verification Matrix](./initiative-matrix.md): verification records for each work package
- [Decision Log](./initiative-decisions.md): decisions, deferred items, and reopen conditions

## 1. Current Conclusion

- Primary goal: let AI agents connect `qt-e2e-driver` to real Qt products with a repeatable scan, wire, verify, and harden workflow.
- Current assessment: initial scanner, doctor, TestServer template, playbook, recipes, and compile-smoke fixture exist.
- Current biggest issue: alias data should move out of hand-written product C++ and into a test-only JSON catalog source of truth.

## 2. Stage-Level Todo

### Stage 1: Integration Kit Foundation

- Goal: provide scanner, doctor, TestServer template, AI playbook, build recipes, and compile smoke fixture.
- Non-goal: fully automatic product patching.
- Completion criteria: docs and tests cover scanner/doctor/template/playbook behavior.

### Stage 2: JSON Catalog And Widget Defaults

- Goal: add JSON alias catalog loading/generation and a reusable default widget driver.
- Non-goal: cover every custom widget type.
- Completion criteria: catalog loader/generator tests pass and common Qt controls can be driven by default.

### Stage 3: Stronger Agent Feedback Loop

- Goal: expand doctor reports, alias suggestions, task prompt, failure diagnostics, and pytest fixtures.
- Non-goal: remove the need for product-specific review of aliases and custom widgets.
- Completion criteria: AI can run deterministic checks and repair common integration drift.

### Stage 4: Hybrid Native And H5 Flows

- Goal: support Qt webview containers with local H5 locators while keeping the alias catalog native-first.
- Non-goal: full browser automation or stable contracts for third-party H5 internals.
- Completion criteria: WebView locator driver design and tests distinguish native aliases from H5 locators.

## 3. Execution Order

1. Complete AIKIT-01 through AIKIT-04 foundation packages.
2. Prioritize AIKIT-05 JSON catalog loader/generator.
3. Continue with AIKIT-06 DefaultWidgetDriver and doctor improvements.
4. Add AIKIT-13 when native adapter and diagnostics are stable enough to support webview locator failures.

Current next item: determined by the highest-priority `todo / in_progress` package at the top of the [Execution Board](./initiative-board.md).

Before implementing a work package, read [Hardening Design](./hardening-design.md) and the applicable project rule in `harness/project/rules/`.
