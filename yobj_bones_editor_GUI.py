import tkinter as tk
from tkinter import filedialog, messagebox
import struct
import shutil

# Data storage
bones = []
bones_offset = []
bones_name = []
bones_parent = []
read_bones_offset = 0
bones_count = 0
current_file_path = None

# Fungsi membuat backup
def create_backup(file_path):
    try:
        backup_path = file_path + ".bak"
        shutil.copyfile(file_path, backup_path)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create backup: {e}")

# Fungsi membaca bones dari file
def bones_list(file_path):
    global bones, bones_offset, bones_name, bones_parent, read_bones_offset, bones_count
    bones.clear()
    bones_offset.clear()
    bones_name.clear()
    bones_parent.clear()

    try:
        with open(file_path, "r+b") as f:
            f.seek(28)
            bones_count = struct.unpack('<i', f.read(4))[0]
            f.seek(40)
            read_bones_offset = struct.unpack('<i', f.read(4))[0]
            f.seek(read_bones_offset + 8)
            for i in range(bones_count):
                offset = f.tell()
                bones_offset.append(offset)
                pointer = f.read(16).decode('ascii').strip('\x00')
                bones_name.append(pointer)
                f.read(32)
                pointer = struct.unpack('<i', f.read(4))[0]
                bones_parent.append(pointer)
                f.seek(-52, 1)
                pointer = f.read(80)
                bones.append(pointer)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")
        return []

    # Create readable bones list
    result = []
    for i in range(bones_count):
        name = bones_name[i]
        offset = bones_offset[i]
        parent = bones_parent[i]
        parent_name = "none" if parent == -1 else bones_name[parent]
        result.append(f"Index {i}, Name {name}, Offset {offset}, Parent {parent} ({parent_name})")
    return result

# Fungsi tombol Browse
def browse_file():
    global current_file_path
    file_path = filedialog.askopenfilename(filetypes=[("YOBJ files", "*.yobj")])
    if file_path:
        current_file_path = file_path
        file_label.config(text=file_path)
        bones_data = bones_list(file_path)
        bones_listbox.delete(0, tk.END)
        for item in bones_data:
            bones_listbox.insert(tk.END, item)

# Fungsi Rename Bones
def rename_bones(file_path, index, new_name):
    global bones_name, bones_offset
    create_backup(file_path)  # Backup dibuat di sini
    new_name = new_name[:16]  # Max length 16
    padded_name = new_name.encode('ascii').ljust(16, b'\x00')

    try:
        with open(file_path, "r+b") as f:
            f.seek(bones_offset[index])
            f.write(padded_name)
        bones_name[index] = new_name
        bones_listbox.delete(index)
        bones_listbox.insert(index, f"Index {index}, Name {new_name}, Offset {bones_offset[index]}, Parent {bones_parent[index]} (none)")
        messagebox.showinfo("Success", f"Bone renamed successfully to '{new_name}'!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to rename bone: {e}")

# Fungsi Change Parent
def change_parent(file_path, index, new_parent):
    global bones_parent
    create_backup(file_path)  # Backup dibuat di sini

    try:
        with open(file_path, "r+b") as f:
            f.seek(bones_offset[index] + 48)
            f.write(struct.pack('<i', new_parent))
        bones_parent[index] = new_parent
        bones_listbox.delete(index)
        parent_name = "none" if new_parent == -1 else bones_name[new_parent]
        bones_listbox.insert(index, f"Index {index}, Name {bones_name[index]}, Offset {bones_offset[index]}, Parent {new_parent} ({parent_name})")
        messagebox.showinfo("Success", f"Parent changed successfully to {new_parent}!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to change parent: {e}")

# Fungsi membuka jendela rename
def open_rename_window():
    selected_index = bones_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Warning", "Please select a bone from the list!")
        return

    index = selected_index[0]

    # Jendela Rename
    rename_window = tk.Toplevel(root)
    rename_window.title("Rename Bone")
    rename_window.geometry("300x200")
    root.attributes("-disabled", True)  # Freeze main window

    def close_rename_window():
        root.attributes("-disabled", False)  # Unfreeze main window
        rename_window.destroy()

    rename_window.protocol("WM_DELETE_WINDOW", close_rename_window)

    tk.Label(rename_window, text=f"Old Name: {bones_name[index]}").pack(pady=5)
    tk.Label(rename_window, text="New Name (max 16 characters):").pack(pady=5)

    new_name_var = tk.StringVar()

    def limit_input(*args):
        if len(new_name_var.get()) > 16:
            new_name_var.set(new_name_var.get()[:16])

    new_name_var.trace("w", limit_input)
    new_name_entry = tk.Entry(rename_window, textvariable=new_name_var)
    new_name_entry.pack(pady=5)

    def save_new_name():
        new_name = new_name_var.get().strip()
        if len(new_name) == 0:
            messagebox.showwarning("Warning", "New name cannot be empty!")
            return
        rename_bones(current_file_path, index, new_name)
        close_rename_window()

    tk.Button(rename_window, text="Save", command=save_new_name).pack(pady=10)

# Fungsi membuka jendela change parent
def open_change_parent_window():
    selected_index = bones_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Warning", "Please select a bone from the list!")
        return

    index = selected_index[0]

    # Jendela Change Parent
    parent_window = tk.Toplevel(root)
    parent_window.title("Change Parent")
    parent_window.geometry("300x300")
    root.attributes("-disabled", True)  # Freeze main window

    def close_parent_window():
        root.attributes("-disabled", False)  # Unfreeze main window
        parent_window.destroy()

    parent_window.protocol("WM_DELETE_WINDOW", close_parent_window)
    parent=bones_parent[index]
    parent_name="none"
    if parent != -1:
        parent_name=bones_name[parent]
        pass
    tk.Label(parent_window, text=f"Bone: {bones_name[index]}").pack(pady=1)
    tk.Label(parent_window, text=f"Old parent: {parent} ({parent_name})").pack(pady=1)
    tk.Label(parent_window, text="Select New Parent (or None):").pack(pady=1)

    parent_listbox = tk.Listbox(parent_window, height=10)
    parent_listbox.pack(pady=5)

    # Add None option at the top
    parent_listbox.insert(tk.END, "None (-1)")

    # Add other bones as options
    for i, name in enumerate(bones_name):
        parent_listbox.insert(tk.END, f"{i}: {name}")

    def save_new_parent():
        try:
            selection = parent_listbox.curselection()
            if not selection:
                raise ValueError("No parent selected!")
            selected_parent = selection[0] - 1  # Subtract 1 to account for the "None" entry at the top
            if selected_parent < -1 or selected_parent >= bones_count:
                raise ValueError("Invalid parent index!")
            change_parent(current_file_path, index, selected_parent)
            close_parent_window()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(parent_window, text="Save", command=save_new_parent).pack(pady=10)

# GUI
root = tk.Tk()
root.title("YOBJ Bones Editor GUI")

# File selection
file_label = tk.Label(root, text="No file selected")
file_label.pack()
browse_button = tk.Button(root, text="Browse File", command=browse_file)
browse_button.pack()

# Listbox
bones_listbox = tk.Listbox(root, width=80, height=20)
bones_listbox.pack()

# Buttons
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=10)
rename_button = tk.Button(buttons_frame, text="Rename", command=open_rename_window)
rename_button.grid(row=0, column=0, padx=5)
change_parent_button = tk.Button(buttons_frame, text="Change Parent", command=open_change_parent_window)
change_parent_button.grid(row=0, column=1, padx=5)

# Run
root.mainloop()
