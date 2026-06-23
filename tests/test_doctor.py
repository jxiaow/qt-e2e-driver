from __future__ import annotations

from pathlib import Path

from qt_e2e_driver.doctor import doctor_project
from qt_e2e_driver.doctor import doctor_endpoint


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def check_map(project: Path) -> dict[str, bool]:
    return {check.name: check.passed for check in doctor_project(project)}


def test_doctor_reports_missing_static_integration_pieces(tmp_path: Path) -> None:
    write(tmp_path / "src" / "main.cpp", "int main() { return 0; }\n")

    checks = check_map(tmp_path)

    assert checks == {
        "adapter-files": False,
        "build-gate": False,
        "run-gate": False,
        "alias-registry": False,
    }


def test_doctor_reports_present_static_integration_pieces(tmp_path: Path) -> None:
    write(tmp_path / "include" / "qt_e2e_driver" / "AliasRegistry.h", "#pragma once\n")
    write(tmp_path / "include" / "qt_e2e_driver" / "TestServer.h", "#pragma once\n")
    write(tmp_path / "src" / "qt" / "AliasRegistry.cpp", "AliasRegistry\n")
    write(tmp_path / "src" / "qt" / "TestServer.cpp", "TestServer\n")
    write(
        tmp_path / "src" / "main.cpp",
        """
        #ifdef ENABLE_TEST_SERVER
        if (QCoreApplication::arguments().contains("--test-mode")) {
            qt_e2e_driver::AliasRegistry registry;
        }
        #endif
        """,
    )

    checks = check_map(tmp_path)

    assert checks == {
        "adapter-files": True,
        "build-gate": True,
        "run-gate": True,
        "alias-registry": True,
    }


class FakeClient:
    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def load_alias_catalog(self) -> object:
        return object()


def test_doctor_endpoint_reports_health_and_alias_catalog() -> None:
    checks = {check.name: check.passed for check in doctor_endpoint(FakeClient())}

    assert checks == {
        "live-health": True,
        "live-alias-catalog": True,
    }
