from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".pytest_cache",
    "__pycache__",
    "build",
    "cmake-build-debug",
    "cmake-build-release",
    "node_modules",
}

SOURCE_SUFFIXES = {".cpp", ".cc", ".cxx", ".h", ".hpp", ".hh"}
SET_OBJECT_NAME_RE = re.compile(
    r"setObjectName\s*\(\s*(?:QStringLiteral\s*\(\s*)?[\"']([^\"']+)[\"']"
)


@dataclass(frozen=True)
class ScanReport:
    root: Path
    qmake_projects: tuple[Path, ...]
    cmake_projects: tuple[Path, ...]
    visual_studio_projects: tuple[Path, ...]
    entry_points: tuple[Path, ...]
    ui_files: tuple[Path, ...]
    ui_object_names: tuple[str, ...]
    source_object_names: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "qmakeProjects": _stringify(self.qmake_projects),
            "cmakeProjects": _stringify(self.cmake_projects),
            "visualStudioProjects": _stringify(self.visual_studio_projects),
            "entryPoints": _stringify(self.entry_points),
            "uiFiles": _stringify(self.ui_files),
            "uiObjectNames": list(self.ui_object_names),
            "sourceObjectNames": list(self.source_object_names),
        }


def scan_project(root: str | Path) -> ScanReport:
    project_root = Path(root).resolve()
    files = tuple(_iter_project_files(project_root))

    ui_files = _sorted_paths(path for path in files if path.suffix == ".ui")
    source_files = tuple(path for path in files if path.suffix.lower() in SOURCE_SUFFIXES)

    return ScanReport(
        root=project_root,
        qmake_projects=_sorted_paths(path for path in files if path.suffix == ".pro"),
        cmake_projects=_sorted_paths(path for path in files if path.name == "CMakeLists.txt"),
        visual_studio_projects=_sorted_paths(
            path for path in files if path.suffix.lower() in {".sln", ".vcxproj"}
        ),
        entry_points=_sorted_paths(path for path in source_files if path.name == "main.cpp"),
        ui_files=ui_files,
        ui_object_names=_extract_ui_object_names(ui_files),
        source_object_names=_extract_source_object_names(source_files),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="qt-e2e-scan",
        description="Scan a Qt project for AI-assisted qt-e2e-driver integration.",
    )
    parser.add_argument("project", nargs="?", default=".", help="Qt project root")
    args = parser.parse_args(argv)

    report = scan_project(args.project)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0


def _iter_project_files(root: Path) -> Iterable[Path]:
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
            if child.is_file():
                yield child


def _extract_ui_object_names(ui_files: Iterable[Path]) -> tuple[str, ...]:
    names: set[str] = set()
    for ui_file in ui_files:
        try:
            root = ET.parse(ui_file).getroot()
        except ET.ParseError:
            continue
        for widget in root.iter("widget"):
            name = widget.attrib.get("name", "").strip()
            if name:
                names.add(name)
    return tuple(sorted(names))


def _extract_source_object_names(source_files: Iterable[Path]) -> tuple[str, ...]:
    names: set[str] = set()
    for source_file in source_files:
        text = source_file.read_text(encoding="utf-8", errors="ignore")
        names.update(match.group(1).strip() for match in SET_OBJECT_NAME_RE.finditer(text))
    return tuple(sorted(name for name in names if name))


def _sorted_paths(paths: Iterable[Path]) -> tuple[Path, ...]:
    return tuple(sorted(paths, key=lambda path: path.as_posix().lower()))


def _stringify(paths: Iterable[Path]) -> list[str]:
    return [str(path) for path in paths]


if __name__ == "__main__":
    sys.exit(main())
