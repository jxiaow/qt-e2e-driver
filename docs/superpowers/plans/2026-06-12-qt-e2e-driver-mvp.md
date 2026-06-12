# qt-e2e-driver MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone open-source-ready Qt E2E driver project with Python alias catalog handling, C++ adapter contracts, protocol docs, examples, and tests.

**Architecture:** The Qt application owns the alias registry and exposes it through `list-aliases`. The Python driver loads the registry at startup, builds a dynamic namespace, and fails fast when the catalog or a required alias is missing. The C++ adapter defines registry and `hitTarget` concepts without binding to any product repository.

**Tech Stack:** Python 3.9+, pytest, standard-library sockets and JSON, C++ Qt headers for adapter contracts.

---

### Task 1: Project Skeleton

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: `pyproject.toml`

- [x] **Step 1: Create standalone project metadata**

Define a package named `qt-e2e-driver`, Python source under `src`, tests under `tests`, and no product-specific dependencies.

- [x] **Step 2: Document initial project purpose**

Explain that the project is independent from any Qt product repository and that product apps only embed a gated adapter.

### Task 2: Python Alias Catalog

**Files:**
- Create: `src/qt_e2e_driver/errors.py`
- Create: `src/qt_e2e_driver/catalog.py`
- Create: `src/qt_e2e_driver/client.py`
- Create: `src/qt_e2e_driver/__init__.py`
- Create: `tests/test_catalog.py`

- [x] **Step 1: Define fail-fast errors**

Provide distinct exceptions for connection failure, infrastructure failure, empty catalog, and unknown aliases.

- [x] **Step 2: Implement alias catalog and dynamic namespace**

Convert `login.account` into `ui.login.account`, backed by runtime catalog data.

- [x] **Step 3: Add tests**

Cover namespace access, missing alias failure, empty catalog failure, and duplicate alias failure.

### Task 3: Qt Adapter Contract

**Files:**
- Create: `include/qt_e2e_driver/AliasRegistry.h`
- Create: `src/qt/AliasRegistry.cpp`

- [x] **Step 1: Define alias registry data model**

Represent alias, page, owner, objectName, classHint, role, hitTargets, required, deprecated, and description.

- [x] **Step 2: Define hit resolver contract**

Expose `hitPoint(widget, hitTarget)` as a coordinate resolver, not a business action invoker.

### Task 4: Docs and Examples

**Files:**
- Create: `docs/PROTOCOL.md`
- Create: `docs/ALIAS_REGISTRY.md`
- Create: `docs/QT_ADAPTER.md`
- Create: `examples/python/test_login_smoke.py`

- [x] **Step 1: Document protocol commands and errors**

Describe `health`, `list-aliases`, `query`, `set-text`, `click`, and fail-fast boundaries.

- [x] **Step 2: Document alias maintenance**

Make C++ registry the single source of truth and Python catalog loading mandatory.

- [x] **Step 3: Add pytest usage example**

Show how tests use `ui.login.account` without hard-coding objectName.

### Task 5: Verification

**Files:**
- Test: `tests/test_catalog.py`

- [x] **Step 1: Run Python tests**

Run: `python -m pytest -q`

- [x] **Step 2: Run Python syntax compile**

Run: `python -m compileall -q src tests examples`

- [x] **Step 3: Record boundary**

C++ adapter is a Qt contract skeleton and was not compiled in this environment.
