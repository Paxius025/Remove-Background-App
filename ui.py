from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QIcon
import sys
import os
import subprocess

class BackgroundRemovalThread(QThread):
    progress_signal = pyqtSignal(int)  # Signal to update the progress bar
    result_signal = pyqtSignal(str, str)  # Signal to update the UI with status

    def __init__(self, image_paths, export_path):
        super().__init__()
        self.image_paths = image_paths
        self.export_path = export_path

    def run(self):
        try:
            from utils import remove_background
            self.progress_signal.emit(0)  # Initial progress
            
            for i, image_path in enumerate(self.image_paths):
                output_file = remove_background(image_path, self.export_path)
                if not output_file:
                    self.result_signal.emit("error", f"Error processing {os.path.basename(image_path)}")
                    return
                progress = int((i + 1) / len(self.image_paths) * 100)
                self.progress_signal.emit(progress)
                self.msleep(20)  # Simulate some processing time

            self.result_signal.emit("success", "")
        except Exception as e:
            self.result_signal.emit("error", str(e))

class RemoveBGApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.bg_thread = None  # Initialize the background thread
        self.image_paths = []  # Store multiple image paths

    def initUI(self):
        self.setWindowTitle("Remove Background")
        self.setGeometry(100, 100, 600, 400)  # Smaller window size
        self.setWindowIcon(QIcon("assets/logo.png"))

        # Set the window to be frameless but include shadow and rounded corners
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                border-radius: 10px;
                border: 1px solid #888;
            }
        """)

        self.dragPos = None

        # Center the window on the screen
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        # Layout and Widgets
        self.central_widget = QWidget()
        layout = QVBoxLayout(self.central_widget)

        # App Bar
        app_bar = QWidget()
        app_bar_layout = QHBoxLayout(app_bar)
        app_bar_layout.setContentsMargins(5, 5, 5, 5)
        app_bar.setStyleSheet("background-color: #2c3e50; border-top-left-radius: 10px; border-top-right-radius: 10px;")

        self.title_label = QLabel("Remove Background App")
        self.title_label.setFont(QFont("Arial", 12))
        self.title_label.setStyleSheet("color: white; padding: 5px;")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.close_button.clicked.connect(self.close_app)

        app_bar_layout.addWidget(self.title_label)
        app_bar_layout.addStretch()
        app_bar_layout.addWidget(self.close_button)

        layout.addWidget(app_bar)

        # Image Display
        image_layout = QHBoxLayout()

        self.original_image_label = QLabel("Original Image")
        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.original_image_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        image_layout.addWidget(self.original_image_label)

        self.processed_image_label = QLabel("Processed Image")
        self.processed_image_label.setAlignment(Qt.AlignCenter)
        self.processed_image_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        image_layout.addWidget(self.processed_image_label)

        layout.addLayout(image_layout)

        # Beautiful Loading Animation (Progress Bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #6dd5ed, stop:1 #2193b0
                );
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.loading_label = QLabel("Ready")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.loading_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        layout.addWidget(self.loading_label)

        # Buttons
        button_style = """
            QPushButton {
                background-color: #2980b9; 
                color: white; 
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """

        self.browse_button = QPushButton("Browse Images")
        self.browse_button.setStyleSheet(button_style)
        self.browse_button.clicked.connect(self.browse_images)
        layout.addWidget(self.browse_button)

        self.remove_bg_button = QPushButton("Remove Background")
        self.remove_bg_button.setStyleSheet(button_style)
        self.remove_bg_button.clicked.connect(self.start_background_removal)
        layout.addWidget(self.remove_bg_button)

        self.open_folder_button = QPushButton("Open Export Folder")
        self.open_folder_button.setStyleSheet(button_style)
        self.open_folder_button.clicked.connect(self.open_export_folder)
        layout.addWidget(self.open_folder_button)

        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        self.export_path = "C:\\Users\\panto\\OneDrive\\Pictures\\remvoebg"

    def close_app(self):
        self.close()

    def browse_images(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Open Images", "C:\\Users\\panto\\Downloads", "Image Files (*.png *.jpg *.jpeg)")
        if file_names:
            total_size = sum(os.path.getsize(f) for f in file_names) / (1024 * 1024)  # Calculate total size in MB
            if total_size > 100:
                self.show_popup("The total size of selected images exceeds 100MB. Please select smaller files.")
                return
            self.image_paths = file_names
            pixmap = QPixmap(file_names[0]).scaled(200, 200, Qt.KeepAspectRatio)
            self.original_image_label.setPixmap(pixmap)
            self.processed_image_label.clear()
            self.loading_label.setText("Ready")

    def start_background_removal(self):
        if self.image_paths:
            self.loading_label.setText("Removing background, please wait...")
            self.loading_label.setStyleSheet("color: #e67e22;")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            # Start the background removal thread
            self.bg_thread = BackgroundRemovalThread(self.image_paths, self.export_path)
            self.bg_thread.progress_signal.connect(self.update_progress_bar)
            self.bg_thread.result_signal.connect(self.update_ui_after_removal)
            self.bg_thread.start()
        else:
            self.loading_label.setText("Please select images first.")
            self.loading_label.setStyleSheet("color: #e74c3c;")

    def show_popup(self, message):
        msg = QMessageBox(self)
        msg.setWindowTitle("File Size Warning")
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 12px;
            }
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        msg.exec_()

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def update_ui_after_removal(self, status, _):
        self.progress_bar.setVisible(False)
        if status == "success":
            self.loading_label.setText("Backgrounds removed successfully!")
            self.loading_label.setStyleSheet("color: #27ae60;")
        else:
            self.loading_label.setText("Error processing images.")
            self.loading_label.setStyleSheet("color: #e74c3c;")

    def open_export_folder(self):
        if os.path.exists(self.export_path):
            subprocess.Popen(f'explorer "{self.export_path}"')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.dragPos:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RemoveBGApp()
    window.show()
    sys.exit(app.exec_())
