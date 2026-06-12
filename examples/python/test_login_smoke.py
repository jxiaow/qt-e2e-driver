import os

import pytest

from qt_e2e_driver import QtE2EClient, UiAliases


@pytest.fixture(scope="session")
def e2e_client() -> QtE2EClient:
    port = int(os.environ.get("QT_E2E_PORT", "19527"))
    return QtE2EClient("127.0.0.1", port)


@pytest.fixture(scope="session")
def ui(e2e_client: QtE2EClient) -> UiAliases:
    catalog = e2e_client.load_alias_catalog()
    return UiAliases(catalog)


def test_wrong_password_shows_error(e2e_client: QtE2EClient, ui: UiAliases) -> None:
    e2e_client.set_text(ui.login.account, "bad_user")
    e2e_client.set_text(ui.login.password, "bad_password")
    e2e_client.click(ui.login.submit)

    error_text = e2e_client.get_text(ui.login.error)

    assert error_text
