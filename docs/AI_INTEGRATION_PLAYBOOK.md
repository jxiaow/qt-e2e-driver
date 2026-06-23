# AI Integration Playbook

This playbook is for an AI coding agent integrating `qt-e2e-driver` into an existing Qt desktop application.

The goal is a test-only local protocol server that lets pytest drive real widgets through stable aliases. This document only describes capabilities that exist in this repository today. Future hardening work is tracked in `harness/project/operations/ai-integration-kit/`.

Do not add production behavior, do not call business slots directly, and do not make Python depend on Qt `objectName` values.

## 1. Inspect The Product Project

Run:

```powershell
qt-e2e-scan C:\path\to\product
```

Use the scan output to identify:

- qmake, CMake, or Visual Studio build files.
- The application entry point, usually `main.cpp`.
- Existing `.ui` files and `objectName` values.
- Source-created widgets using `setObjectName(...)`.

Pick the matching recipe:

- `docs/recipes/qmake.md`
- `docs/recipes/cmake.md`
- `docs/recipes/visual-studio.md`

## 2. Vendor The Adapter

Copy these files into the product repository or include them through the product dependency system:

```text
include/qt_e2e_driver/AliasRegistry.h
include/qt_e2e_driver/TestServer.h
src/qt/AliasRegistry.cpp
src/qt/TestServer.cpp
```

Compile `AliasRegistry.cpp` and `TestServer.cpp` only in `ENABLE_TEST_SERVER` builds.

## 3. Add Build And Run Gates

Add a build gate:

```text
ENABLE_TEST_SERVER
```

Add a runtime gate:

```text
--test-mode
```

The server must listen only on localhost. Use `TestServer::listenLocalhost(...)`; do not bind to public interfaces.

## 4. Build The Alias Registry

The current adapter exposes an in-memory `AliasRegistry`. Build it only in test
mode and keep it outside normal business logic where possible:

```cpp
qt_e2e_driver::AliasRegistry buildE2EAliasRegistry()
{
    qt_e2e_driver::AliasRegistry registry;
    QString error;

    registry.add({
        QStringLiteral("login.account"),
        QStringLiteral("login"),
        QStringLiteral("login"),
        QStringLiteral("inputAccount"),
        QStringLiteral("QLineEdit"),
        QStringLiteral("input"),
        {},
        true,
        false,
        QStringLiteral("Login account input")
    }, &error);

    return registry;
}
```

Use stable business-facing aliases. If an `objectName` changes, update the
registry mapping instead of renaming Python tests.

## 5. Implement WidgetDriver

Implement product-specific widget operations behind `WidgetDriver`:

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

This class should find widgets by `entry.objectName`, check visibility/enabled state, and use real Qt interactions such as `QTest::mouseClick`. It should not call product slots or service APIs directly.

## 6. Start The Test Server

In the app startup path:

```cpp
#ifdef ENABLE_TEST_SERVER
if (QCoreApplication::arguments().contains("--test-mode")) {
    auto* driver = new ProductWidgetDriver(qApp);
    auto* server = new qt_e2e_driver::TestServer(buildE2EAliasRegistry(), driver, qApp);
    QString error;
    if (!server->listenLocalhost(19527, &error)) {
        qFatal("Failed to start E2E server: %s", qPrintable(error));
    }
}
#endif
```

Keep the server lifetime tied to `qApp` or another long-lived QObject.

## 7. Verify The Integration

Run the static doctor:

```powershell
qt-e2e-doctor C:\path\to\product
```

Start the product app with:

```powershell
product.exe --test-mode --test-port 19527
```

Then verify the live protocol:

```powershell
qt-e2e-doctor C:\path\to\product --host 127.0.0.1 --port 19527
```

You can also probe it from pytest or Python:

```python
from qt_e2e_driver import QtE2EClient

client = QtE2EClient("127.0.0.1", 19527)
client.wait_until_ready()
catalog = client.load_alias_catalog()
assert len(catalog) > 0
```

The first commands that must work are `health` and `list-aliases`. Only after those pass should you write smoke tests using `UiAliases`.

## 8. Write The First Smoke Test

```python
from qt_e2e_driver import QtE2EClient, UiAliases


def test_login_smoke():
    client = QtE2EClient("127.0.0.1", 19527)
    client.wait_until_ready()
    ui = UiAliases(client.load_alias_catalog())

    client.set_text(ui.login.account, "bad_user")
    client.click(ui.login.submit)
    client.wait_idle(timeout_ms=500)
```

Use smoke aliases first. Add broader UI coverage only after the server, registry, and widget driver have proven stable.

## 9. Continue Hardening

After the first integration is working, use
`harness/project/operations/ai-integration-kit/` to prioritize deeper automation:
JSON alias catalog loading, default widget handling, richer doctor reports, alias
suggestions, copy-ready AI prompts, compile smoke scripts, richer failure
diagnostics, and standard pytest fixtures.
