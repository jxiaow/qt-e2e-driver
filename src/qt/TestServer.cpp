#ifdef ENABLE_TEST_SERVER

#include "qt_e2e_driver/TestServer.h"

#include <QCoreApplication>
#include <QEventLoop>
#include <QHostAddress>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTcpServer>
#include <QTcpSocket>

namespace qt_e2e_driver {

TestServer::TestServer(AliasRegistry registry, WidgetDriver* driver, QObject* parent)
    : QObject(parent)
    , registry_(registry)
    , driver_(driver)
{
    QObject::connect(&server_, &QTcpServer::newConnection, [this]() {
        handleNewConnection();
    });
}

bool TestServer::listenLocalhost(quint16 port, QString* error)
{
    if (!driver_) {
        if (error) {
            *error = QStringLiteral("WidgetDriver must not be null");
        }
        return false;
    }

    if (!server_.listen(QHostAddress::LocalHost, port)) {
        if (error) {
            *error = server_.errorString();
        }
        return false;
    }

    return true;
}

void TestServer::close()
{
    server_.close();
}

void TestServer::handleNewConnection()
{
    while (QTcpSocket* socket = server_.nextPendingConnection()) {
        socket->setParent(this);
        QObject::connect(socket, &QTcpSocket::readyRead, [this, socket]() {
            handleSocketReady(socket);
        });
        QObject::connect(socket, &QTcpSocket::disconnected, socket, &QTcpSocket::deleteLater);
    }
}

void TestServer::handleSocketReady(QTcpSocket* socket)
{
    while (socket->canReadLine()) {
        const QByteArray line = socket->readLine().trimmed();
        QJsonParseError parseError;
        const QJsonDocument requestDoc = QJsonDocument::fromJson(line, &parseError);

        QJsonObject response;
        if (parseError.error != QJsonParseError::NoError || !requestDoc.isObject()) {
            response = fail(QStringLiteral("E2E_INFRA_ERROR"), QStringLiteral("request must be a JSON object"));
        } else {
            response = handleRequest(requestDoc.object());
        }

        socket->write(QJsonDocument(response).toJson(QJsonDocument::Compact));
        socket->write("\n");
        socket->flush();
    }
}

QJsonObject TestServer::handleRequest(const QJsonObject& request)
{
    const QString command = request.value(QStringLiteral("command")).toString();

    if (command == QStringLiteral("health")) {
        return handleHealth();
    }
    if (command == QStringLiteral("list-aliases")) {
        return handleListAliases();
    }
    if (command == QStringLiteral("query")) {
        return handleQuery(request);
    }
    if (command == QStringLiteral("click")) {
        return handleClick(request);
    }
    if (command == QStringLiteral("set-text")) {
        return handleSetText(request);
    }
    if (command == QStringLiteral("get-text")) {
        return handleGetText(request);
    }
    if (command == QStringLiteral("wait-idle")) {
        return handleWaitIdle(request);
    }

    return fail(QStringLiteral("UNKNOWN_COMMAND"), QStringLiteral("unknown command"));
}

QJsonObject TestServer::handleHealth() const
{
    QJsonObject data;
    data.insert(QStringLiteral("status"), QStringLiteral("ok"));
    return ok(data);
}

QJsonObject TestServer::handleListAliases() const
{
    QJsonArray aliases;
    for (const AliasEntry& entry : registry_.entries()) {
        aliases.append(aliasToJson(entry));
    }

    QJsonObject data;
    data.insert(QStringLiteral("aliases"), aliases);
    return ok(data);
}

QJsonObject TestServer::handleQuery(const QJsonObject& request)
{
    const QString name = request.value(QStringLiteral("name")).toString();
    if (!registry_.contains(name)) {
        return fail(QStringLiteral("NOT_FOUND"), QStringLiteral("alias not found"));
    }

    QJsonObject data = aliasToJson(registry_.entry(name));
    QString error;
    if (!driver_->query(registry_.entry(name), &data, &error)) {
        return fail(QStringLiteral("E2E_INFRA_ERROR"), error);
    }
    return ok(data);
}

QJsonObject TestServer::handleClick(const QJsonObject& request)
{
    const QString name = request.value(QStringLiteral("name")).toString();
    if (!registry_.contains(name)) {
        return fail(QStringLiteral("NOT_FOUND"), QStringLiteral("alias not found"));
    }

    QString error;
    if (!driver_->click(registry_.entry(name), &error)) {
        return fail(QStringLiteral("E2E_INFRA_ERROR"), error);
    }
    QJsonObject data;
    data.insert(QStringLiteral("alias"), name);
    return ok(data);
}

QJsonObject TestServer::handleSetText(const QJsonObject& request)
{
    const QString name = request.value(QStringLiteral("name")).toString();
    const QString value = request.value(QStringLiteral("value")).toString();
    if (!registry_.contains(name)) {
        return fail(QStringLiteral("NOT_FOUND"), QStringLiteral("alias not found"));
    }

    QString error;
    if (!driver_->setText(registry_.entry(name), value, &error)) {
        return fail(QStringLiteral("E2E_INFRA_ERROR"), error);
    }
    QJsonObject data;
    data.insert(QStringLiteral("alias"), name);
    return ok(data);
}

QJsonObject TestServer::handleGetText(const QJsonObject& request)
{
    const QString name = request.value(QStringLiteral("name")).toString();
    if (!registry_.contains(name)) {
        return fail(QStringLiteral("NOT_FOUND"), QStringLiteral("alias not found"));
    }

    QString value;
    QString error;
    if (!driver_->getText(registry_.entry(name), &value, &error)) {
        return fail(QStringLiteral("E2E_INFRA_ERROR"), error);
    }

    QJsonObject data;
    data.insert(QStringLiteral("alias"), name);
    data.insert(QStringLiteral("text"), value);
    return ok(data);
}

QJsonObject TestServer::handleWaitIdle(const QJsonObject& request)
{
    const int timeoutMs = request.value(QStringLiteral("timeoutMs")).toInt(0);
    QCoreApplication::processEvents(QEventLoop::AllEvents, timeoutMs);
    QJsonObject data;
    data.insert(QStringLiteral("idle"), true);
    return ok(data);
}

QJsonObject TestServer::aliasToJson(const AliasEntry& entry) const
{
    QJsonArray hitTargets;
    for (const QString& hitTarget : entry.hitTargets) {
        hitTargets.append(hitTarget);
    }

    QJsonObject data;
    data.insert(QStringLiteral("alias"), entry.alias);
    data.insert(QStringLiteral("page"), entry.page);
    data.insert(QStringLiteral("owner"), entry.owner);
    data.insert(QStringLiteral("objectName"), entry.objectName);
    data.insert(QStringLiteral("classHint"), entry.classHint);
    data.insert(QStringLiteral("role"), entry.role);
    data.insert(QStringLiteral("hitTargets"), hitTargets);
    data.insert(QStringLiteral("required"), entry.required);
    data.insert(QStringLiteral("deprecated"), entry.deprecated);
    data.insert(QStringLiteral("description"), entry.description);
    return data;
}

QJsonObject TestServer::ok(const QJsonObject& data) const
{
    QJsonObject response;
    response.insert(QStringLiteral("ok"), true);
    response.insert(QStringLiteral("data"), data);
    return response;
}

QJsonObject TestServer::fail(const QString& code, const QString& message) const
{
    QJsonObject response;
    response.insert(QStringLiteral("ok"), false);
    response.insert(QStringLiteral("code"), code);
    response.insert(QStringLiteral("message"), message);
    response.insert(QStringLiteral("data"), QJsonObject{});
    return response;
}

} // namespace qt_e2e_driver

#endif // ENABLE_TEST_SERVER
