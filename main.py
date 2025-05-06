import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import pyttsx3
import speech_recognition as sr
from PIL import Image, ImageTk
import subprocess

# Initialize voice engine
engine = pyttsx3.init()

# Main window setup
root = tk.Tk()
root.title("Voice Controlled File Explorer")
root.geometry("1000x600")
root.config(bg="#2b2b2b")

# Global Variables
current_dir = tk.StringVar()
current_dir.set(os.path.expanduser("~"))
previous_dir = []  # To keep track of the directory history
clipboard = {}  # For storing copied/moved items (path and type)

# Treeview to display files/folders
tree = ttk.Treeview(root, columns=("FullPath"), show="tree")
tree.pack(fill=tk.BOTH, expand=True)

# Set Treeview style for a modern look
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#333", fieldbackground="#333", foreground="white")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), foreground="#e8e8e8")
style.map('Treeview', background=[('selected', '#565656')])

# Populate the treeview with files/folders
def populate_treeview(path):
    tree.delete(*tree.get_children())
    for item in os.listdir(path):
        abspath = os.path.join(path, item)
        try:
            tree.insert('', 'end', text=item, values=[abspath], open=False)
        except PermissionError:
            continue
# Function to handle double-click event and open file/folder
def on_double_click(event):
    selected_item = tree.focus()
    if not selected_item:
        return
    file_path = tree.item(selected_item, 'values')[0]
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
        engine.say("No results found.")
        engine.runAndWait()
        return None

# Function to open a file or folder
def open_item(item_type, path=None):
    if path is None:
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "No file or folder selected")
            return

        file_path = tree.item(selected_item, 'values')[0]
    else:
        file_path = path

    if item_type == 'folder' and os.path.isdir(file_path):
        previous_dir.append(current_dir.get())  # Save current directory
        populate_treeview(file_path)
        current_dir.set(file_path)
        engine.say("Folder opened successfully.")
        engine.runAndWait()
    elif item_type == 'file' and os.path.isfile(file_path):
        os.startfile(file_path)
        engine.say("File opened successfully.")
        engine.runAndWait()
    else:
        messagebox.showwarning("Error", f"Cannot open {item_type}: {file_path}")
        engine.say(f"Cannot open {item_type}.")
        engine.runAndWait()

# Function to go back to the previous directory
def go_back():
    if previous_dir:
        last_dir = previous_dir.pop()  # Get the last directory
        populate_treeview(last_dir)
        current_dir.set(last_dir)
        engine.say("Returned to the previous folder.")
        engine.runAndWait()
    else:
        engine.say("No previous directory to return to.")
        engine.runAndWait()

# Function to rename file or folder
def rename_item(item_type):
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file or folder selected")
        return

    old_path = tree.item(selected_item, 'values')[0]
    new_name = simpledialog.askstring("Rename", "Enter new name:")
    
    if new_name:
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        try:
            os.rename(old_path, new_path)
            populate_treeview(current_dir.get())
            engine.say(f"{item_type.capitalize()} renamed successfully.")
            engine.runAndWait()
        except Exception as e:
            messagebox.showerror("Error", f"Could not rename {item_type}: {e}")

# Function to copy file or folder
def copy_item(item_type):
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file or folder selected")
        return

    source_path = tree.item(selected_item, 'values')[0]
    clipboard['path'] = source_path
    clipboard['action'] = 'copy'
    engine.say(f"{item_type.capitalize()} copied to clipboard.")
    engine.runAndWait()

# Function to move file or folder
def move_item(item_type):
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file or folder selected")
        return

    source_path = tree.item(selected_item, 'values')[0]
    clipboard['path'] = source_path
    clipboard['action'] = 'move'
    engine.say(f"{item_type.capitalize()} cut to clipboard.")
    engine.runAndWait()

# Function to paste copied or moved file or folder
def paste_item():
    if not clipboard:
        engine.say("Clipboard is empty.")
        engine.runAndWait()
        return

    destination = current_dir.get()
    source_path = clipboard['path']
    action = clipboard['action']
    
    try:
        if action == 'copy':
            if os.path.isfile(source_path):
                shutil.copy(source_path, destination)
            else:
                shutil.copytree(source_path, os.path.join(destination, os.path.basename(source_path)))
            engine.say("Item pasted successfully.")
        elif action == 'move':
            shutil.move(source_path, destination)
            engine.say("Item moved successfully.")
        populate_treeview(current_dir.get())
        engine.runAndWait()
    except Exception as e:
        messagebox.showerror("Error", f"Could not paste item: {e}")

# Function to preview file (text/image)
def preview_file():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file selected")
        return

    file_path = tree.item(selected_item, 'values')[0]

    if file_path.endswith('.txt'):
        with open(file_path, 'r') as f:
            content = f.read()
        preview_window = tk.Toplevel(root)
        preview_window.title(f"Preview: {os.path.basename(file_path)}")
        text_widget = tk.Text(preview_window, wrap='word')
        text_widget.insert('1.0', content)
        text_widget.pack(fill=tk.BOTH, expand=True)
    elif file_path.endswith(('.png', '.jpg', '.jpeg')):
        preview_window = tk.Toplevel(root)
        preview_window.title(f"Preview: {os.path.basename(file_path)}")
        img = Image.open(file_path)
        img = img.resize((400, 400))
        img_tk = ImageTk.PhotoImage(img)
        label = tk.Label(preview_window, image=img_tk)
        label.image = img_tk
        label.pack(fill=tk.BOTH, expand=True)

