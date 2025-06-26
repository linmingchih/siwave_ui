import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QListWidget, QLineEdit, QFormLayout,
    QProgressBar, QGroupBox, QComboBox
)
from PySide6.QtGui import QFont

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

        # Setup panel with simulation settings
        setup_panel = QGroupBox("Setup")
        setup_layout = QVBoxLayout()

        self.file_btn = QPushButton("Upload Layout")
        self.file_btn.clicked.connect(self.load_file)
        self.stackup_btn = QPushButton("Check Stackup")
        self.nets_list = QListWidget()
        self.nets_list.setToolTip("Select power/ground nets")
        setup_layout.addWidget(self.file_btn)
        setup_layout.addWidget(self.stackup_btn)
        setup_layout.addWidget(QLabel("Nets"))
        setup_layout.addWidget(self.nets_list)

        sim_settings_box = QGroupBox("Simulation Settings")
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

        sim_settings_box.setLayout(form_layout)
        setup_layout.addWidget(sim_settings_box)
        setup_panel.setLayout(setup_layout)

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
        self.download_snp = QPushButton("Download S-parameters")
        self.download_spice = QPushButton("Download SPICE Model")
        dl_layout = QHBoxLayout()
        dl_layout.addWidget(self.download_snp)
        dl_layout.addWidget(self.download_spice)
        results_layout.addLayout(dl_layout)
        results_box = QGroupBox("Results")
        results_box.setLayout(results_layout)

        main_layout.addWidget(top_box)
        main_layout.addWidget(setup_panel)
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
