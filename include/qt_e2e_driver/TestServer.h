#pragma once

#include "qt_e2e_driver/AliasRegistry.h"

#include <QJsonObject>
#include <QObject>
#include <QTcpServer>

class QTcpSocket;

namespace qt_e2e_driver {

class WidgetDriver {
public:
    virtual ~WidgetDriver() = default;

    virtual bool query(const AliasEntry& entry, QJsonObject* data, QString* error) = 0;
    virtual bool click(const AliasEntry& entry, QString* error) = 0;
    virtual bool setText(const AliasEntry& entry, const QString& value, QString* error) = 0;
    virtual bool getText(const AliasEntry& entry, QString* value, QString* error) = 0;
};

class TestServer : public QObject {
public:
    explicit TestServer(AliasRegistry registry, WidgetDriver* driver, QObject* parent = nullptr);

    bool listenLocalhost(quint16 port, QString* error = nullptr);
    void close();

private:
    void handleNewConnection();
    void handleSocketReady(QTcpSocket* socket);
    QJsonObject handleRequest(const QJsonObject& request);
    QJsonObject handleHealth() const;
    QJsonObject handleListAliases() const;
    QJsonObject handleQuery(const QJsonObject& request);
    QJsonObject handleClick(const QJsonObject& request);
    QJsonObject handleSetText(const QJsonObject& request);
    QJsonObject handleGetText(const QJsonObject& request);
    QJsonObject handleWaitIdle(const QJsonObject& request);
    QJsonObject aliasToJson(const AliasEntry& entry) const;
    QJsonObject ok(const QJsonObject& data) const;
    QJsonObject fail(const QString& code, const QString& message) const;

    AliasRegistry registry_;
    WidgetDriver* driver_ = nullptr;
    QTcpServer server_;
};

} // namespace qt_e2e_driver
