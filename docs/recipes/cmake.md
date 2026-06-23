# CMake Recipe

Use this recipe when the product project has `CMakeLists.txt`.

## Build Gate

Add an option and compile adapter files only when enabled:

```cmake
option(ENABLE_TEST_SERVER "Enable local Qt E2E test server" OFF)

if(ENABLE_TEST_SERVER)
  target_compile_definitions(my_qt_app PRIVATE ENABLE_TEST_SERVER)
  target_link_libraries(my_qt_app PRIVATE Qt::Network Qt::Test Qt::Widgets)
  target_include_directories(my_qt_app PRIVATE third_party/qt-e2e-driver/include)
  target_sources(my_qt_app PRIVATE
    third_party/qt-e2e-driver/src/qt/AliasRegistry.cpp
    third_party/qt-e2e-driver/src/qt/TestServer.cpp
  )
endif()
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

Confirm release presets leave `ENABLE_TEST_SERVER` off.
