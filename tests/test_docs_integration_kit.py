from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ai_integration_playbook_names_required_workflow_and_tools() -> None:
    text = (ROOT / "docs" / "AI_INTEGRATION_PLAYBOOK.md").read_text(encoding="utf-8")

    for expected in (
        "qt-e2e-scan",
        "qt-e2e-doctor",
        "ENABLE_TEST_SERVER",
        "--test-mode",
        "AliasRegistry",
        "WidgetDriver",
        "health",
        "list-aliases",
    ):
        assert expected in text


def test_build_recipes_cover_qmake_cmake_and_visual_studio() -> None:
    for recipe in ("qmake.md", "cmake.md", "visual-studio.md"):
        text = (ROOT / "docs" / "recipes" / recipe).read_text(encoding="utf-8")
        assert "ENABLE_TEST_SERVER" in text
        assert "TestServer.cpp" in text
        assert "AliasRegistry.cpp" in text


def test_readme_links_ai_integration_playbook() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "AI_INTEGRATION_PLAYBOOK.md" in text
    assert "harness/project/operations/ai-integration-kit" in text


def test_unimplemented_hardening_work_lives_in_harness_operations() -> None:
    assert not (ROOT / "docs" / "AI_INTEGRATION_HARDENING.md").exists()
    text = (
        ROOT
        / "harness"
        / "project"
        / "operations"
        / "ai-integration-kit"
        / "current-initiative.md"
    ).read_text(encoding="utf-8")
    design = (
        ROOT
        / "harness"
        / "project"
        / "operations"
        / "ai-integration-kit"
        / "hardening-design.md"
    ).read_text(encoding="utf-8")

    for expected in (
        "Hardening Design",
        "hardening-design.md",
    ):
        assert expected in text

    for expected in (
        "JSON catalog",
        "DefaultWidgetDriver",
        "Doctor As Integration Report",
        "Alias Suggestions",
        "Protocol Failure Diagnostics",
        "Standard Pytest Fixtures",
        "WebView Locator Driver",
        "H5 internal elements: local locators",
        "Final responsibility split",
        "`qt-e2e-driver`",
        "Product Qt app",
        "Product E2E tests",
        "H5 owner",
        "Excel Case Converter",
        "parser name/version",
        "Pytest mapping mechanism",
        "Privacy and retention policy",
        "Recorder-to-case relationship",
        "Optional Dependencies",
        "openpyxl",
    ):
        assert expected in design


def test_hardening_plan_covers_execution_tasks() -> None:
    text = (
        ROOT
        / "harness"
        / "project"
        / "operations"
        / "ai-integration-kit"
        / "initiative-board.md"
    ).read_text(encoding="utf-8")

    for expected in (
        "AIKIT-05",
        "Add JSON alias catalog loader/generator",
        "AIKIT-06",
        "Add DefaultWidgetDriver",
        "AIKIT-07",
        "Expand doctor static report",
        "AIKIT-08",
        "Expand doctor live report",
        "AIKIT-09",
        "Add alias suggestions",
        "AIKIT-10",
        "Add copy-ready AI task prompt",
        "AIKIT-11",
        "Add compile smoke script",
        "AIKIT-12",
        "Add diagnostics and pytest fixtures",
        "AIKIT-13",
        "Add WebView locator driver",
    ):
        assert expected in text


def test_playbook_only_documents_current_alias_registry_behavior() -> None:
    text = (ROOT / "docs" / "AI_INTEGRATION_PLAYBOOK.md").read_text(encoding="utf-8")

    assert "Build The Alias Registry" in text
    assert "buildE2EAliasRegistry" in text
    assert "loadE2EAliasRegistryFromJson" not in text
    assert "tests/e2e/aliases.json" not in text


def test_operations_decisions_cover_case_reports_privacy_and_dependencies() -> None:
    decisions = (
        ROOT
        / "harness"
        / "project"
        / "operations"
        / "ai-integration-kit"
        / "initiative-decisions.md"
    ).read_text(encoding="utf-8")
    matrix = (
        ROOT
        / "harness"
        / "project"
        / "operations"
        / "ai-integration-kit"
        / "initiative-matrix.md"
    ).read_text(encoding="utf-8")

    for expected in (
        "DEC-008 Case Conversion Provenance And Privacy",
        "DEC-009 Reports And Artifacts Are Sensitive",
        "DEC-010 Optional Dependencies Stay Out Of The Base Package",
        "parser version",
        "redaction hooks",
        "openpyxl",
    ):
        assert expected in decisions

    for expected in (
        "AIKIT-15A",
        "Conversion report",
        "AIKIT-15B",
        "Execution report core JSON",
        "AIKIT-15C",
        "HTML report and screenshots",
        "JSON schema versions",
        "privacy boundaries",
    ):
        assert expected in matrix

def test_execution_board_covers_case_reporting_scripts_and_skills() -> None:
    board = (
        ROOT
        / "harness"
        / "project"
        / "operations"
        / "ai-integration-kit"
        / "initiative-board.md"
    ).read_text(encoding="utf-8")

    for expected in (
        "AIKIT-14",
        "Add Excel case converter",
        "AIKIT-15A",
        "Add conversion report",
        "AIKIT-15B",
        "Add execution report core JSON",
        "AIKIT-15C",
        "Add HTML report and screenshots",
        "AIKIT-16",
        "Add UI scan and helper scripts",
        "AIKIT-17",
        "Add project skills for repeated E2E workflows",
    ):
        assert expected in board
