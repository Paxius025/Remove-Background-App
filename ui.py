from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QPixmap, QPalette, QColor, QFont
import sys
import os
import subprocess

class RemoveBGApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Remove Background App")
        self.setGeometry(100, 100, 600, 400)  # Smaller window size

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
        app_bar_layout.addStretch()  # Push the close button to the right
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

        # Loading animation (progress bar)
        self.loading_label = QLabel("Ready")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setFont(QFont("Arial", 10))
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

        self.browse_button = QPushButton("Browse Image")
        self.browse_button.setStyleSheet(button_style)
        self.browse_button.clicked.connect(self.browse_image)
        layout.addWidget(self.browse_button)

        self.remove_bg_button = QPushButton("Remove Background")
        self.remove_bg_button.setStyleSheet(button_style)
        self.remove_bg_button.clicked.connect(self.remove_background)
        layout.addWidget(self.remove_bg_button)

        self.open_folder_button = QPushButton("Open Export Folder")
        self.open_folder_button.setStyleSheet(button_style)
        self.open_folder_button.clicked.connect(self.open_export_folder)
        layout.addWidget(self.open_folder_button)

        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        self.image_path = None
        self.export_path = "C:\\Users\\panto\\OneDrive\\Pictures\\remvoebg"

    def close_app(self):
        self.close()

    def browse_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "C:\\Users\\panto\\Downloads", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name).scaled(200, 200, Qt.KeepAspectRatio)
            self.original_image_label.setPixmap(pixmap)
            self.processed_image_label.clear()
            self.loading_label.setText("Ready")

    def remove_background(self):
        if self.image_path:
            self.loading_label.setText("Removing background, please wait...")
            self.loading_label.setStyleSheet("color: #e67e22;")
            QApplication.processEvents()  # Update the UI immediately

            from utils import remove_background
            output_file = remove_background(self.image_path, self.export_path)

            if output_file:
                processed_pixmap = QPixmap(output_file).scaled(200, 200, Qt.KeepAspectRatio)
                self.processed_image_label.setPixmap(processed_pixmap)
                self.loading_label.setText("Background removed successfully!")
                self.loading_label.setStyleSheet("color: #27ae60;")
            else:
                self.loading_label.setText("Error processing image.")
                self.loading_label.setStyleSheet("color: #e74c3c;")

        else:
            self.loading_label.setText("Please select an image first.")
            self.loading_label.setStyleSheet("color: #e74c3c;")

    def open_export_folder(self):
        # Open the export folder in the file explorer
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
