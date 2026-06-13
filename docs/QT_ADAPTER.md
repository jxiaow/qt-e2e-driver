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
