import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import pyttsx3
import speech_recognition as sr
from PIL import Image, ImageTk
import subprocess
import json
import time
import threading
import requests
from gtts import gTTS
import pygame
import tempfile
import locale

# Initialize pygame for audio playback
pygame.mixer.init()

# Language configuration
LANGUAGES = {
    "English": {
        "code": "en-US",
        "voice_name": "english",
        "commands": {
            "open_file": "open file",
            "open_folder": "open folder",
            "rename": "rename",
            "copy": "copy",
            "move": "move",
            "delete": "delete",
            "preview": "preview",
            "back": "back",
            "paste": "paste",
            "search": "search",
            "change_dir": "change directory",
            "create_folder": "create folder",
            "create_file": "create file"
        }
    },
    "Spanish": {
        "code": "es-ES",
        "voice_name": "spanish",
        "commands": {
            "open_file": "abrir archivo",
            "open_folder": "abrir carpeta",
            "rename": "renombrar",
            "copy": "copiar",
            "move": "mover",
            "delete": "eliminar",
            "preview": "vista previa",
            "back": "atrás",
            "paste": "pegar",
            "search": "buscar",
            "change_dir": "cambiar directorio",
            "create_folder": "crear carpeta",
            "create_file": "crear archivo"
        }
    },
    "French": {
        "code": "fr-FR",
        "voice_name": "french",
        "commands": {
            "open_file": "ouvrir fichier",
            "open_folder": "ouvrir dossier",
            "rename": "renommer",
            "copy": "copier",
            "move": "déplacer",
            "delete": "supprimer",
            "preview": "aperçu",
            "back": "retour",
            "paste": "coller",
            "search": "rechercher",
            "change_dir": "changer répertoire",
            "create_folder": "créer dossier",
            "create_file": "créer fichier"
        }
    },
    "German": {
        "code": "de-DE",
        "voice_name": "german",
        "commands": {
            "open_file": "datei öffnen",
            "open_folder": "ordner öffnen",
            "rename": "umbenennen",
            "copy": "kopieren",
            "move": "verschieben",
            "delete": "löschen",
            "preview": "vorschau",
            "back": "zurück",
            "paste": "einfügen",
            "search": "suchen",
            "change_dir": "verzeichnis ändern",
            "create_folder": "ordner erstellen",
            "create_file": "datei erstellen"
        }
    },
    "Hindi": {
        "code": "hi-IN",
        "voice_name": "hindi",
        "commands": {
            "open_file": "फ़ाइल खोलें",
            "open_folder": "फ़ोल्डर खोलें",
            "rename": "नाम बदलें",
            "copy": "कॉपी करें",
            "move": "ले जाएँ",
            "delete": "हटाएँ",
            "preview": "पूर्वावलोकन",
            "back": "पीछे",
            "paste": "पेस्ट करें",
            "search": "खोजें",
            "change_dir": "डायरेक्टरी बदलें",
            "create_folder": "फ़ोल्डर बनाएँ",
            "create_file": "फ़ाइल बनाएँ"
        }
    }
}

# Main window setup
root = tk.Tk()
root.title("🌐 Voice Controlled File Explorer")
root.geometry("1100x700")
root.config(bg="#2b2b2b")

# Global Variables
current_dir = tk.StringVar()
current_dir.set(os.path.expanduser("~"))
previous_dir = []  # To keep track of the directory history
clipboard = {}  # For storing copied/moved items (path and type)
current_language = tk.StringVar(value="English")
is_listening = False
recognizer = sr.Recognizer()

# Create a modern style
style = ttk.Style()
style.theme_use("clam")

# Configure colors
bg_color = "#2b2b2b"
fg_color = "#e8e8e8"
accent_color = "#4CAF50"
button_color = "#3c3c3c"
tree_bg = "#333333"
tree_select = "#565656"

# Configure styles
style.configure("TFrame", background=bg_color)
style.configure("TLabel", background=bg_color, foreground=fg_color)
style.configure("TButton", 
                background=button_color, 
                foreground=fg_color,
                font=("Arial", 10, "bold"),
                padding=8,
                borderwidth=0)
style.map("TButton", 
          background=[("active", "#4d4d4d"), ("pressed", "#3a3a3a")],
          foreground=[("active", "white")])

style.configure("Treeview", 
                background=tree_bg,
                foreground=fg_color,
                fieldbackground=tree_bg,
                rowheight=28,
                font=("Arial", 10))
style.map("Treeview", background=[("selected", tree_select)])

style.configure("Treeview.Heading", 
                background="#333",
                foreground="#e8e8e8",
                font=("Arial", 11, "bold"),
                padding=8)

