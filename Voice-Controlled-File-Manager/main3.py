import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import pyttsx3
import speech_recognition as sr
from PIL import Image, ImageTk
import time
import threading
from gtts import gTTS
import pygame
import tempfile

# Initialize pygame for audio playback
pygame.mixer.init()

# Enhanced Language configuration with better Hindi support
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
        },
        "phrases": {
            "ready": "Ready",
            "listening": "Listening for command",
            "processing": "Processing",
            "no_speech": "I didn't hear anything. Please try again.",
            "not_understood": "I didn't understand that. Please try again.",
            "service_error": "Sorry, I'm having trouble accessing the speech service.",
            "general_error": "An error occurred",
            "folder_opened": "Folder opened successfully",
            "file_opened": "File opened successfully",
            "open_error": "Cannot open",
            "no_previous": "No previous directory to return to",
            "renamed": "renamed successfully",
            "rename_failed": "Failed to rename",
            "rename_canceled": "Rename operation canceled",
            "copied": "copied to clipboard",
            "moved": "moved to clipboard",
            "deleted": "deleted successfully",
            "delete_failed": "Failed to delete",
            "preview_opened": "Preview opened",
            "preview_not_supported": "Preview not supported for this file type",
            "pasted": "Item pasted successfully",
            "paste_failed": "Failed to paste item",
            "clipboard_empty": "Clipboard is empty",
            "dir_changed": "Directory changed successfully",
            "folder_created": "Folder created successfully",
            "folder_failed": "Failed to create folder",
            "folder_canceled": "Folder creation canceled",
            "file_created": "File created successfully",
            "file_failed": "Failed to create file",
            "file_canceled": "File creation canceled",
            "command_not_recognized": "Command not recognized. Please try again",
            "select_item": "Please select an item",
            "select_file": "Please select a file",
            "select_folder": "Please select a folder",
            "say_filename": "Please say the file name you want to open",
            "say_foldername": "Please say the folder name you want to open",
            "no_results": "No results found",
            "using_online": "Using online speech synthesis",
            "language_changed": "Language changed to English",
            "searching": "Searching for: {}"
        }
    },
    "Hindi": {
        "code": "hi-IN",
        "voice_name": "hindi",
        "commands": {
            "open_file": "फाइल खोलो",
            "open_folder": "फोल्डर खोलो",
            "rename": "नाम बदलो",
            "copy": "कॉपी करो",
            "move": "मूव करो",
            "delete": "डिलीट करो",
            "preview": "प्रीव्यू",
            "back": "पीछे जाओ",
            "paste": "पेस्ट करो",
            "search": "खोजो",
            "change_dir": "डायरेक्टरी बदलो",
            "create_folder": "फोल्डर बनाओ",
            "create_file": "फाइल बनाओ"
        },
        "phrases": {
            "ready": "तैयार",
            "listening": "कमांड सुन रहा हूँ",
            "processing": "प्रोसेसिंग",
            "no_speech": "मैंने कुछ नहीं सुना। कृपया फिर से कोशिश करें।",
            "not_understood": "मैं समझा नहीं। कृपया फिर से कोशिश करें।",
            "service_error": "क्षमा करें, मुझे स्पीच सर्विस तक पहुँचने में समस्या हो रही है।",
            "general_error": "एक त्रुटि हुई",
            "folder_opened": "फोल्डर सफलतापूर्वक खोला गया",
            "file_opened": "फाइल सफलतापूर्वक खोली गई",
            "open_error": "खोल नहीं सकता",
            "no_previous": "वापस जाने के लिए कोई पिछला डायरेक्टरी नहीं",
            "renamed": "सफलतापूर्वक नाम बदला गया",
            "rename_failed": "नाम बदलने में विफल",
            "rename_canceled": "नाम बदलने का ऑपरेशन रद्द",
            "copied": "क्लिपबोर्ड पर कॉपी किया गया",
            "moved": "क्लिपबोर्ड पर ले जाया गया",
            "deleted": "सफलतापूर्वक हटाया गया",
            "delete_failed": "हटाने में विफल",
            "preview_opened": "प्रीव्यू खोला गया",
            "preview_not_supported": "इस फाइल टाइप के लिए प्रीव्यू समर्थित नहीं है",
            "pasted": "आइटम सफलतापूर्वक पेस्ट किया गया",
            "paste_failed": "आइटम पेस्ट करने में विफल",
            "clipboard_empty": "क्लिपबोर्ड खाली है",
            "dir_changed": "डायरेक्टरी सफलतापूर्वक बदली गई",
            "folder_created": "फोल्डर सफलतापूर्वक बनाया गया",
            "folder_failed": "फोल्डर बनाने में विफल",
            "folder_canceled": "फोल्डर निर्माण रद्द",
            "file_created": "फाइल सफलतापूर्वक बनाई गई",
            "file_failed": "फाइल बनाने में विफल",
            "file_canceled": "फाइल निर्माण रद्द",
            "command_not_recognized": "कमांड पहचाना नहीं गया। कृपया फिर से कोशिश करें।",
            "select_item": "कृपया कोई आइटम चुनें",
            "select_file": "कृपया कोई फाइल चुनें",
            "select_folder": "कृपया कोई फोल्डर चुनें",
            "say_filename": "कृपया उस फाइल का नाम बताएं जिसे आप खोलना चाहते हैं",
            "say_foldername": "कृपया उस फोल्डर का नाम बताएं जिसे आप खोलना चाहते हैं",
            "no_results": "कोई परिणाम नहीं मिला",
            "using_online": "ऑनलाइन वाक् संश्लेषण का उपयोग कर रहा हूँ",
            "language_changed": "भाषा हिंदी में बदली गई",
            "searching": "खोज रहा हूँ: {}"
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
def search_file(query, path, search_type="both"):
    results = []
    for item in os.listdir(path):
        abspath = os.path.join(path, item)
        if query.lower() in item.lower():
            if search_type == "both" or \
               (search_type == "file" and os.path.isfile(abspath)) or \
               (search_type == "folder" and os.path.isdir(abspath)):
                results.append(abspath)
        if os.path.isdir(abspath):
            try:
                sub_results = search_file(query, abspath, search_type)
                results.extend(sub_results)
            except PermissionError:
                continue
    return results

# Voice search function with file and folder separation
def voice_search(query, search_type="file"):
    results = search_file(query, current_dir.get(), search_type)
    if results:
        # Return the first result that matches the search type
        for result in results:
            if search_type == "file" and os.path.isfile(result):
                return result
            elif search_type == "folder" and os.path.isdir(result):
                return result
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
        speak("folder_opened")
    elif item_type == 'file' and os.path.isfile(file_path):
        try:
            os.startfile(file_path)
            speak("file_opened")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")
            speak("open_error")
    else:
        messagebox.showwarning("Error", f"Cannot open {item_type}: {file_path}")
        speak("open_error")

# Function to go back to the previous directory
def go_back():
    if previous_dir:
        last_dir = previous_dir.pop()  # Get the last directory
        current_dir.set(last_dir)
        populate_treeview(last_dir)
        speak("folder_opened")
    else:
        speak("no_previous")

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
            speak("renamed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename: {e}")
            speak("rename_failed")
    else:
        speak("rename_canceled")

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
    
    speak("copied")

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
    
    speak("moved")

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
            speak("deleted")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")
            speak("delete_failed")

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
        speak("select_file")
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
            
            speak("preview_opened")
            
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
            
            speak("preview_opened")
            
        elif ext in ['.pdf']:
            # Open PDF with default viewer
            os.startfile(path)
            speak("preview_opened")
            
        else:
            speak("preview_not_supported")
            
    except Exception as e:
        messagebox.showerror("Error", f"Cannot preview file: {e}")
        speak("preview_not_supported")

# Function to paste clipboard item
def paste_item():
    if not clipboard:
        speak("clipboard_empty")
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
            speak("pasted")
        elif operation == 'move':
            shutil.move(source, dest_path)
            clipboard.clear()  # Clear clipboard after move
            speak("pasted")
        
        populate_treeview(current_dir.get())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to paste: {e}")
        speak("paste_failed")

# Function to change directory
def change_directory():
    new_dir = filedialog.askdirectory(initialdir=current_dir.get())
    if new_dir:
        previous_dir.append(current_dir.get())
        current_dir.set(new_dir)
        populate_treeview(new_dir)
        speak("dir_changed")

# Function to create new folder
def create_folder():
    folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
    if folder_name and folder_name.strip():
        folder_path = os.path.join(current_dir.get(), folder_name.strip())
        try:
            os.makedirs(folder_path, exist_ok=True)
            populate_treeview(current_dir.get())
            speak("folder_created")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folder: {e}")
            speak("folder_failed")
    else:
        speak("folder_canceled")

# Function to create new file
def create_file():
    file_name = simpledialog.askstring("Create File", "Enter file name (with extension):")
    if file_name and file_name.strip():
        file_path = os.path.join(current_dir.get(), file_name.strip())
        try:
            with open(file_path, 'w') as f:
                pass  # Create empty file
            populate_treeview(current_dir.get())
            speak("file_created")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create file: {e}")
            speak("file_failed")
    else:
        speak("file_canceled")

# Improved speech function with better Hindi support
def speak(phrase_key, *format_args):
    lang = current_language.get()
    lang_data = LANGUAGES.get(lang, LANGUAGES["English"])
    text = lang_data["phrases"].get(phrase_key, phrase_key)
    
    # Format text if arguments are provided
    if format_args:
        text = text.format(*format_args)
    
    lang_code = lang_data['code'].split('-')[0]  # Extract base language code (en/hi)
    
    # Update status bar
    status_var.set(text)
    
    # For non-English, use gTTS directly for better accuracy
    if lang != "English":
        try:
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmpfile:
                tts = gTTS(text=text, lang=lang_code)
                tts.save(tmpfile.name)
                tmpfile.close()
                
                # Play audio with pygame
                pygame.mixer.music.load(tmpfile.name)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                # Delete temporary file
                os.unlink(tmpfile.name)
            return
        except Exception as e:
            print(f"gTTS Error: {e}")
    
    # For English, use pyttsx3 (offline)
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if lang_data['voice_name'] in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"pyttsx3 Error: {e}")
        # Fallback to gTTS if pyttsx3 fails
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmpfile:
                tts = gTTS(text=text, lang=lang_code)
                tts.save(tmpfile.name)
                tmpfile.close()
                
                pygame.mixer.music.load(tmpfile.name)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                os.unlink(tmpfile.name)
        except Exception as e:
            print(f"gTTS Fallback Error: {e}")

# Function to reset the listening state
def set_listening_finished():
    global is_listening
    is_listening = False
    status_var.set(LANGUAGES[current_language.get()]["phrases"]["ready"])

# Function to start voice command listening (FIXED)
def start_listening():
    global is_listening
    if is_listening:
        return
        
    is_listening = True
    status_var.set(LANGUAGES[current_language.get()]["phrases"]["listening"])
    
    def listen_thread():
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio, language=LANGUAGES[current_language.get()]["code"])
                root.after(0, lambda: process_command(text))
            except sr.WaitTimeoutError:
                root.after(0, lambda: speak("no_speech"))
            except sr.UnknownValueError:
                root.after(0, lambda: speak("not_understood"))
            except sr.RequestError as e:
                root.after(0, lambda: speak("service_error"))
                print(f"API Error: {e}")
            except Exception as e:
                root.after(0, lambda: speak("general_error"))
                print(f"Error: {e}")
            finally:
                root.after(0, set_listening_finished)
    
    threading.Thread(target=listen_thread, daemon=True).start()

