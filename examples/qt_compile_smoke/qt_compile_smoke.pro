TEMPLATE = app
TARGET = qt_compile_smoke
CONFIG += console c++17
CONFIG -= app_bundle

DEFINES += ENABLE_TEST_SERVER
QT += core network widgets testlib

INCLUDEPATH += ../../include

SOURCES += \
    main.cpp \
    ../../src/qt/AliasRegistry.cpp \
    ../../src/qt/TestServer.cpp
