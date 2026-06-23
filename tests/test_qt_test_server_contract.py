from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_test_server_header_exposes_product_extension_points() -> None:
    header = (ROOT / "include" / "qt_e2e_driver" / "TestServer.h").read_text(
        encoding="utf-8"
    )

    assert "class TestServer" in header
    assert "class WidgetDriver" in header
    assert "virtual bool query" in header
    assert "virtual bool click" in header
    assert "virtual bool setText" in header
    assert "virtual bool getText" in header


def test_test_server_source_declares_protocol_commands_and_localhost_boundary() -> None:
    source = (ROOT / "src" / "qt" / "TestServer.cpp").read_text(encoding="utf-8")

    for command in (
        "health",
        "list-aliases",
        "query",
        "set-text",
        "get-text",
        "click",
        "wait-idle",
    ):
        assert command in source

    assert "QTcpServer" in source
    assert "QHostAddress::LocalHost" in source
    assert "ENABLE_TEST_SERVER" in source
