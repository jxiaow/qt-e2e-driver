#include "qt_e2e_driver/TestServer.h"

#include <QApplication>
#include <QJsonObject>

class SmokeDriver : public qt_e2e_driver::WidgetDriver {
public:
    bool query(const qt_e2e_driver::AliasEntry& entry,
               QJsonObject* data,
               QString* error) override
    {
        Q_UNUSED(error);
        data->insert(QStringLiteral("alias"), entry.alias);
        data->insert(QStringLiteral("visible"), true);
        data->insert(QStringLiteral("enabled"), true);
        return true;
    }

    bool click(const qt_e2e_driver::AliasEntry& entry, QString* error) override
    {
        Q_UNUSED(entry);
        Q_UNUSED(error);
        return true;
    }

    bool setText(const qt_e2e_driver::AliasEntry& entry,
                 const QString& value,
                 QString* error) override
    {
        Q_UNUSED(entry);
        Q_UNUSED(value);
        Q_UNUSED(error);
        return true;
    }

    bool getText(const qt_e2e_driver::AliasEntry& entry,
                 QString* value,
                 QString* error) override
    {
        Q_UNUSED(entry);
        Q_UNUSED(error);
        *value = QStringLiteral("ok");
        return true;
    }
};

int main(int argc, char** argv)
{
    QApplication app(argc, argv);

    qt_e2e_driver::AliasRegistry registry;
    QString error;
    registry.add({
        QStringLiteral("smoke.button"),
        QStringLiteral("smoke"),
        QStringLiteral("smoke"),
        QStringLiteral("smokeButton"),
        QStringLiteral("QPushButton"),
        QStringLiteral("button"),
        {},
        true,
        false,
        QStringLiteral("Smoke button")
    }, &error);

    SmokeDriver driver;
    qt_e2e_driver::TestServer server(registry, &driver, &app);
    if (!server.listenLocalhost(0, &error)) {
        return 1;
    }

    server.close();
    return 0;
}