style.configure("TCombobox", 
                fieldbackground=tree_bg,
                background=tree_bg,
                foreground=fg_color,
                selectbackground=tree_select)

# Top frame for language selection
top_frame = ttk.Frame(root)
top_frame.pack(fill=tk.X, padx=10, pady=10)

ttk.Label(top_frame, text="Select Language:").pack(side=tk.LEFT, padx=(0, 10))
lang_combo = ttk.Combobox(top_frame, 
                          textvariable=current_language,
                          values=list(LANGUAGES.keys()),
                          state="readonly")
lang_combo.pack(side=tk.LEFT)
lang_combo.bind("<<ComboboxSelected>>", lambda e: update_language_feedback())

# Status bar
status_var = tk.StringVar(value="Ready")
status_bar = ttk.Label(root, 
                      textvariable=status_var,
                      relief=tk.SUNKEN, 
                      anchor=tk.W,
                      font=("Arial", 9),
                      background="#333",
                      foreground="#e8e8e8")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Treeview to display files/folders
tree_frame = ttk.Frame(root)
tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

# Create scrollbar
scrollbar = ttk.Scrollbar(tree_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=("FullPath", "Type", "Size", "Modified"), 
                   show="headings", yscrollcommand=scrollbar.set)
tree.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=tree.yview)

# Configure columns
tree.heading("FullPath", text="Name", anchor=tk.W)
tree.heading("Type", text="Type", anchor=tk.CENTER)
tree.heading("Size", text="Size", anchor=tk.CENTER)
tree.heading("Modified", text="Modified", anchor=tk.CENTER)

tree.column("FullPath", anchor=tk.W, width=400)
tree.column("Type", anchor=tk.CENTER, width=150)
tree.column("Size", anchor=tk.CENTER, width=100)
tree.column("Modified", anchor=tk.CENTER, width=150)

# Button frame
button_frame = ttk.Frame(root)
button_frame.pack(fill=tk.X, padx=10, pady=10)

# Populate the treeview with files/folders
def populate_treeview(path):
    tree.delete(*tree.get_children())
    try:
        for item in os.listdir(path):
            abspath = os.path.join(path, item)
            try:
                if os.path.isdir(abspath):
                    item_type = "Folder"
                    size = ""
                else:
                    item_type = "File"
                    size = f"{os.path.getsize(abspath) / 1024:.1f} KB"
                
                modified = os.path.getmtime(abspath)
                modified_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(modified))
                
                tree.insert('', 'end', values=(item, item_type, size, modified_str), 
                           tags=('folder' if item_type == "Folder" else 'file'))
            except PermissionError:
                continue
        # Configure tags for folder and file
        tree.tag_configure('folder', foreground='#64B5F6')
        tree.tag_configure('file', foreground=fg_color)
        
        # Update status
        status_var.set(f"Showing: {path}")
    except Exception as e:
        status_var.set(f"Error: {str(e)}")

# Function to handle double-click event and open file/folder
def on_double_click(event):
    selected_item = tree.focus()
    if not selected_item:
        return
    item_values = tree.item(selected_item, 'values')
    if not item_values:
        return
        
    item_name = item_values[0]
    file_path = os.path.join(current_dir.get(), item_name)
    
    if os.path.isdir(file_path):
        open_item('folder', file_path)
    elif os.path.isfile(file_path):
        open_item('file', file_path)

# Search for file or folder
def search_file(query, path):
    for item in os.listdir(path):
        abspath = os.path.join(path, item)
        if query.lower() in item.lower():
            return abspath
        if os.path.isdir(abspath):
            try:
                result = search_file(query, abspath)
                if result:
                    return result
            except PermissionError:
                continue
    return None

# Voice search function with file and folder separation
def voice_search(query, search_type="file"):
    result = search_file(query, current_dir.get())
    if result:
        if search_type == "file" and os.path.isfile(result):
            return result
        elif search_type == "folder" and os.path.isdir(result):
            return result
    else:
        speak("No results found.")
        return None

# Function to open a file or folder
def open_item(item_type, path=None):
    if path is None:
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "No file or folder selected")
            return

        item_values = tree.item(selected_item, 'values')
        if not item_values:
            return
            
        item_name = item_values[0]
        file_path = os.path.join(current_dir.get(), item_name)
    else:
        file_path = path

    if item_type == 'folder' and os.path.isdir(file_path):
        previous_dir.append(current_dir.get())  # Save current directory
        current_dir.set(file_path)
        populate_treeview(file_path)
        speak("Folder opened successfully.")
    elif item_type == 'file' and os.path.isfile(file_path):
        try:
            os.startfile(file_path)
            speak("File opened successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")
            speak(f"Cannot open file: {e}")
    else:
        messagebox.showwarning("Error", f"Cannot open {item_type}: {file_path}")
        speak(f"Cannot open {item_type}.")