# Function to delete file or folder
def delete_item(item_type):
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No file or folder selected")
        return

    file_path = tree.item(selected_item, 'values')[0]
    if messagebox.askyesno("Delete", f"Are you sure you want to delete {os.path.basename(file_path)}?"):
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)
            populate_treeview(current_dir.get())
            engine.say(f"{item_type.capitalize()} deleted successfully.")
            engine.runAndWait()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete {item_type}: {e}")

# Voice commands: rename, copy, move, preview, open, delete, search, paste
def voice_commands():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        engine.say("Say a command")
        engine.runAndWait()
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            print(f"Recognized command: {command}")
            
            # Handle file-specific commands
            if "file" in command:
                query = command.split('file', 1)[-1].strip()
                if "open" in command:
                    result = voice_search(query, search_type="file")
                    if result:
                        open_item("file", result)  # Open specific file
                elif "rename" in command:
                    rename_item("file")
                elif "copy" in command:
                    copy_item("file")
                elif "move" in command:
                    move_item("file")
                elif "delete" in command:
                    delete_item("file")
                elif "preview" in command:
                    preview_file()

            # Handle folder-specific commands
            elif "folder" in command:
                query = command.split('folder', 1)[-1].strip()
                if "open" in command:
                    result = voice_search(query, search_type="folder")
                    if result:
                        open_item("folder", result)  # Open specific folder
                elif "rename" in command:
                    rename_item("folder")
                elif "copy" in command:
                    copy_item("folder")
                elif "move" in command:
                    move_item("folder")
                elif "delete" in command:
                    delete_item("folder")

            elif "back" in command:
                go_back()

            elif "paste" in command:
                paste_item()
            
            elif "change directory" in command:
                if "d" in command:
                    populate_treeview("D:\\")
                    current_dir.set("D:\\")
                    engine.say("Changed to directory D.")
                    engine.runAndWait()
                elif "c" in command:
                    populate_treeview("C:\\")
                    current_dir.set("C:\\")
                    engine.say("Changed to directory C.")
                    engine.runAndWait()

            else:
                engine.say("Command not recognized. Please try again.")
                engine.runAndWait()
        except sr.UnknownValueError:
            engine.say("Sorry, I did not understand.")
            engine.runAndWait()
def get_system_drives():
    drives = []
    if os.name == 'nt':  # For Windows
        bitmask = subprocess.check_output("fsutil fsinfo drives").decode().split()
        drives = bitmask[1:]  # Ignore "Drives:" part
    else:  # For Linux/Unix-based systems
        drives = ['/']
        for folder in os.listdir('/media'):
            drives.append(os.path.join('/media', folder))
    return drives

def open_directory_navigator():
    nav_window = tk.Toplevel(root)
    nav_window.title("Navigate to Directory")
    nav_window.geometry("500x300")

    nav_tree = ttk.Treeview(nav_window, columns=("FullPath"), show="tree")
    nav_tree.pack(fill=tk.BOTH, expand=True)

    # Populate with system drives at start
    drives = get_system_drives()
    for drive in drives:
        nav_tree.insert('', 'end', text=drive, values=[drive], open=False)

    def nav_populate_treeview(path):
        nav_tree.delete(*nav_tree.get_children())
        for item in os.listdir(path):
            abspath = os.path.join(path, item)
            try:
                nav_tree.insert('', 'end', text=item, values=[abspath], open=False)
            except PermissionError:
                continue

    def on_nav_select(event):
        selected_item = nav_tree.focus()
        new_dir = nav_tree.item(selected_item, 'values')[0]
        if os.path.isdir(new_dir):
            nav_populate_treeview(new_dir)

    nav_tree.bind("<Double-1>", on_nav_select)

    def on_select_directory():
        selected_item = nav_tree.focus()
        new_dir = nav_tree.item(selected_item, 'values')[0]
        if os.path.isdir(new_dir):
            previous_dir.append(current_dir.get())
            populate_treeview(new_dir)
            current_dir.set(new_dir)
            nav_window.destroy()
            engine.say("Directory changed successfully.")
            engine.runAndWait()

    select_btn = tk.Button(nav_window, text="Select Directory", command=on_select_directory)
    select_btn.pack(pady=10)
    

# Adding action buttons
button_frame = tk.Frame(root, bg="#444")  # Dark button frame
button_frame.pack(fill=tk.X)

buttons = [
    ("Open Folder", lambda: open_item("folder")),
    ("Open File", lambda: open_item("file")),
    ("Rename", lambda: rename_item("item")),
    ("Copy", lambda: copy_item("item")),
    ("Move", lambda: move_item("item")),
    ("Paste", paste_item),
    ("Delete", lambda: delete_item("item")),
    ("Preview File", preview_file),
    ("Voice Commands", voice_commands),
    ("Back", go_back),  # Add the back button functionality
    ("Change Directory", open_directory_navigator)
]

for (text, command) in buttons:
    btn = tk.Button(button_frame, text=text, command=command, bg="#565656", fg="white", relief="flat", padx=10, pady=5)
    btn.pack(side=tk.LEFT, padx=5, pady=5)

# Initially populate the treeview with the user's home directory
populate_treeview(current_dir.get())

# Bind double-click event to treeview
tree.bind("<Double-1>", on_double_click)

root.mainloop()
