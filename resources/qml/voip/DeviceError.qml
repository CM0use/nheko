// SPDX-FileCopyrightText: Nheko Contributors
//
// SPDX-License-Identifier: GPL-3.0-or-later

import QtQuick 2.9
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.2

Popup {
    id: r

    property string errorString
    property var image

    modal: true

    background: Rectangle {
        border.color: palette.windowText
        color: palette.window
    }

    // only set the anchors on Qt 5.12 or higher
    // see https://doc.qt.io/qt-5/qml-qtquick-controls2-popup.html#anchors.centerIn-prop
    Component.onCompleted: {
        if (anchors)
            anchors.centerIn = parent;
    }

    RowLayout {
        Image {
            Layout.preferredHeight: 16
            Layout.preferredWidth: 16
            source: "image://colorimage/" + r.image + "?" + palette.windowText
        }
        Label {
            color: palette.windowText
            text: r.errorString
        }
    }
}
