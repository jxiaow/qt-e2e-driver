import pytest

from qt_e2e_driver import (
    AliasCatalog,
    DuplicateAliasError,
    EmptyAliasCatalog,
    UiAliases,
    UnknownAliasInCatalog,
)


def test_ui_namespace_returns_alias_string() -> None:
    catalog = AliasCatalog.from_payload(
        [
            {"alias": "login.account", "objectName": "inputAccount", "role": "input"},
            {"alias": "login.submit", "objectName": "apBtnLogin", "role": "button"},
        ]
    )

    ui = UiAliases(catalog)

    assert ui.login.account == "login.account"
    assert ui.login.submit == "login.submit"


def test_missing_alias_fails_when_accessed() -> None:
    catalog = AliasCatalog.from_payload(
        [{"alias": "login.account", "objectName": "inputAccount"}]
    )

    ui = UiAliases(catalog)

    with pytest.raises(UnknownAliasInCatalog, match="login.password"):
        _ = ui.login.password


def test_empty_catalog_fails_fast() -> None:
    with pytest.raises(EmptyAliasCatalog, match="empty alias catalog"):
        AliasCatalog.from_payload([])


def test_duplicate_alias_fails_fast() -> None:
    with pytest.raises(DuplicateAliasError, match="duplicate alias"):
        AliasCatalog.from_payload(
            [
                {"alias": "login.account", "objectName": "inputAccount"},
                {"alias": "login.account", "objectName": "accountEdit"},
            ]
        )


def test_hit_targets_are_normalized_from_comma_string() -> None:
    catalog = AliasCatalog.from_payload(
        [
            {
                "alias": "meeting.toolbar.mic",
                "objectName": "meetingToolbar",
                "hitTargets": "mic,camera",
            }
        ]
    )

    entry = catalog.get("meeting.toolbar.mic")

    assert entry.hit_targets == ("mic", "camera")