# Function to process voice commands
def process_command(command):
    lang = current_language.get()
    commands = LANGUAGES[lang]["commands"]
    command = command.lower()
    
    # Get the current language's command set
    cmd_set = LANGUAGES[lang]["commands"]
    
    # Command processing logic
    if cmd_set["open_file"] in command:
        if "search" in command or "find" in command:
            speak("say_filename")
            start_listening()
        else:
            open_item('file')
    elif cmd_set["open_folder"] in command:
        if "search" in command or "find" in command:
            speak("say_foldername")
            start_listening()
        else:
            open_item('folder')
    elif cmd_set["rename"] in command:
        rename_item()
    elif cmd_set["copy"] in command:
        copy_item()
    elif cmd_set["move"] in command:
        move_item()
    elif cmd_set["delete"] in command:
        delete_item()
    elif cmd_set["preview"] in command:
        preview_file()
    elif cmd_set["back"] in command:
        go_back()
    elif cmd_set["paste"] in command:
        paste_item()
    elif cmd_set["search"] in command:
        process_search_command(command)
    elif cmd_set["change_dir"] in command:
        change_directory()
    elif cmd_set["create_folder"] in command:
        create_folder()
    elif cmd_set["create_file"] in command:
        create_file()
    else:
        # Handle search commands
        if cmd_set["search"] in command:
            process_search_command(command)
        else:
            speak("command_not_recognized")

