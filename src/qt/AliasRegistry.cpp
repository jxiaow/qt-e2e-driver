#include "qt_e2e_driver/AliasRegistry.h"

#include <algorithm>

namespace qt_e2e_driver {

bool AliasRegistry::add(const AliasEntry& entry, QString* error)
{
    if (entry.alias.trimmed().isEmpty()) {
        if (error) {
            *error = QStringLiteral("alias must not be empty");
        }
        return false;
    }

    if (entry.objectName.trimmed().isEmpty()) {
        if (error) {
            *error = QStringLiteral("objectName must not be empty for alias %1").arg(entry.alias);
        }
        return false;
    }

    if (entriesByAlias_.contains(entry.alias)) {
        if (error) {
            *error = QStringLiteral("duplicate alias %1").arg(entry.alias);
        }
        return false;
    }

    entriesByAlias_.insert(entry.alias, entry);
    return true;
}

bool AliasRegistry::contains(const QString& alias) const
{
    return entriesByAlias_.contains(alias);
}

AliasEntry AliasRegistry::entry(const QString& alias) const
{
    return entriesByAlias_.value(alias);
}

QVector<AliasEntry> AliasRegistry::entries() const
{
    return entriesByAlias_.values().toVector();
}

QStringList AliasRegistry::aliases() const
{
    QStringList names = entriesByAlias_.keys();
    names.sort();
    return names;
}

QStringList AliasRegistry::validate() const
{
    QStringList errors;
    QHash<QString, QString> firstAliasByObjectName;

    for (const AliasEntry& item : entriesByAlias_) {
        if (item.alias.trimmed().isEmpty()) {
            errors.append(QStringLiteral("alias must not be empty"));
        }

        if (item.objectName.trimmed().isEmpty()) {
            errors.append(QStringLiteral("%1 has empty objectName").arg(item.alias));
        }

        if (item.required && item.deprecated) {
            errors.append(QStringLiteral("%1 cannot be both required and deprecated").arg(item.alias));
        }

        if (firstAliasByObjectName.contains(item.objectName)) {
            errors.append(
                QStringLiteral("%1 and %2 share objectName %3")
                    .arg(firstAliasByObjectName.value(item.objectName), item.alias, item.objectName));
        } else {
            firstAliasByObjectName.insert(item.objectName, item.alias);
        }
    }

    errors.sort();
    return errors;
}

} // namespace qt_e2e_driver
