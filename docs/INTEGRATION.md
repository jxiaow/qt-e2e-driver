# Integration Guide

This guide shows how a Qt application integrates `qt-e2e-driver`.

The split is intentional:

- The product Qt app embeds a small test-only adapter.
- The standalone `qt-e2e-driver` project provides the Python driver, protocol contract, alias rules, and reusable C++ registry interfaces.

## 1. Add the Adapter to the Qt App

Copy or vendor these files into the product repository, or include them through your dependency system:

```text
include/qt_e2e_driver/AliasRegistry.h
src/qt/AliasRegistry.cpp
```

The product app should compile them only in a test build.

### qmake Example

```qmake
contains(CONFIG, ENABLE_TEST_SERVER) {
    DEFINES += ENABLE_TEST_SERVER
    QT += network testlib

    INCLUDEPATH += $$PWD/third_party/qt-e2e-driver/include
    SOURCES += $$PWD/third_party/qt-e2e-driver/src/qt/AliasRegistry.cpp
}
```

### CMake Example

```cmake
option(ENABLE_TEST_SERVER "Enable local Qt E2E test server" OFF)

if(ENABLE_TEST_SERVER)
  target_compile_definitions(my_qt_app PRIVATE ENABLE_TEST_SERVER)
  target_link_libraries(my_qt_app PRIVATE Qt::Network Qt::Test)
  target_include_directories(my_qt_app PRIVATE third_party/qt-e2e-driver/include)
  target_sources(my_qt_app PRIVATE third_party/qt-e2e-driver/src/qt/AliasRegistry.cpp)
endif()
```

## 2. Register Aliases in the Qt App

The Qt app owns the alias registry. Python never maintains `alias -> objectName`.

```cpp
#ifdef ENABLE_TEST_SERVER
#include "qt_e2e_driver/AliasRegistry.h"
#endif
```

```cpp
#ifdef ENABLE_TEST_SERVER
qt_e2e_driver::AliasRegistry buildAliasRegistry()
{
    qt_e2e_driver::AliasRegistry registry;
    QString error;

    registry.add({
        .alias = "login.account",
        .page = "login",
        .owner = "login",
        .objectName = "inputAccount",
        .classHint = "LoginInput",
        .role = "input",
        .required = true,
        .description = "Account input"
    }, &error);

    registry.add({
        .alias = "login.submit",
        .page = "login",
        .owner = "login",
        .objectName = "apBtnLogin",
        .classHint = "QPushButton",
        .role = "button",
        .required = true,
        .description = "Login submit button"
    }, &error);

    return registry;
}
#endif
```

Each alias should point to a stable `objectName` in the Qt UI. If the UI `objectName` changes, update the registry only; keep Python tests unchanged.

## 3. Start the Local Test Server

The product app must start the protocol server only when both gates are open:

```text
Build gate: ENABLE_TEST_SERVER
Run gate:   --test-mode
Network:    localhost only
```

Example startup shape:

```cpp
#ifdef ENABLE_TEST_SERVER
if (QCoreApplication::arguments().contains("--test-mode")) {
    const quint16 port = parsePortOrDefault(QCoreApplication::arguments(), 19527);
    auto* server = new TestServer(buildAliasRegistry(), qApp);
    server->listen(QHostAddress::LocalHost, port);
}
#endif
```

`TestServer` is product-side glue code. It should expose the protocol commands defined in [PROTOCOL.md](PROTOCOL.md):

```text
health
list-aliases
query
set-text
get-text
click
wait-idle
```

The reusable project defines the contract and client behavior; the product app still owns widget lookup, widget handlers, and actual Qt event execution because those pieces depend on the app's widget types.

## 4. Implement `list-aliases`

`list-aliases` returns the runtime alias registry:

```json
{
  "ok": true,
  "data": {
    "aliases": [
      {
        "alias": "login.account",
        "page": "login",
        "owner": "login",
        "objectName": "inputAccount",
        "classHint": "LoginInput",
        "role": "input",
        "required": true,
        "description": "Account input"
      }
    ]
  }
}
```

