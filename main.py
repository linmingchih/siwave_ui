from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QFileDialog,
    QPlainTextEdit,
    QDialog,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QDialogButtonBox,
    QMessageBox,
)
import os
from win32com import client
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt
import xml.etree.ElementTree as ET
import re
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


def _parse_custom_stackup(text: str) -> ET.Element:
    """Convert a $begin/$end style stackup file into an XML Element."""
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"\$begin '([^']+)'", line)
        if m:
            lines.append(f"<{m.group(1)}>")
            continue
        m = re.match(r"\$end '([^']+)'", line)
        if m:
            lines.append(f"</{m.group(1)}>")
            continue
        if line.startswith("Units(") and line.endswith(")"):
            val = line[len("Units("):-1].strip("'\"")
            lines.append(f"<Units>{val}</Units>")
            continue
        if line.startswith("Layer(") and line.endswith(")"):
            content = line[len("Layer("):-1]
            attrs = dict(re.findall(r"(\w+)=('(?:[^']*)'|[^,()]+)", content))
            attr_str = " ".join(f'{k}="{v.strip("'\"")}"' for k, v in attrs.items())
            lines.append(f"<Layer {attr_str}/>")
            continue
        if '(' in line and line.endswith(')'):
            key, val = line[:-1].split('(', 1)
            lines.append(f"<{key}>{val}</{key}>")
            continue
        if '=' in line:
            key, val = line.split('=', 1)
            lines.append(f"<{key}>{val.strip("'\"")}</{key}>")
            continue
    xml_text = "".join(lines)
    return ET.fromstring(xml_text)


def parse_stackup_file(path: str) -> ET.ElementTree:
    """Parse a stackup file that may not be valid XML."""
    try:
        return ET.parse(path)
    except (ET.ParseError, FileNotFoundError):
        with open(path, "r", encoding="utf-8") as fh:
            data = fh.read()
        root = _parse_custom_stackup(data)
        return ET.ElementTree(root)


class StackupDialog(QDialog):
    def __init__(self, xml_path: str, doc=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stackup Editor")
        self.resize(600, 400)

        self.xml_path = xml_path
        # store the SIwave document handle for later use
        self.oDoc = doc
        try:
            self.tree = parse_stackup_file(xml_path)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to parse stackup file:\n{exc}"
            )
            raise
        self.root = self.tree.getroot()
        self.stackup = self.root
        if self.root.tag != "Stackup":
            child = self.root.find("Stackup")
            if child is not None:
                self.stackup = child
        self.layers = self.stackup.find("Layers").findall("Layer")
        mats_elem = self.stackup.find("Materials")
        self.materials = list(mats_elem) if mats_elem is not None else []

        self.tabs = QTabWidget(self)

        # Only show the basic layer information and materials
        self.tab_general = self._create_general_tab()
        self.tab_material = self._create_material_tab()

        buttons = QDialogButtonBox()
        self._btn_apply = buttons.addButton(QDialogButtonBox.Apply)
        buttons.addButton(QDialogButtonBox.Ok)
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._btn_apply.clicked.connect(self.apply_changes)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        layout.addWidget(buttons)

    def _create_general_tab(self):
        table = QTableWidget(len(self.layers), 5)
        table.setHorizontalHeaderLabels([
            "Name", "Type", "Thickness", "Elevation", "Material"
        ])
        material_names = [
            mat.get("Name") or mat.findtext("Name", default="")
            for mat in self.materials
        ]
        for row, layer in enumerate(self.layers):
            table.setItem(
                row, 0,
                QTableWidgetItem(layer.get("LayerName", layer.get("Name", "")))
            )
            table.setItem(
                row, 1,
                QTableWidgetItem(layer.get("LayerType", layer.get("Type", "")))
            )
            table.setItem(row, 2, QTableWidgetItem(layer.get("Thickness", "")))
            table.setItem(row, 3, QTableWidgetItem(layer.get("Elevation", "")))

            combo = QComboBox()
            combo.addItems(material_names)
            current = layer.get("Material", "")
            if current:
                idx = combo.findText(current)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            table.setCellWidget(row, 4, combo)
        table.cellDoubleClicked.connect(self._on_general_double_clicked)
        self.tabs.addTab(table, "Layers")
        return table

    def _on_general_double_clicked(self, row: int, column: int):
        if column != 4:
            return
        widget = self.tab_general.cellWidget(row, 4)
        if isinstance(widget, QComboBox):
            mat_name = widget.currentText()
        else:
            item = self.tab_general.item(row, 4)
            mat_name = item.text() if item else ""
        for r in range(self.tab_material.rowCount()):
            if self.tab_material.item(r, 0).text() == mat_name:
                self.tabs.setCurrentWidget(self.tab_material)
                self.tab_material.selectRow(r)
                break

    def _create_roughness_tab(self):
        table = QTableWidget(len(self.layers), 4)
        table.setHorizontalHeaderLabels([
            "Name", "Top", "Bottom", "Side"
        ])
        for row, layer in enumerate(self.layers):
            table.setItem(row, 0, QTableWidgetItem(layer.get("Name", "")))
            table.setItem(row, 1, QTableWidgetItem(layer.get("TopRoughness", "")))
            table.setItem(row, 2, QTableWidgetItem(layer.get("BottomRoughness", "")))
            table.setItem(row, 3, QTableWidgetItem(layer.get("SideRoughness", "")))
        self.tabs.addTab(table, "Roughness")
        return table

    def _create_cross_tab(self):
        table = QTableWidget(len(self.layers), 5)
        table.setHorizontalHeaderLabels([
            "Name", "Shape", "Etch", "Top Edge", "Bottom Edge"
        ])
        for row, layer in enumerate(self.layers):
            table.setItem(row, 0, QTableWidgetItem(layer.get("Name", "")))
            table.setItem(row, 1, QTableWidgetItem(layer.get("TraceCrossSectionShape", "")))
            table.setItem(row, 2, QTableWidgetItem(layer.get("TraceCrossSectionEtchStyle", "")))
            table.setItem(row, 3, QTableWidgetItem(layer.get("TraceCrossSectionTopEdgeRatio", "")))
            table.setItem(row, 4, QTableWidgetItem(layer.get("TraceCrossSectionBottomEdgeRatio", "")))
        self.tabs.addTab(table, "Cross Section")
        return table

    def _create_material_tab(self):
        table = QTableWidget(len(self.materials), 4)
        table.setHorizontalHeaderLabels([
            "Name", "Permittivity", "LossTangent", "Conductivity"
        ])
        for row, mat in enumerate(self.materials):
            name = mat.get("Name") or mat.findtext("Name", default="")
            perm_el = mat.find("Permittivity")
            if perm_el is not None and perm_el.find("Double") is not None:
                perm = perm_el.findtext("Double", default="")
            else:
                perm = mat.findtext("Permittivity", default="")
            loss_el = mat.find("LossTangent") or mat.find("DielectricLossTangent")
            if loss_el is not None and loss_el.find("Double") is not None:
                loss = loss_el.findtext("Double", default="")
            else:
                loss = (mat.findtext("LossTangent") or
                        mat.findtext("DielectricLossTangent", default=""))
            cond_el = mat.find("Conductivity")
            if cond_el is not None and cond_el.find("Double") is not None:
                cond = cond_el.findtext("Double", default="")
            else:
                cond = mat.findtext("Conductivity", default="")
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(perm))
            table.setItem(row, 2, QTableWidgetItem(loss))
            table.setItem(row, 3, QTableWidgetItem(cond))
        self.tabs.addTab(table, "Materials")
        return table

    def _save_changes(self):
        """Save table values back to the XML file."""
        # update layers
        for row, layer in enumerate(self.layers):
            layer.set("LayerName", self.tab_general.item(row, 0).text())
            layer.set("LayerType", self.tab_general.item(row, 1).text())
            layer.set("Thickness", self.tab_general.item(row, 2).text())
            layer.set("Elevation", self.tab_general.item(row, 3).text())
            widget = self.tab_general.cellWidget(row, 4)
            if isinstance(widget, QComboBox):
                layer.set("Material", widget.currentText())
            else:
                layer.set("Material", self.tab_general.item(row, 4).text())

        # update materials
        for row, mat in enumerate(self.materials):
            name_el = mat.find("Name")
            if name_el is not None:
                name_el.text = self.tab_material.item(row, 0).text()
            perm_el = mat.find("Permittivity")
            if perm_el is not None:
                dbl = perm_el.find("Double")
                if dbl is not None:
                    dbl.text = self.tab_material.item(row, 1).text()
                else:
                    perm_el.text = self.tab_material.item(row, 1).text()
            loss_el = mat.find("LossTangent") or mat.find("DielectricLossTangent")
            if loss_el is not None:
                dbl = loss_el.find("Double")
                if dbl is not None:
                    dbl.text = self.tab_material.item(row, 2).text()
                else:
                    loss_el.text = self.tab_material.item(row, 2).text()
            cond_el = mat.find("Conductivity")
            if cond_el is not None:
                dbl = cond_el.find("Double")
                if dbl is not None:
                    dbl.text = self.tab_material.item(row, 3).text()
                else:
                    cond_el.text = self.tab_material.item(row, 3).text()

        ET.indent(self.tree, space="  ")
        self.tree.write(self.xml_path, encoding="utf-8", xml_declaration=True)

    def apply_changes(self):
        self._save_changes()

        try:
            self.oDoc.ScrImportLayerStackup(self.xml_path)
            parent = self.parent()
            if parent and hasattr(parent, "messages"):
                parent.messages.appendPlainText(
                    "Imported stackup from {}".format(self.xml_path)
                )
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Failed to import stackup:\n{exc}")

    def accept(self):
        self._save_changes()
        super().accept()

class ModelExtractionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIwave Model Extraction (Dark Mode)")
        self.setFixedSize(360, 640)
        self.move(0, 0)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.oApp = None
        self.oDoc = None

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

        self.messages = QPlainTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setPlaceholderText("Messages")
        self.messages.setFixedHeight(120)
        layout.addWidget(self.messages)

    def closeEvent(self, event):
        if self.oApp:
            try:
                self.oApp.Quit()
            except Exception as exc:
                self.messages.appendPlainText(f"Failed to close SIwave: {exc}")
        super().closeEvent(event)

    def handle_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        if item.text(0) == "Load Layout File" and not item.isDisabled():
            edb_file, _ = QFileDialog.getOpenFileName(
                self,
                "Select edb.def",
                "",
                "edb.def (edb.def)"
            )
            if edb_file:
                folder = os.path.dirname(edb_file)
                self.oApp = client.Dispatch("SIwave.Application.2025.1")
                self.oApp.RestoreWindow()
                self.oDoc = self.oApp.GetActiveProject()
                self.oDoc.ScrImportEDB(folder)
                self.messages.appendPlainText(f"Loaded layout: {folder}")
        elif item.text(0) == "Check Stackup" and not item.isDisabled():
            if not self.oDoc:
                self.messages.appendPlainText("Please load a layout first")
                return
            xml_path = os.path.join(os.getcwd(), "stackup.xml")
            self.oDoc.ScrExportLayerStackup(xml_path)
            try:
                dlg = StackupDialog(xml_path, self.oDoc, self)
            except Exception as exc:
                self.messages.appendPlainText(f"Failed to open stackup editor: {exc}")
                return
            if dlg.exec() == QDialog.Accepted:
                self.oDoc.ScrImportLayerStackup(xml_path)
                self.messages.appendPlainText("Stackup updated")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)               # 啟用深色模式
    win = ModelExtractionWindow()
    win.show()
    sys.exit(app.exec())
