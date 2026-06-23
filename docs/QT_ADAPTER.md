# Qt Adapter

The adapter is embedded by the application under explicit test-only gates.

```text
Build gate: ENABLE_TEST_SERVER
Run gate:   --test-mode
Network:    localhost only
```

## Minimal Registration

```cpp
qt_e2e_driver::AliasRegistry registry;

registry.add({
    .alias = "login.account",
    .page = "login",
    .owner = "login",
    .objectName = "inputAccount",
    .classHint = "LoginInput",
    .role = "input",
    .required = true,
    .description = "Account input"
});
```

## Minimal Test Server

The repository includes a vendorable `TestServer` template:

```text
include/qt_e2e_driver/TestServer.h
src/qt/TestServer.cpp
```

Compile it only in `ENABLE_TEST_SERVER` builds. The server listens through
`listenLocalhost(...)`, which binds to `QHostAddress::LocalHost` and dispatches the
protocol commands documented in `PROTOCOL.md`.

Product code still owns widget behavior by implementing `WidgetDriver`:

```cpp
class ProductWidgetDriver : public qt_e2e_driver::WidgetDriver {
public:
    bool query(const qt_e2e_driver::AliasEntry& entry,
               QJsonObject* data,
               QString* error) override;
    bool click(const qt_e2e_driver::AliasEntry& entry, QString* error) override;
    bool setText(const qt_e2e_driver::AliasEntry& entry,
                 const QString& value,
                 QString* error) override;
    bool getText(const qt_e2e_driver::AliasEntry& entry,
                 QString* value,
                 QString* error) override;
};
```

The shared server handles JSON framing, `health`, `list-aliases`, command dispatch,
and bounded `wait-idle`. Product code handles QWidget lookup, widget-specific
operations, and detailed runtime errors such as `NOT_FOUND`, `NOT_READY`,
`NO_HANDLER`, and `UNKNOWN_HIT_TARGET`.

## Compile Smoke

The `examples/qt_compile_smoke` fixture is a tiny qmake application that compiles
`AliasRegistry.cpp` and `TestServer.cpp` together with a minimal `WidgetDriver`.
Use it after changing adapter headers or sources:

```powershell
$env:QT_E2E_RUN_QT_COMPILE = "1"
python -m pytest tests/test_qt_compile_smoke_fixture.py::test_qt_compile_smoke_fixture_builds_with_qmake -q
```

The test is skipped by default and also skips when qmake cannot run the configured
C++ compiler. On Windows with MSVC Qt kits, run it from a Visual Studio Developer
Command Prompt or an equivalent environment where `cl.exe`, qmake, and jom/nmake
are all available.

## Hit Target Resolver

Custom-painted widgets can expose named hit targets:

```cpp
class ToolbarHitResolver : public qt_e2e_driver::HitResolver {
public:
    bool hitPoint(QWidget* widget,
                  const QString& hitTarget,
                  QPoint* point,
                  QString* error) const override;
};
```

The resolver only returns a coordinate in widget-local space. It must not call product slots, emit product signals, or directly toggle business state.

Alias registry validation allows multiple hit target aliases to share one `objectName` when those aliases declare `hitTargets`. Plain widget aliases should not share `objectName`; use a hit resolver only for regions inside a custom-painted widget.

## Product Boundary

Application repositories should own:

- Which aliases exist.
- Which widgets are required for smoke tests.
- How custom widgets resolve `hitTarget` coordinates.
- When the localhost server starts.

This project owns:

- Protocol shape.
- Python client behavior.
- Alias catalog contract.
- Reusable C++ registry interfaces.
