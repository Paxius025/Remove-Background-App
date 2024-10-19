from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, 
    QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QMessageBox, 
    QScrollArea, QGridLayout, QStackedWidget, QDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QPixmap, QFont, QIcon
import sys
import os
import subprocess

class BackgroundRemovalThread(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(str, str)

    def __init__(self, image_paths, export_path):
        super().__init__()
        self.image_paths = image_paths
        self.export_path = export_path

    def run(self):
        try:
            from utils import remove_background
            self.progress_signal.emit(0)

            for i, image_path in enumerate(self.image_paths):
                output_file = remove_background(image_path, self.export_path)
                if not output_file:
                    self.result_signal.emit("error", f"Error processing {os.path.basename(image_path)}")
                    return
                progress = int((i + 1) / len(self.image_paths) * 100)
                self.progress_signal.emit(progress)
                self.result_signal.emit("success", output_file)

            self.result_signal.emit("done", "")
        except Exception as e:
            self.result_signal.emit("error", str(e))

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtCore import Qt

class FolderSettingsDialog(QDialog):
    def __init__(self, main_app, import_folder, export_folder):
        super().__init__()
        self.main_app = main_app  # Store the reference to the main app

        # Remove the title bar
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)

        self.setWindowTitle("Set Folder Paths")
        self.setFixedSize(400, 200)

        self.import_folder_line_edit = QLineEdit(import_folder)
        self.export_folder_line_edit = QLineEdit(export_folder)

        # Styling for buttons
        button_style = """
            QPushButton {
                background-color: #3498db; /* Base Color */
                color: white; 
                border-radius: 15px; 
                padding: 10px 20px; /* More padding for a better look */
                font-size: 14px; /* Increase font size */
                border: 2px solid transparent; /* Border for hover effect */
            }
            QPushButton:hover {
                background-color: #2980b9; /* Darker color on hover */
            }
            QPushButton:pressed {
                background-color: #1abc9c; /* Color when pressed */
            }
        """

        browse_import_button = QPushButton("🔎")
        browse_import_button.setStyleSheet(button_style)
        browse_import_button.clicked.connect(self.browse_import_folder)

        browse_export_button = QPushButton("🔎")
        browse_export_button.setStyleSheet(button_style)
        browse_export_button.clicked.connect(self.browse_export_folder)

        save_button = QPushButton("✅")
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(self.save_folders)

        cancel_button = QPushButton("🧹")
        cancel_button.setStyleSheet(button_style)
        cancel_button.clicked.connect(self.close)

        # Layout setup
        layout = QVBoxLayout()
        
        # Import Folder Layout
        import_layout = QHBoxLayout()
        import_layout.addWidget(QLabel("Import Folder:"))
        import_layout.addWidget(self.import_folder_line_edit)
        import_layout.addWidget(browse_import_button)

        # Export Folder Layout
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Export Folder:"))
        export_layout.addWidget(self.export_folder_line_edit)
        export_layout.addWidget(browse_export_button)

        layout.addLayout(import_layout)
        layout.addLayout(export_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Import Folder", "")
        if folder:
            self.import_folder_line_edit.setText(folder)

    def browse_export_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder", "")
        if folder:
            self.export_folder_line_edit.setText(folder)

    def save_folders(self):
        import_folder = self.import_folder_line_edit.text()
        export_folder = self.export_folder_line_edit.text()

        if import_folder and export_folder:
            self.main_app.settings.setValue("import_folder", import_folder)  # Use the stored reference
            self.main_app.settings.setValue("export_path", export_folder)  # Use the stored reference
            self.close()

class RemoveBGApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("RemoveBGApp", "Settings")
        self.initUI()
        self.bg_thread = None
        self.image_paths = []
        self.processed_images = []
        self.import_folder = self.settings.value("import_folder", "")
        self.export_path = self.settings.value("export_path", "")

        # If paths are not set, prompt the user to set them
        if not self.import_folder or not self.export_path:
            self.prompt_initial_settings()

    def initUI(self):
        self.setWindowTitle("Remove Background")
        self.setGeometry(100, 100, 1200, 600)
        self.setWindowIcon(QIcon("assets/logo.png"))

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setStyleSheet(""" 
            QMainWindow {
                background-color: #f0f0f0; 
                border-radius: 10px; 
                border: 1px solid #888; 
            }
        """)

        self.dragPos = None

        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        # Use a stacked widget to switch between the main menu and the app content
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Create the main menu and the main content widgets
        self.main_menu_widget = self.create_main_menu()
        self.main_content_widget = self.create_main_content()

        # Add widgets to the stacked widget
        self.stacked_widget.addWidget(self.main_menu_widget)
        self.stacked_widget.addWidget(self.main_content_widget)

        # Set the main content as the initial view
        self.stacked_widget.setCurrentWidget(self.main_content_widget)

    def create_main_menu(self):
        main_menu = QWidget()
        layout = QVBoxLayout(main_menu)

        button_style = """
            QPushButton {
                background-color: #2980b9; 
                color: white; 
                border-radius: 5px; 
                padding: 10px; 
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """

        title_label = QLabel("Welcome to Remove Background App")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)

        browse_button = QPushButton("Browse Images")
        browse_button.setStyleSheet(button_style)
        browse_button.clicked.connect(self.go_to_main_content)
        layout.addWidget(browse_button)

        set_import_button = QPushButton("Set Import Folder")
        set_import_button.setStyleSheet(button_style)
        set_import_button.clicked.connect(self.open_folder_settings)
        layout.addWidget(set_import_button)

        set_export_button = QPushButton("Set Export Folder")
        set_export_button.setStyleSheet(button_style)
        set_export_button.clicked.connect(self.open_folder_settings)
        layout.addWidget(set_export_button)

        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet(button_style)
        exit_button.clicked.connect(self.close_app)
        layout.addWidget(exit_button)

        layout.setAlignment(Qt.AlignCenter)
        return main_menu

    def create_main_content(self):
        main_content = QWidget()
        main_layout = QVBoxLayout(main_content)

        nav_bar = QWidget()
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_bar.setStyleSheet("background-color: #2c3e50; border-top-left-radius: 10px; border-top-right-radius: 10px;")

        self.title_label = QLabel("Remove Background by Pantong🧑🏻‍💻 and ChatGPT🤖")
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: white; padding: 5px;")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.settings_button = QPushButton("⚙️ SETTING FOLDER")
        self.settings_button.setFixedSize(150, 30)
        self.settings_button.setStyleSheet(""" 
            QPushButton {
                background-color: #f39c12; 
                color: white; 
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.settings_button.clicked.connect(self.open_folder_settings)

        self.close_button = QPushButton("❌")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet(""" 
            QPushButton {
                background-color: #FFFFFFFF; 
                color: white; 
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #F1F1F1FF;
            }
        """)
        self.close_button.clicked.connect(self.close_app)
        
            # Minimize Button
        self.minimize_button = QPushButton("─")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFFFF; 
                color: black; 
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #F1F1F1FF;
            }
        """)
        self.minimize_button.clicked.connect(self.show_minimized)

        nav_layout.addWidget(self.title_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.settings_button)
        nav_layout.addWidget(self.minimize_button)
        nav_layout.addWidget(self.close_button)

        main_layout.addWidget(nav_bar)

        content_layout = QHBoxLayout()

        self.left_scroll_area = QScrollArea()
        self.left_scroll_area.setWidgetResizable(True)
        self.left_scroll_content = QWidget()
        self.left_scroll_layout = QGridLayout(self.left_scroll_content)
        self.left_scroll_area.setWidget(self.left_scroll_content)

        self.right_scroll_area = QScrollArea()
        self.right_scroll_area.setWidgetResizable(True)
        self.right_scroll_content = QWidget()
        self.right_scroll_layout = QGridLayout(self.right_scroll_content)
        self.right_scroll_area.setWidget(self.right_scroll_content)

        content_layout.addWidget(self.left_scroll_area)
        content_layout.addWidget(self.right_scroll_area)

        main_layout.addLayout(content_layout)

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
        main_layout.addWidget(self.progress_bar)

        self.loading_label = QLabel("Ready")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.loading_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        main_layout.addWidget(self.loading_label)

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
        main_layout.addWidget(self.browse_button)

        self.remove_bg_button = QPushButton("Remove Background")
        self.remove_bg_button.setStyleSheet(button_style)
        self.remove_bg_button.clicked.connect(self.start_background_removal)
        main_layout.addWidget(self.remove_bg_button)

        self.open_folder_button = QPushButton("Open Export Folder")
        self.open_folder_button.setStyleSheet(button_style)
        self.open_folder_button.clicked.connect(self.open_export_folder)
        main_layout.addWidget(self.open_folder_button)

        return main_content

    def open_folder_settings(self):
        dialog = FolderSettingsDialog(self, self.import_folder, self.export_path)  # Pass self (main app)
        dialog.exec_()


    def go_to_main_content(self):
        self.stacked_widget.setCurrentWidget(self.main_content_widget)

    def go_to_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu_widget)

    def prompt_initial_settings(self):
        self.set_import_folder()
        self.set_export_folder()

    def show_minimized(self):
        self.showMinimized()  # ย่อหน้าต่างไปที่ taskbar
        
    def close_app(self):
        self.close()

    def browse_images(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Open Images", self.import_folder, "Image Files (*.png *.jpg *.jpeg)")
        if file_names:
            self.image_paths = file_names
            self.processed_images.clear()
            self.display_uploaded_images()

    def display_uploaded_images(self):
        for i in reversed(range(self.left_scroll_layout.count())): 
            widget = self.left_scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        display_size = 100

        for idx, image_path in enumerate(self.image_paths):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                label = QLabel()
                scaled_pixmap = pixmap.scaled(display_size, display_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                label.setPixmap(scaled_pixmap)
                label.setFixedSize(display_size, display_size)
                self.left_scroll_layout.addWidget(label, idx // 2, idx % 2)

        self.loading_label.setText("Ready")

    def start_background_removal(self):
        if self.image_paths:
            self.loading_label.setText("Removing background, please wait...")
            self.loading_label.setStyleSheet("color: #e67e22;")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

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

    def update_ui_after_removal(self, status, output_file):
        if status == "success":
            self.processed_images.append(output_file)
            self.display_processed_images()
        elif status == "done":
            self.progress_bar.setVisible(False)
            self.loading_label.setText("Backgrounds removed successfully!")
            self.loading_label.setStyleSheet("color: #27ae60;")
        else:
            self.loading_label.setText("Error processing images.")
            self.loading_label.setStyleSheet("color: #e74c3c;")

    def display_processed_images(self):
        for i in reversed(range(self.right_scroll_layout.count())): 
            widget = self.right_scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        display_size = 100

        for idx, processed_image in enumerate(self.processed_images):
            pixmap = QPixmap(processed_image)
            if not pixmap.isNull():
                label = QLabel()
                scaled_pixmap = pixmap.scaled(display_size, display_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                label.setPixmap(scaled_pixmap)
                label.setFixedSize(display_size, display_size)
                self.right_scroll_layout.addWidget(label, idx // 2, idx % 2)

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