# Function to go back to the previous directory
def go_back():
    if previous_dir:
        last_dir = previous_dir.pop()  # Get the last directory
        current_dir.set(last_dir)
        populate_treeview(last_dir)
        speak("Returned to the previous folder.")
    else:
        speak("No previous directory to return to.")

# Function to rename file or folder
def rename_item(item_type):
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file or folder selected")
        return
        
    item_values = tree.item(selected_item, 'values')
    if not item_values:
        return
        
    item_name = item_values[0]
    old_path = os.path.join(current_dir.get(), item_name)
    
    new_name = simpledialog.askstring("Rename", f"Enter new name for {item_name}:")
    if new_name and new_name.strip():
        new_path = os.path.join(current_dir.get(), new_name.strip())
        try:
            os.rename(old_path, new_path)
            populate_treeview(current_dir.get())
            speak(f"{item_type} renamed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename: {e}")
            speak(f"Failed to rename {item_type}.")
    else:
        speak("Rename operation canceled.")

# Function to copy file or folder
def copy_item():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file or folder selected")
        return
        
    item_values = tree.item(selected_item, 'values')
    if not item_values:
        return
        
    item_name = item_values[0]
    path = os.path.join(current_dir.get(), item_name)
    item_type = "folder" if os.path.isdir(path) else "file"
    
    clipboard.clear()
    clipboard['path'] = path
    clipboard['type'] = 'copy'
    clipboard['name'] = item_name
    
    speak(f"{item_type} copied to clipboard.")

# Function to move file or folder
def move_item():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file or folder selected")
        return
        
    item_values = tree.item(selected_item, 'values')
    if not item_values:
        return
        
    item_name = item_values[0]
    path = os.path.join(current_dir.get(), item_name)
    item_type = "folder" if os.path.isdir(path) else "file"
    
    clipboard.clear()
    clipboard['path'] = path
    clipboard['type'] = 'move'
    clipboard['name'] = item_name
    
    speak(f"{item_type} moved to clipboard.")

# Function to delete file or folder
def delete_item():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file or folder selected")
        return
        
    item_values = tree.item(selected_item, 'values')
    if not item_values:
        return
        
    item_name = item_values[0]
    path = os.path.join(current_dir.get(), item_name)
    item_type = "folder" if os.path.isdir(path) else "file"
    
    confirm = messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete this {item_type}?\n{item_name}")
    if confirm:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            populate_treeview(current_dir.get())
            speak(f"{item_type} deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")
            speak(f"Failed to delete {item_type}.")

# Function to preview file
def preview_file():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file selected")
        return
        
    item_values = tree.item(selected_item, 'values')
    if not item_values:
        return
        
    item_name = item_values[0]
    path = os.path.join(current_dir.get(), item_name)
    
    if os.path.isdir(path):
        speak("Cannot preview folders. Please select a file.")
        return
        
    # Get file extension
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    
    try:
        if ext in ['.txt', '.py', '.java', '.c', '.cpp', '.html', '.css', '.js']:
            # Preview text files
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 characters
            preview_window = tk.Toplevel(root)
            preview_window.title(f"Preview: {item_name}")
            preview_window.geometry("600x400")
            
            text = tk.Text(preview_window, wrap='word')
            text.insert('1.0', content)
            text.config(state='disabled')
            text.pack(fill='both', expand=True)
            
            speak("Text preview opened.")
            
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # Preview images
            preview_window = tk.Toplevel(root)
            preview_window.title(f"Preview: {item_name}")
            
            img = Image.open(path)
            img.thumbnail((800, 600))  # Resize for preview
            photo = ImageTk.PhotoImage(img)
            
            label = tk.Label(preview_window, image=photo)
            label.image = photo  # Keep a reference
            label.pack()
            
            speak("Image preview opened.")
            
        elif ext in ['.pdf']:
            # Open PDF with default viewer
            os.startfile(path)
            speak("Opening PDF file.")
            
        else:
            speak("Preview not supported for this file type.")
            
    except Exception as e:
        messagebox.showerror("Error", f"Cannot preview file: {e}")
        speak(f"Cannot preview file: {e}")

