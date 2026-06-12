# qt-e2e-driver

`qt-e2e-driver` is a small, framework-neutral E2E driver for Qt desktop applications.

It keeps the test runner outside the product repository while letting a Qt app expose a narrow, local-only test protocol during test builds.

## Goals

- Drive real Qt widgets from pytest without image recognition or hard-coded screen coordinates.
- Keep Python tests independent from Qt `objectName` values.
- Make widget names discoverable through a runtime alias catalog.
- Support custom-painted widgets through `hitTarget`, a named click target inside a QWidget.
- Fail fast when the test protocol or alias catalog is unavailable.

## Project Shape

```text
qt-e2e-driver/
  src/qt_e2e_driver/        Python pytest-side driver
  include/qt_e2e_driver/    C++ Qt adapter public headers
  src/qt/                   C++ Qt adapter implementation skeleton
  docs/                     Protocol and maintenance specs
  examples/python/          Example pytest usage
  tests/                    Python unit tests
```

## Core Idea

The Qt app owns the runtime alias registry:

```text
login.account
  objectName=inputAccount
  role=input
  classHint=XYLoginInputDropDownBox
  required=true
```

Python gets that registry by calling `list-aliases` at startup. Python does not maintain an `alias -> objectName` copy.

```python
from qt_e2e_driver import QtE2EClient, UiAliases

client = QtE2EClient("127.0.0.1", 19527)
catalog = client.load_alias_catalog()
ui = UiAliases(catalog)

client.set_text(ui.login.account, "alice")
client.click(ui.login.submit)
```

If `list-aliases` fails, the test session fails before any UI action runs. If an alias is missing from the catalog, accessing `ui.login.account` fails immediately.

## Qt App Boundary

The product app should only embed the C++ adapter behind explicit gates:

```text
Build gate: ENABLE_TEST_SERVER
Run gate:   --test-mode
Network:    localhost only
```

The open-source driver stays independent. A product repository only registers aliases, starts the local test server in test mode, and implements optional `hitTarget` resolvers for custom-painted widgets.

For step-by-step product integration, see [docs/INTEGRATION.md](docs/INTEGRATION.md).

## License

No license has been selected yet. Choose and add a license before publishing this repository publicly.
