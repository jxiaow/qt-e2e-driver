from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .client import QtE2EClient
from .errors import QtE2EError
from .scanner import IGNORED_DIRS


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    passed: bool
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
        }


def doctor_project(root: str | Path) -> tuple[DoctorCheck, ...]:
    project_root = Path(root).resolve()
    files = tuple(_iter_text_files(project_root))
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in files)

    return (
        _adapter_files_check(project_root),
        DoctorCheck(
            "build-gate",
            "ENABLE_TEST_SERVER" in text,
            "Found ENABLE_TEST_SERVER build gate."
            if "ENABLE_TEST_SERVER" in text
            else "Missing ENABLE_TEST_SERVER build gate.",
        ),
        DoctorCheck(
            "run-gate",
            "--test-mode" in text,
            "Found --test-mode runtime gate."
            if "--test-mode" in text
            else "Missing --test-mode runtime gate.",
        ),
        DoctorCheck(
            "alias-registry",
            "AliasRegistry" in text,
            "Found AliasRegistry usage."
            if "AliasRegistry" in text
            else "Missing AliasRegistry usage.",
        ),
    )


def doctor_endpoint(client: object) -> tuple[DoctorCheck, ...]:
    checks: list[DoctorCheck] = []

    try:
        health = client.health()  # type: ignore[attr-defined]
        checks.append(
            DoctorCheck("live-health", True, f"health returned {health!r}.")
        )
    except (OSError, QtE2EError, AttributeError) as exc:
        checks.append(DoctorCheck("live-health", False, str(exc)))
        checks.append(DoctorCheck("live-alias-catalog", False, "Skipped after health failed."))
        return tuple(checks)

    try:
        client.load_alias_catalog()  # type: ignore[attr-defined]
        checks.append(DoctorCheck("live-alias-catalog", True, "Loaded alias catalog."))
    except (OSError, QtE2EError, AttributeError) as exc:
        checks.append(DoctorCheck("live-alias-catalog", False, str(exc)))

    return tuple(checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="qt-e2e-doctor",
        description="Check static qt-e2e-driver integration markers in a Qt project.",
    )
    parser.add_argument("project", nargs="?", default=".", help="Qt project root")
    parser.add_argument("--host", help="Live test server host, usually 127.0.0.1")
    parser.add_argument("--port", type=int, default=19527, help="Live test server port")
    args = parser.parse_args(argv)

    checks = list(doctor_project(args.project))
    if args.host:
        checks.extend(doctor_endpoint(QtE2EClient(args.host, args.port)))
    print(json.dumps([check.to_dict() for check in checks], indent=2, sort_keys=True))
    return 0 if all(check.passed for check in checks) else 1


def _adapter_files_check(root: Path) -> DoctorCheck:
    required = (
        root / "include" / "qt_e2e_driver" / "AliasRegistry.h",
        root / "include" / "qt_e2e_driver" / "TestServer.h",
        root / "src" / "qt" / "AliasRegistry.cpp",
        root / "src" / "qt" / "TestServer.cpp",
    )
    missing = tuple(path for path in required if not path.exists())
    if missing:
        relative = ", ".join(str(path.relative_to(root)) for path in missing)
        return DoctorCheck("adapter-files", False, f"Missing adapter files: {relative}")
    return DoctorCheck("adapter-files", True, "Found vendored adapter files.")


def _iter_text_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        raise FileNotFoundError(root)

    stack = [root]
    while stack:
        current = stack.pop()
        for child in current.iterdir():
            if child.is_dir():
                if child.name not in IGNORED_DIRS:
                    stack.append(child)
                continue
            if child.is_file() and child.suffix.lower() in {
                ".cpp",
                ".cc",
                ".cxx",
                ".h",
                ".hpp",
                ".pro",
                ".pri",
                ".cmake",
                ".txt",
                ".vcxproj",
            }:
                yield child


if __name__ == "__main__":
    sys.exit(main())
