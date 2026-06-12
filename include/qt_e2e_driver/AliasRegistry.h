#pragma once

#include <QHash>
#include <QPoint>
#include <QString>
#include <QStringList>
#include <QVector>

class QWidget;

namespace qt_e2e_driver {

struct AliasEntry {
    QString alias;
    QString page;
    QString owner;
    QString objectName;
    QString classHint;
    QString role;
    QStringList hitTargets;
    bool required = false;
    bool deprecated = false;
    QString description;
};

class AliasRegistry {
public:
    bool add(const AliasEntry& entry, QString* error = nullptr);
    bool contains(const QString& alias) const;
    AliasEntry entry(const QString& alias) const;
    QVector<AliasEntry> entries() const;
    QStringList aliases() const;
    QStringList validate() const;

private:
    QHash<QString, AliasEntry> entriesByAlias_;
};

class HitResolver {
public:
    virtual ~HitResolver() = default;

    // Resolves a named hit target inside a QWidget into a local widget coordinate.
    // This must not call business slots or emit product signals.
    virtual bool hitPoint(QWidget* widget,
                          const QString& hitTarget,
                          QPoint* point,
                          QString* error) const = 0;
};

} // namespace qt_e2e_driver