# Function to paste clipboard item
def paste_item():
    if not clipboard:
        speak("Clipboard is empty.")
        return
        
    source = clipboard['path']
    operation = clipboard['type']
    name = clipboard['name']
    destination = current_dir.get()
    dest_path = os.path.join(destination, name)
    
    try:
        if operation == 'copy':
            if os.path.isdir(source):
                shutil.copytree(source, dest_path)
            else:
                shutil.copy2(source, dest_path)
            speak("Item copied successfully.")
        elif operation == 'move':
            shutil.move(source, dest_path)
            clipboard.clear()  # Clear clipboard after move
            speak("Item moved successfully.")
        
        populate_treeview(current_dir.get())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to paste: {e}")
        speak(f"Failed to paste item: {e}")

# Function to change directory
def change_directory():
    new_dir = filedialog.askdirectory(initialdir=current_dir.get())
    if new_dir:
        previous_dir.append(current_dir.get())
        current_dir.set(new_dir)
        populate_treeview(new_dir)
        speak("Directory changed successfully.")

# Function to create new folder
def create_folder():
    folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
    if folder_name and folder_name.strip():
        folder_path = os.path.join(current_dir.get(), folder_name.strip())
        try:
            os.makedirs(folder_path, exist_ok=True)
            populate_treeview(current_dir.get())
            speak("Folder created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folder: {e}")
            speak(f"Failed to create folder: {e}")
    else:
        speak("Folder creation canceled.")

# Function to create new file
def create_file():
    file_name = simpledialog.askstring("Create File", "Enter file name (with extension):")
    if file_name and file_name.strip():
        file_path = os.path.join(current_dir.get(), file_name.strip())
        try:
            with open(file_path, 'w') as f:
                pass  # Create empty file
            populate_treeview(current_dir.get())
            speak("File created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create file: {e}")
            speak(f"Failed to create file: {e}")
    else:
        speak("File creation canceled.")

# Function to speak text using gTTS as fallback
def speak(text):
    lang = current_language.get()
    lang_code = LANGUAGES[lang]['code']
    
    try:
        # Try pyttsx3 first
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        lang_prefix = lang_code[:2].lower()
        
        # Try to find matching voice
        for voice in voices:
            if lang_prefix in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        # Fallback to gTTS if pyttsx3 fails
        try:
            status_var.set("Using online speech synthesis...")
            tts = gTTS(text=text, lang=lang_code[:2], slow=False)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
                tts.save(temp_file)
            
            # Play the audio
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Clean up
            os.unlink(temp_file)
        except Exception as e2:
            messagebox.showerror("Speech Error", f"Failed to speak: {e2}")
            status_var.set(f"Speech error: {e2}")

# Function to listen for voice commands with better error handling
def listen():
    global is_listening
    if is_listening:
        return
        
    is_listening = True
    status_var.set("Listening...")
    root.update()
    
    def recognition_thread():
        global is_listening  # Changed from nonlocal to global
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                speak("Listening for command")
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                
                status_var.set("Processing...")
                root.update()
                
                lang_code = LANGUAGES[current_language.get()]['code']
                command = r.recognize_google(audio, language=lang_code)
                status_var.set(f"Command: {command}")
                process_voice_command(command.lower())
            except sr.WaitTimeoutError:
                status_var.set("No speech detected")
                speak("I didn't hear anything. Please try again.")
            except sr.UnknownValueError:
                status_var.set("Could not understand audio")
                speak("I didn't understand that. Please try again.")
            except sr.RequestError as e:
                status_var.set(f"Request error: {e}")
                speak("Sorry, I'm having trouble accessing the speech service.")
            except Exception as e:
                status_var.set(f"Error: {str(e)}")
                speak(f"An error occurred: {str(e)}")
            finally:
                is_listening = False
                status_var.set("Ready")
    
    # Start recognition in a separate thread
    threading.Thread(target=recognition_thread, daemon=True).start()

