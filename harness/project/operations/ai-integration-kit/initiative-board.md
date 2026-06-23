# Execution Board

> Status date: 2026-06-23

This file is the single source of truth for the AI integration kit backlog and status.

## Usage Rules

- Only advance one work package to closeable state at a time.
- Before implementation, read [Hardening Design](./hardening-design.md) for rationale and non-goals.
- Work packages must have a fixed `ID`.
- Status values: `todo` / `in_progress` / `done` / `blocked` / `deferred`.
- After completion, sync [Verification Matrix](./initiative-matrix.md).
- If new architectural conclusions, deferred items, or reopen conditions arise, sync [Decision Log](./initiative-decisions.md).

## Current Execution Order

1. AIKIT-01
2. AIKIT-02
3. AIKIT-03
4. AIKIT-04
5. AIKIT-05
6. AIKIT-06
7. AIKIT-07
8. AIKIT-08
9. AIKIT-09
10. AIKIT-10
11. AIKIT-11
12. AIKIT-12
13. AIKIT-13
14. AIKIT-14
15. AIKIT-15A
16. AIKIT-15B
17. AIKIT-15C
18. AIKIT-16
19. AIKIT-17

## Work Packages

| ID | Priority | Status | Goal | Scope | Risk | Completion criteria | Dependencies | Next step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AIKIT-01 | P1 | done | Add scanner and doctor foundation | `qt-e2e-scan`, `qt-e2e-doctor`, entry points, tests | medium | Scanner/doctor tests pass | none | Done |
| AIKIT-02 | P1 | done | Add Qt TestServer template | `TestServer.h/.cpp`, docs, source-contract tests | medium | Qt contract tests pass | none | Done |
| AIKIT-03 | P1 | done | Add AI playbook and recipes | playbook, qmake/CMake/VS recipes, README links | low | Docs tests pass | AIKIT-01 | Done |
| AIKIT-04 | P2 | done | Add compile smoke fixture | qmake fixture and opt-in compile test | medium | Fixture tests pass; real compile is environment-gated | AIKIT-02 | Done |
| AIKIT-05 | P1 | todo | Add JSON alias catalog loader/generator | C++ loader, Python generator CLI, docs | medium | Loader/generator tests pass | AIKIT-01 | Start TDD |
| AIKIT-06 | P1 | todo | Add DefaultWidgetDriver | common QWidget lookup and operations | high | Contract tests pass and compile fixture includes driver | AIKIT-02, AIKIT-05 | Write contract tests |
| AIKIT-07 | P2 | todo | Expand doctor static report | localhost boundary, production gate risk, JSON catalog validation | medium | Doctor tests pass | AIKIT-05 | Write tests |
| AIKIT-08 | P2 | todo | Expand doctor live report | alias counts, required/deprecated counts, duplicate objectName risks | medium | Doctor endpoint tests pass | AIKIT-07 | Write tests |
| AIKIT-09 | P2 | todo | Add alias suggestions | scanner draft aliases from `.ui` and `setObjectName` | medium | Scanner suggestion tests pass | AIKIT-05 | Write tests |
| AIKIT-10 | P3 | todo | Add copy-ready AI task prompt | `docs/prompts/integrate-qt-e2e-driver.md` | low | Docs tests pass | AIKIT-03 | Write docs test |
| AIKIT-11 | P3 | todo | Add compile smoke script | PowerShell script for qmake compiler diagnostics | medium | Script tests pass | AIKIT-04 | Write tests |
| AIKIT-12 | P3 | todo | Add diagnostics and pytest fixtures | richer protocol failure data and reusable pytest fixtures | medium | Contract/plugin tests pass | AIKIT-06, AIKIT-08 | Split if too large |
| AIKIT-13 | P3 | todo | Add WebView locator driver | Alias only the Qt webview container; use local H5 locators for text/role/testid/css actions | high | Web locator tests pass and docs mark third-party H5 risk | AIKIT-06, AIKIT-08 | Write protocol/API design tests |
| AIKIT-14 | P2 | todo | Add Excel case converter | Read human-authored Excel natural-language cases, produce structured IR, review report, and generated pytest | high | Converter tests cover xlsx/csv import, optional dependency errors, AI parser provenance, ambiguous-step review, and pytest generation | AIKIT-05, AIKIT-09, AIKIT-13 | Write IR and conversion-report tests |
| AIKIT-15A | P2 | todo | Add conversion report | Emit JSON/HTML report for Excel-to-IR-to-pytest conversion, including review-needed steps and confidence | high | Conversion report tests verify schema, source row mapping, and review items | AIKIT-14 | Write conversion report tests |
| AIKIT-15B | P2 | todo | Add execution report core JSON | Emit structured execution report with case/step mapping, error context, traces, and artifact paths | high | Execution JSON tests verify failures map to caseId/sheet/row/step | AIKIT-12, AIKIT-14 | Write execution report schema tests |
| AIKIT-15C | P2 | todo | Add HTML report and screenshots | Render human HTML report with filters, inline screenshots, trace links, redaction hooks, and suggested fixes | high | HTML/screenshot tests verify links, redaction markers, and failure summaries | AIKIT-15B | Write renderer tests |
| AIKIT-16 | P2 | todo | Add UI scan and helper scripts | Add scripts for Qt UI scanning, alias suggestions, case IR validation, artifact collection, and compile smoke diagnostics | medium | Script tests verify inputs/outputs, exit codes, JSON schema versions, and no source files are silently modified | AIKIT-05, AIKIT-09, AIKIT-15B | Write script behavior tests |
| AIKIT-17 | P2 | todo | Add project skills for repeated E2E workflows | Add project skills for scan/alias, Excel case conversion, failure debugging, and WebView locator recording | low | Harness checks pass and skills reference scripts, reports, privacy boundaries, review gates, and common mistakes | AIKIT-16 | Write skills content tests |

## Current Work Package Details

### AIKIT-05

- Goal: make `tests/e2e/aliases.json` the preferred source of truth for product integrations.
- Not doing this round: automatic product build-file patching.
- Current progress: documented and planned; implementation not started.
