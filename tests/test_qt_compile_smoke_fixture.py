from pathlib import Path
import os
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "qt_compile_smoke"


def test_qt_compile_smoke_fixture_contains_qmake_project() -> None:
    project = (FIXTURE / "qt_compile_smoke.pro").read_text(encoding="utf-8")

    assert "ENABLE_TEST_SERVER" in project
    assert "AliasRegistry.cpp" in project
    assert "TestServer.cpp" in project
    assert "QT += core network widgets testlib" in project


def test_qt_compile_smoke_fixture_exercises_server_symbols() -> None:
    source = (FIXTURE / "main.cpp").read_text(encoding="utf-8")

    assert "SmokeDriver" in source
    assert "qt_e2e_driver::TestServer" in source
    assert "listenLocalhost(0" in source


def test_qt_compile_smoke_fixture_builds_with_qmake(tmp_path: Path) -> None:
    if os.environ.get("QT_E2E_RUN_QT_COMPILE") != "1":
        pytest.skip("set QT_E2E_RUN_QT_COMPILE=1 to run the Qt compile smoke")

    qmake = shutil.which("qmake")
    if not qmake:
        pytest.skip("qmake is not available")

    build_dir = tmp_path / "build"
    build_dir.mkdir()

    qmake_result = subprocess.run(
        [qmake, str(FIXTURE / "qt_compile_smoke.pro")],
        cwd=build_dir,
        text=True,
        capture_output=True,
    )
    if qmake_result.returncode != 0 and "Cannot run compiler" in qmake_result.stderr:
        pytest.skip(qmake_result.stderr.strip())
    qmake_result.check_returncode()

    make_tool = shutil.which("jom") or shutil.which("nmake") or shutil.which("make")
    if not make_tool:
        pytest.skip("no make tool is available")

    subprocess.run(
        [make_tool],
        cwd=build_dir,
        check=True,
        text=True,
        capture_output=True,
    )