# Function to process voice commands with fuzzy matching
def process_voice_command(command):
    lang = current_language.get()
    commands = LANGUAGES[lang]['commands']
    
    # Find the best matching command
    best_match = None
    best_score = 0
    
    for key, phrase in commands.items():
        # Simple fuzzy matching by checking if command contains phrase
        if phrase in command:
            best_match = key
            break
        
        # Calculate match score
        score = sum(1 for word in phrase.split() if word in command)
        if score > best_score:
            best_score = score
            best_match = key
    
    if not best_match:
        speak("Command not recognized. Please try again.")
        return
    
    # Execute the command
    if best_match == 'open_file':
        selected_item = tree.focus()
        if selected_item:
            item_values = tree.item(selected_item, 'values')
            if item_values and item_values[1] == "File":
                open_item('file')
            else:
                speak("Please select a file first.")
        else:
            # Voice search for file
            speak("Please say the file name you want to open.")
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    audio = r.listen(source, timeout=5)
                file_name = r.recognize_google(audio, language=LANGUAGES[lang]['code'])
                file_path = voice_search(file_name, "file")
                if file_path:
                    open_item('file', file_path)
            except:
                speak("Could not recognize file name.")
                
    elif best_match == 'open_folder':
        selected_item = tree.focus()
        if selected_item:
            item_values = tree.item(selected_item, 'values')
            if item_values and item_values[1] == "Folder":
                open_item('folder')
            else:
                speak("Please select a folder first.")
        else:
            # Voice search for folder
            speak("Please say the folder name you want to open.")
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    audio = r.listen(source, timeout=5)
                folder_name = r.recognize_google(audio, language=LANGUAGES[lang]['code'])
                folder_path = voice_search(folder_name, "folder")
                if folder_path:
                    open_item('folder', folder_path)
            except:
                speak("Could not recognize folder name.")
                
    elif best_match == 'rename':
        selected_item = tree.focus()
        if selected_item:
            item_values = tree.item(selected_item, 'values')
            if item_values:
                item_type = "folder" if item_values[1] == "Folder" else "file"
                rename_item(item_type)
        else:
            speak("Please select an item to rename.")
            
    elif best_match == 'copy':
        copy_item()
        
    elif best_match == 'move':
        move_item()
        
    elif best_match == 'delete':
        delete_item()
        
    elif best_match == 'preview':
        preview_file()
        
    elif best_match == 'back':
        go_back()
        
    elif best_match == 'paste':
        paste_item()
        
    elif best_match == 'search':
        # Implement search functionality
        speak("Please use the search bar at the top right.")
        
    elif best_match == 'change_dir':
        change_directory()
        
    elif best_match == 'create_folder':
        create_folder()
        
    elif best_match == 'create_file':
        create_file()
        
    else:
        speak("Command not recognized. Please try again.")

# Function to update UI based on language selection
def update_language_feedback():
    lang = current_language.get()
    speak(f"Language changed to {lang}")

# Create buttons
btn_listen = ttk.Button(button_frame, text="🎤 Voice Command", command=listen)
btn_listen.pack(side=tk.LEFT, padx=5)

btn_back = ttk.Button(button_frame, text="↩ Back", command=go_back)
btn_back.pack(side=tk.LEFT, padx=5)

btn_open = ttk.Button(button_frame, text="📂 Open", command=lambda: open_item('file'))
btn_open.pack(side=tk.LEFT, padx=5)

btn_rename = ttk.Button(button_frame, text="✏ Rename", command=lambda: rename_item('file'))
btn_rename.pack(side=tk.LEFT, padx=5)

btn_copy = ttk.Button(button_frame, text="📋 Copy", command=copy_item)
btn_copy.pack(side=tk.LEFT, padx=5)

btn_move = ttk.Button(button_frame, text="✂ Move", command=move_item)
btn_move.pack(side=tk.LEFT, padx=5)

btn_paste = ttk.Button(button_frame, text="📎 Paste", command=paste_item)
btn_paste.pack(side=tk.LEFT, padx=5)

btn_delete = ttk.Button(button_frame, text="🗑 Delete", command=delete_item)
btn_delete.pack(side=tk.LEFT, padx=5)

btn_preview = ttk.Button(button_frame, text="👁 Preview", command=preview_file)
btn_preview.pack(side=tk.LEFT, padx=5)

btn_new_folder = ttk.Button(button_frame, text="📁 New Folder", command=create_folder)
btn_new_folder.pack(side=tk.LEFT, padx=5)

btn_new_file = ttk.Button(button_frame, text="📄 New File", command=create_file)
btn_new_file.pack(side=tk.LEFT, padx=5)

# Search bar
search_frame = ttk.Frame(button_frame)
search_frame.pack(side=tk.RIGHT, padx=5)

search_entry = ttk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=(0, 5))

def on_search():
    query = search_entry.get()
    if query:
        result = voice_search(query)
        if result:
            if os.path.isfile(result):
                open_item('file', result)
            elif os.path.isdir(result):
                open_item('folder', result)

btn_search = ttk.Button(search_frame, text="🔍 Search", command=on_search)
btn_search.pack(side=tk.LEFT)

# Bind double click event
tree.bind("<Double-1>", on_double_click)

# Initial population
populate_treeview(current_dir.get())

# Start the main loop
root.mainloop()