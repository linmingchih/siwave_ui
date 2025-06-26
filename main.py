import sys
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QListWidget, QLineEdit, QFormLayout,
    QProgressBar, QGroupBox, QComboBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class SParameterPlot(QWidget):
    """Matplotlib widget to display S-parameter curves."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.plot_placeholder()

    def plot_placeholder(self):
        ax = self.figure.add_subplot(111)
        ax.clear()
        freqs = [i for i in range(1, 11)]
        s11 = [random.uniform(-40, -3) for _ in freqs]
        ax.plot(freqs, s11, label="S11")
        ax.set_xlabel("Frequency (GHz)")
        ax.set_ylabel("dB")
        ax.set_title("S-parameter Plot")
        ax.legend()
        self.canvas.draw()


class PIApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIwave PI Simulation")
        self.setMinimumSize(900, 600)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Top section
        title = QLabel("SIwave PI Simulation Tool")
        desc = QLabel("This tool guides you through setting up and running a power integrity simulation.")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        desc.setWordWrap(True)
        top_layout = QVBoxLayout()
        top_layout.addWidget(title)
        top_layout.addWidget(desc)
        top_box = QGroupBox()
        top_box.setLayout(top_layout)

        # Middle section with left and right panels
        middle_layout = QHBoxLayout()

        # Left panel
        left_panel = QGroupBox("Setup")
        left_layout = QVBoxLayout()

        self.file_btn = QPushButton("Upload Layout")
        self.file_btn.clicked.connect(self.load_file)
        self.stackup_btn = QPushButton("Check Stackup")
        self.nets_list = QListWidget()
        self.nets_list.setToolTip("Select power/ground nets")
        left_layout.addWidget(self.file_btn)
        left_layout.addWidget(self.stackup_btn)
        left_layout.addWidget(QLabel("Nets"))
        left_layout.addWidget(self.nets_list)
        left_panel.setLayout(left_layout)

        # Right panel
        right_panel = QGroupBox("Simulation Settings")
        form_layout = QFormLayout()
        self.freq_start = QLineEdit()
        self.freq_stop = QLineEdit()
        self.freq_step = QLineEdit()
        tooltip_text = "Enter frequency range in GHz"
        self.freq_start.setToolTip(tooltip_text)
        self.freq_stop.setToolTip(tooltip_text)
        self.freq_step.setToolTip(tooltip_text)
        form_layout.addRow("Start freq", self.freq_start)
        form_layout.addRow("Stop freq", self.freq_stop)
        form_layout.addRow("Step", self.freq_step)

        self.port_option = QComboBox()
        self.port_option.addItems(["Auto", "Manual"])
        form_layout.addRow("Port generation", self.port_option)

        self.cap_option = QComboBox()
        self.cap_option.addItems(["Ideal", "Realistic"])
        form_layout.addRow("Capacitor model", self.cap_option)

        right_panel.setLayout(form_layout)

        middle_layout.addWidget(left_panel)
        middle_layout.addWidget(right_panel)

        # Bottom section with button and progress bar
        bottom_layout = QHBoxLayout()
        self.run_btn = QPushButton("Start Simulation")
        self.progress = QProgressBar()
        bottom_layout.addWidget(self.run_btn)
        bottom_layout.addWidget(self.progress)
        bottom_box = QGroupBox()
        bottom_box.setLayout(bottom_layout)

        # Results section
        results_layout = QVBoxLayout()
        self.plot_widget = SParameterPlot()
        self.download_snp = QPushButton("Download S-parameters")
        self.download_spice = QPushButton("Download SPICE Model")
        results_layout.addWidget(self.plot_widget)
        dl_layout = QHBoxLayout()
        dl_layout.addWidget(self.download_snp)
        dl_layout.addWidget(self.download_spice)
        results_layout.addLayout(dl_layout)
        results_box = QGroupBox("Results")
        results_box.setLayout(results_layout)

        main_layout.addWidget(top_box)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(bottom_box)
        main_layout.addWidget(results_box)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Layout", "", "Layout Files (*.aedb *.brd)")
        if file_path:
            # Placeholder: populate nets list with dummy data
            self.nets_list.clear()
            for net in ["VCC", "GND", "VIN"]:
                self.nets_list.addItem(net)

    def apply_styles(self):
        style = f"""
            QWidget {{
                background-color: #f5f7fa;
                color: #333333;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }}
            QGroupBox {{
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 16px;
                padding: 8px;
            }}
            QPushButton {{
                background-color: #007bff;
                color: white;
                border-radius: 8px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                box-shadow: 0 0 5px rgba(0,0,0,0.3);
            }}
            QProgressBar {{
                border-radius: 8px;
                height: 16px;
            }}
        """
        self.setStyleSheet(style)


def main():
    app = QApplication(sys.argv)
    window = PIApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
