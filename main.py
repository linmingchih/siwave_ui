from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QFileDialog,
)
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt
import sys

def apply_dark_theme(app: QApplication):
    """設定深色主題調色盤"""
    palette = QPalette()
    # 背景色
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    # 文字色
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    # 按鈕
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    # 選取
    palette.setColor(QPalette.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

class ModelExtractionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIwave Model Extraction (Dark Mode)")
        self.resize(360, 640)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(12)

        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)

        root = QTreeWidgetItem(self.tree, ["Model Extraction"])
        root.setFont(0, title_font)
        self.tree.addTopLevelItem(root)

        def add_section(parent, title, items, selected=None, disabled=None):
            sec = QTreeWidgetItem(parent, [title])
            sec.setFont(0, title_font)
            for txt in items:
                it = QTreeWidgetItem(sec, [txt])
                if selected and txt in selected:
                    it.setSelected(True)
                if disabled and txt in disabled:
                    it.setDisabled(True)

        add_section(root, "Layout Setup",
            ["Load Layout File", "Check Stackup", "Select Nets",
             "Assign Capacitor Models", "Select Components"],
            selected=["Check Stackup"]
        )

        add_section(root, "Simulation Setup",
            ["Enable Extraction Mode", "Generate Port(s)", "Setup Simulation Frequencies"],
            selected=["Enable Extraction Mode"]
        )

        add_section(root, "Simulation",
            ["Check Errors/Warnings", "Set up Computer Resources",
             "Start Simulation", "Report"],
            disabled=["Start Simulation", "Report"]
        )

        add_section(root, "View, Check, Process Result",
            ["Network Parameter Display", "Check S-Parameter by BBS"]
        )

        add_section(root, "Generate Model",
            ["Generate Broadband SPICE Model"],
            disabled=["Generate Broadband SPICE Model"]
        )

        root.setExpanded(True)
        for i in range(root.childCount()):
            root.child(i).setExpanded(True)

        self.tree.itemDoubleClicked.connect(self.handle_item_double_clicked)

        layout.addWidget(self.tree)

    def handle_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        if item.text(0) == "Load Layout File" and not item.isDisabled():
            QFileDialog.getOpenFileName(
                self,
                "Open Layout File",
                "",
                "Layout Files (*.aedb *.brd);;All Files (*)",
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)               # 啟用深色模式
    win = ModelExtractionWindow()
    win.show()
    sys.exit(app.exec())
