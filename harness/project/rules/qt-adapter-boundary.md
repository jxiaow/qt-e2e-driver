# Qt Adapter Boundary

## Goal

Keep Qt adapter code vendorable, test-only, and safe for product repositories.

## Repo Facts

- Public Qt headers live in `include/qt_e2e_driver/`.
- Qt implementation files live in `src/qt/`.
- Compile smoke fixture lives in `examples/qt_compile_smoke/`.
- Adapter docs live in `docs/QT_ADAPTER.md` and `docs/INTEGRATION.md`.
- Build recipes live in `docs/recipes/`.

## Core Rules

- Adapter code must compile only behind explicit test build gates such as `ENABLE_TEST_SERVER`.
- Server startup must also require a runtime gate such as `--test-mode`.
- Server listen behavior must stay localhost-only.
- Shared adapter code must not call product business slots, emit business signals, or bypass real UI paths.
- Product-specific widget behavior belongs behind extension points such as `WidgetDriver`.
- Normal test runs must not require Qt tooling; real Qt compile smoke is opt-in.

## Design Checklist

- Is this generic adapter behavior or product-specific glue?
- Does the API expose only what product projects need to vendor?
- Does the change increase production binary size if gates are used correctly?
- Can qmake/CMake/Visual Studio recipes still explain how to include it?

## Implementation Checklist

- Update C++ source-contract tests when public headers or server behavior changes.
- Update `examples/qt_compile_smoke/` when new adapter sources must compile together.
- Keep docs and recipes aligned with any new source/header files.
- Run `python -m pytest`; run opt-in Qt compile smoke when a configured Qt compiler is available.

## Common Smells

- Test-only alias data is added to product business files.
- Server code binds beyond localhost.
- A helper directly invokes product logic instead of UI actions.
- A regular pytest test assumes qmake, jom, MSVC, or Qt are installed.