# Function to process search commands
def process_search_command(command):
    lang = current_language.get()
    commands = LANGUAGES[lang]["commands"]
    
    # Extract search query
    query = command.replace(commands["search"], "").strip()
    
    if not query:
        if commands["open_file"] in command:
            speak("say_filename")
            start_listening()
            return
        elif commands["open_folder"] in command:
            speak("say_foldername")
            start_listening()
            return
    
    speak("searching", query)
    
    # Determine search type
    search_type = "both"
    if commands["open_file"] in command:
        search_type = "file"
    elif commands["open_folder"] in command:
        search_type = "folder"
    
    # Perform search
    results = search_file(query, current_dir.get(), search_type)
    
    if results:
        # Open first result
        if os.path.isdir(results[0]):
            open_item('folder', results[0])
        else:
            open_item('file', results[0])
    else:
        speak("no_results")

# Function to update UI language feedback
def update_language_feedback():
    lang = current_language.get()
    speak("language_changed")
    status_var.set(LANGUAGES[lang]["phrases"]["ready"])

# Create buttons with icons
def create_button(parent, text, command, icon=None):
    btn = ttk.Button(parent, text=text, command=command)
    btn.pack(side=tk.LEFT, padx=5)
    return btn

# Create all buttons
buttons = [
    ("🗣️ Voice Command", lambda: start_listening()),
    ("📂 Open Folder", lambda: open_item('folder')),
    ("📄 Open File", lambda: open_item('file')),
    ("🔙 Back", go_back),
    ("✏️ Rename", rename_item),
    ("📋 Copy", copy_item),
    ("✂️ Move", move_item),
    ("🧹 Delete", delete_item),
    ("👁️ Preview", preview_file),
    ("📎 Paste", paste_item),
    ("🔍 Search", lambda: process_search_command("")),
    ("📁 Create Folder", create_folder),
    ("📝 Create File", create_file),
    ("🔄 Change Dir", change_directory)
]

for text, cmd in buttons:
    create_button(button_frame, text, cmd)

# Bind double click event
tree.bind("<Double-1>", on_double_click)

# Initial population
populate_treeview(current_dir.get())

# Set initial status
status_var.set(LANGUAGES[current_language.get()]["phrases"]["ready"])

# Run the application
root.mainloop()