# Visual Studio Recipe

Use this recipe when the product project has `.sln` or `.vcxproj` files.

## Build Gate

Create a dedicated test configuration or property sheet. In that configuration:

- Add `ENABLE_TEST_SERVER` to preprocessor definitions.
- Add `third_party\qt-e2e-driver\include` to include directories.
- Add Qt Network, Test, and Widgets libraries as required by the local Qt setup.
- Add these source files to the project:

```text
third_party\qt-e2e-driver\src\qt\AliasRegistry.cpp
third_party\qt-e2e-driver\src\qt\TestServer.cpp
```

Do not add `ENABLE_TEST_SERVER` to production configurations.

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

Inspect the `.vcxproj` or test property sheet to confirm only the test configuration defines `ENABLE_TEST_SERVER`.