Python treats this response as the source of truth. If the command fails or returns an empty list, pytest fails before any UI operation runs.

## 5. Implement Widget Operations

Product-side command handlers should follow this boundary:

```text
query(alias)
  -> resolve alias from registry
  -> find QWidget by objectName in visible top-level windows
  -> return registry metadata + runtime widget state

set-text(alias, value)
  -> resolve alias
  -> find QWidget
  -> use the correct widget type handler
  -> process Qt events

click(alias)
  -> resolve alias
  -> find QWidget
  -> choose widget center or hitTarget point
  -> QTest::mouseClick(widget, point)
  -> process Qt events
```

Avoid direct business calls:

```text
Do not call onLoginClicked()
Do not emit clicked()
Do not call product service APIs
```

The point of E2E is to drive the real UI path.

## 6. Add `hitTarget` for Custom-Painted Widgets

Use `hitTarget` only when one QWidget contains multiple clickable regions.

```text
meeting.toolbar.mic
  objectName=meetingToolbar
  hitTarget=mic
```

The resolver returns a coordinate:

```cpp
bool ToolbarHitResolver::hitPoint(QWidget* widget,
                                  const QString& hitTarget,
                                  QPoint* point,
                                  QString* error) const
{
    if (hitTarget == "mic") {
        *point = micRect(widget).center();
        return true;
    }

    *error = QStringLiteral("unknown hitTarget %1").arg(hitTarget);
    return false;
}
```

The resolver must not call product slots. It only answers "where should a real mouse click land?"

## 7. Write Python Tests

Install the Python package from the standalone project:

```powershell
cd C:\Code\codespace\qt-e2e-driver
python -m pip install -e .[test]
```

Start the Qt app in test mode:

```powershell
my_qt_app.exe --test-mode --test-port 19527
```

Then write pytest tests:

```python
import pytest
from qt_e2e_driver import QtE2EClient, UiAliases


@pytest.fixture(scope="session")
def e2e_client():
    client = QtE2EClient("127.0.0.1", 19527)
    client.wait_until_ready(timeout=10)
    return client


@pytest.fixture(scope="session")
def ui(e2e_client):
    catalog = e2e_client.load_alias_catalog()
    return UiAliases(catalog)


def test_login_wrong_password(e2e_client, ui):
    e2e_client.set_text(ui.login.account, "bad_user")
    e2e_client.set_text(ui.login.password, "bad_password")
    e2e_client.click(ui.login.submit)
    e2e_client.wait_idle(timeout_ms=500)

    assert e2e_client.get_text(ui.login.error)
```

## 8. Expected Failure Modes

| Failure | Owner | Meaning |
| --- | --- | --- |
| `E2E_CONNECTION_ERROR` | Python/test environment | Qt app is not running, port is wrong, or server is not listening. |
| `E2E_INFRA_ERROR` | Protocol/server | `list-aliases` or another command returned `ok=false`. |
| `EMPTY_ALIAS_CATALOG` | Qt app registry | Server returned no aliases. |
| `UNKNOWN_ALIAS_IN_CATALOG` | Test/registry contract | Python requested an alias not published by `list-aliases`. |
| `NOT_FOUND` | Qt runtime | Alias exists, but the QWidget was not found. |
| `NOT_READY` | Qt runtime | Widget exists but is hidden or disabled. |
| `UNKNOWN_HIT_TARGET` | Qt hit resolver | Alias points to an internal target that the resolver does not know. |

## 9. Integration Checklist

- Build includes the adapter only with `ENABLE_TEST_SERVER`.
- Runtime starts the test server only with `--test-mode`.
- Server listens only on `127.0.0.1`.
- `list-aliases` returns every alias used by pytest.
- Python tests never use Qt `objectName`.
- Custom-painted widgets use `hitTarget`, not Python-side coordinates.
- Failure responses include alias, objectName, class name, visible/enabled state, and available candidates when possible.
