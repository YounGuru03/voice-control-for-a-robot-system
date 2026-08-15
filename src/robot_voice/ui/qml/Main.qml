import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 1280
    height: 820
    title: "机器人语音控制系统"

    TabView {
        anchors.fill: parent

        Tab {
            title: "仪表盘"
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 10
                Label { text: "状态: " + appVm.status; font.pixelSize: 24 }
                Rectangle { Layout.fillWidth: true; height: 12; radius: 6; color: "#35c46a" }
                RowLayout {
                    Button { text: "开始"; onClicked: appVm.start() }
                    Button { text: "暂停"; onClicked: appVm.pause() }
                    Button { text: "停止"; onClicked: appVm.stop() }
                    Button { text: "急停"; onClicked: appVm.emergencyStop() }
                }
                Label { text: "实时转写" }
                TextArea { Layout.fillWidth: true; Layout.fillHeight: true; text: appVm.transcript; readOnly: true }
                Label { text: "最近命令" }
                TextArea { Layout.fillWidth: true; Layout.preferredHeight: 180; text: appVm.history; readOnly: true }
            }
        }

        Tab {
            title: "命令管理"
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                Label { text: "搜索/过滤/导入导出/启停命令（基础页面占位）" }
                TextArea { Layout.fillWidth: true; Layout.fillHeight: true; text: "命令配置将从 config/commands.json 载入"; readOnly: true }
            }
        }

        Tab {
            title: "音频与模型"
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                Label { text: "音频设备、VAD敏感度、ASR后端与模型管理" }
                TextArea { Layout.fillWidth: true; Layout.fillHeight: true; text: "支持 Auto-VAD / Push-to-Talk / Manual 模式"; readOnly: true }
            }
        }

        Tab {
            title: "机器人连接"
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                Label { text: "Mock / Serial / HTTP 连接和健康检查" }
                TextArea { Layout.fillWidth: true; Layout.fillHeight: true; text: "硬件操作通过异步服务层执行，UI不直接访问串口/HTTP"; readOnly: true }
            }
        }

        Tab {
            title: "诊断"
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                Label { text: "日志与时延指标" }
                TextArea { Layout.fillWidth: true; Layout.fillHeight: true; text: "默认不包含原始录音；可导出脱敏诊断包"; readOnly: true }
            }
        }
    }
}
