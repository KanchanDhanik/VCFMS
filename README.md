# Voice-Controlled File Explorer

A Python-based file explorer with voice-command support for seamless file management. This application allows users to perform essential file and folder operations using an intuitive GUI and voice recognition.

---

## Features

- **Voice Commands**: Open, rename, delete, copy, move files or folders, and more.
- **File Preview**: Supports text and image previews.
- **Clipboard Management**: Copy and paste items between directories.
- **Directory Navigation**: Easily change directories or go back.
- **GUI Interface**: Modern, dark-themed treeview for file/folder display.

---

## Technologies Used

- **Tkinter**: GUI development.
- **Pyttsx3**: Text-to-speech for operation feedback.
- **SpeechRecognition**: Voice command parsing.
- **PIL (Pillow)**: For image file preview.
- **Shutil**: File and folder operations.

---

## How to Use

### 1. Clone the Repository
```bash
git clone https://github.com/sms32/Voice-Controlled-File-Manager.git
cd Voice-Controlled-File-Manager
```

### 2. Install Dependencies
```bash
pip install pyttsx3 SpeechRecognition pillow
```

### 3. Run the Application
```bash
python main.py
```

### 4. Usage

- Use GUI buttons or double-click on items for file/folder management.
- Issue voice commands for operations like opening, renaming, copying, or deleting files and folders.

---

## Sample Voice Commands

### 1. File Operations

- **Open a file**: "Open file report.txt"
- **Rename a file**: "Rename file notes.txt"
- **Delete a file**: "Delete file data.csv"
- **Copy a file**: "Copy file image.jpg"
- **Paste**: "Paste"

### 2. Folder Operations

- **Open a folder**: "Open folder Documents"
- **Rename a folder**: "Rename folder Projects"
- **Delete a folder**: "Delete folder Downloads"

### 3. Navigation

- **Go back**: "Back"
- **Change directory to D drive**: "Change directory to D"
- **Change directory to C drive**: "Change directory to C"

