# qmake Recipe

Use this recipe when the product project has `.pro` or `.pri` files.

## Build Gate

Add a test-only config such as `ENABLE_TEST_SERVER`:

```qmake
contains(CONFIG, ENABLE_TEST_SERVER) {
    DEFINES += ENABLE_TEST_SERVER
    QT += network testlib widgets

    INCLUDEPATH += $$PWD/third_party/qt-e2e-driver/include
    SOURCES += $$PWD/third_party/qt-e2e-driver/src/qt/AliasRegistry.cpp
    SOURCES += $$PWD/third_party/qt-e2e-driver/src/qt/TestServer.cpp
}
```

## Runtime Gate

In `main.cpp`, start the server only when `--test-mode` is present:

```cpp
#ifdef ENABLE_TEST_SERVER
if (QCoreApplication::arguments().contains("--test-mode")) {
    startE2ETestServer(qApp);
}
#endif
```

## Checks

Run:

```powershell
qt-e2e-doctor C:\path\to\product
```

Confirm production qmake configs do not define `ENABLE_TEST_SERVER`.
