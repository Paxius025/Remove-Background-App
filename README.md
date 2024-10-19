
# 🖼️ Remove Background App
Welcome to the **Remove Background App**! This application is designed to remove backgrounds from images using Python and PyQt5. The app features a user-friendly interface and allows you to browse, select, and process images seamlessly.

## 📋 Project Details

- **Language**: Python 🐍
- **Framework**: PyQt5 🖥️
- **Image Processing**: Pillow and rembg libraries 📸

## 🚀 Features

- **Easy-to-use GUI**: Drag-and-drop functionality, clean and modern UI with styled buttons and labels.
- **Image Browsing**: Quickly browse images from your system and display them within the app.
- **Background Removal**: Process images with one click to remove backgrounds using the rembg library.
- **Export Location**: Set and open export folders directly from the app.
- **Progress Animation**: Displays a progress bar while processing images for better user experience.

## 🛠️ Setup Instructions

Follow these steps to set up and run the project locally:

### 1. Clone the Repository

```bash
git clone https://github.com/Paxius025/Remove-Background-App.git
cd remove-background-app
```

### 2. Create and Activate a Virtual Environment

```bash
# Windows
python -m venv env
env\Scripts\activate
```

```bash
# macOS/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Requirements

Ensure you have a clean environment and install the necessary packages:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python ui.py
```

### 5. Build the Executable (Optional)

To build an executable version of the app:

```bash
pyinstaller --onefile --windowed --name removeBg --icon=assets/favicon.ico ui.py
```

After building, you can find the executable in the \`dist\` folder.

## 📂 File Structure

```bash
remove-background-app/
├── env/
├── build/
├── dist/
├── __pycache__/
├── ui.py
├── utils.py
├── README.MD
```

- **env/**: Virtual environment folder (excluded from Git).
- **build/** and **dist/**: Output folders for PyInstaller.
- **\_\_pycache\_\_/**: Python bytecode cache (excluded from Git).
- **ui.py**: The main application script containing the PyQt5 UI.
- **utils.py**: Utility functions, including background removal logic.
- **requirements.txt**: List of dependencies needed for the project.

## 📝 Important Notes

- Make sure to use Python 3.8 or later for compatibility.
- If any modules are missing, add them to \`requirements.txt\` and reinstall.

## 📧 Support

If you have any questions or issues, feel free to open an issue on GitHub or reach out via email.

**Happy coding!** 🚀
