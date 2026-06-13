import pytest

from qt_e2e_driver import (
    AliasCatalog,
    DuplicateAliasError,
    EmptyAliasCatalog,
    InvalidAliasCatalog,
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


def test_missing_alias_error_suggests_close_match() -> None:
    catalog = AliasCatalog.from_payload(
        [
            {"alias": "login.account", "objectName": "inputAccount"},
            {"alias": "login.password", "objectName": "inputPassword"},
        ]
    )

    ui = UiAliases(catalog)

    with pytest.raises(UnknownAliasInCatalog, match="did you mean: login.password"):
        _ = ui.login.passwrod


def test_ui_namespace_dir_lists_next_alias_segments() -> None:
    catalog = AliasCatalog.from_payload(
        [
            {"alias": "login.account", "objectName": "inputAccount"},
            {"alias": "login.submit", "objectName": "apBtnLogin"},
            {"alias": "settings.audio.input", "objectName": "audioInput"},
        ]
    )

    ui = UiAliases(catalog)

    assert "login" in dir(ui)
    assert "account" in dir(ui.login)
    assert "submit" in dir(ui.login)
    assert "audio" in dir(ui.settings)


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


def test_bool_fields_normalize_common_string_values() -> None:
    catalog = AliasCatalog.from_payload(
        [
            {
                "alias": "login.account",
                "objectName": "inputAccount",
                "required": "false",
                "deprecated": "true",
            }
        ]
    )

    entry = catalog.get("login.account")

    assert entry.required is False
    assert entry.deprecated is True


def test_invalid_bool_field_fails_with_field_name() -> None:
    with pytest.raises(InvalidAliasCatalog, match="required"):
        AliasCatalog.from_payload(
            [
                {
                    "alias": "login.account",
                    "objectName": "inputAccount",
                    "required": "sometimes",
                }
            ]
        )


def test_invalid_hit_targets_field_fails_with_field_name() -> None:
    with pytest.raises(InvalidAliasCatalog, match="hitTargets"):
        AliasCatalog.from_payload(
            [
                {
                    "alias": "meeting.toolbar",
                    "objectName": "meetingToolbar",
                    "hitTargets": {"mic": "left"},
                }
            ]
        )


def test_payload_mapping_must_include_aliases() -> None:
    with pytest.raises(InvalidAliasCatalog, match="missing aliases"):
        AliasCatalog.from_payload({"items": []})


def test_alias_entry_must_be_mapping() -> None:
    with pytest.raises(InvalidAliasCatalog, match="entry 0 must be an object"):
        AliasCatalog.from_payload(["login.account"])


def test_alias_entry_requires_object_name() -> None:
    with pytest.raises(InvalidAliasCatalog, match="objectName"):
        AliasCatalog.from_payload([{"alias": "login.account"}])
