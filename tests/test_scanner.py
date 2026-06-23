from __future__ import annotations

from pathlib import Path

from qt_e2e_driver.scanner import scan_project


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_scan_project_detects_build_files_and_entry_points(tmp_path: Path) -> None:
    write(tmp_path / "app.pro", "QT += widgets\nSOURCES += src/main.cpp\n")
    write(tmp_path / "CMakeLists.txt", "find_package(Qt6 REQUIRED COMPONENTS Widgets)\n")
    write(tmp_path / "app.sln", "Microsoft Visual Studio Solution File\n")
    write(tmp_path / "app.vcxproj", "<Project></Project>\n")
    write(tmp_path / "src" / "main.cpp", "int main(int argc, char** argv) { return 0; }\n")

    report = scan_project(tmp_path)

    assert report.root == tmp_path
    assert report.qmake_projects == (tmp_path / "app.pro",)
    assert report.cmake_projects == (tmp_path / "CMakeLists.txt",)
    assert report.visual_studio_projects == (
        tmp_path / "app.sln",
        tmp_path / "app.vcxproj",
    )
    assert report.entry_points == (tmp_path / "src" / "main.cpp",)


def test_scan_project_extracts_ui_and_source_object_names(tmp_path: Path) -> None:
    write(
        tmp_path / "forms" / "Login.ui",
        """
        <ui version="4.0">
          <widget class="QWidget" name="Login">
            <widget class="QLineEdit" name="inputAccount"/>
            <widget class="QPushButton" name="apBtnLogin"/>
          </widget>
        </ui>
        """,
    )
    write(
        tmp_path / "src" / "Login.cpp",
        """
        account->setObjectName("inputPassword");
        submit->setObjectName(QStringLiteral("apBtnSubmit"));
        """,
    )

    report = scan_project(tmp_path)

    assert report.ui_files == (tmp_path / "forms" / "Login.ui",)
    assert report.ui_object_names == ("Login", "apBtnLogin", "inputAccount")
    assert report.source_object_names == ("apBtnSubmit", "inputPassword")


def test_scan_project_ignores_common_generated_directories(tmp_path: Path) -> None:
    write(tmp_path / "build" / "ignored.pro", "QT += widgets\n")
    write(tmp_path / ".git" / "ignored.cpp", 'x->setObjectName("ignored");\n')
    write(tmp_path / "src" / "main.cpp", "int main() { return 0; }\n")

    report = scan_project(tmp_path)

    assert report.qmake_projects == ()
    assert report.source_object_names == ()
    assert report.entry_points == (tmp_path / "src" / "main.cpp",)
