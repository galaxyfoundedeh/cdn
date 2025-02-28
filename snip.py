import tkinter as tk
from tkinter import simpledialog, messagebox
import os
import subprocess
import pyperclip
from PIL import ImageGrab

# Set upload folder
UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "cdn", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Git repository path
REPO_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "cdn")

# Global selection variables
start_x, start_y, end_x, end_y = 0, 0, 0, 0

# Function to start selection
def on_press(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y
    canvas.delete("rect")

# Function to update selection rectangle
def on_drag(event):
    global end_x, end_y
    end_x, end_y = event.x, event.y
    canvas.delete("rect")
    canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="red", width=2, tags="rect")

# Function to capture selected area and save
def on_release(event):
    global start_x, start_y, end_x, end_y
    selection_window.withdraw()
    
    x1, x2 = sorted([start_x, end_x])
    y1, y2 = sorted([start_y, end_y])
    
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    
    filename = simpledialog.askstring("Save Image", "Enter a filename (without extension):")
    if not filename:
        return
    
    filename = "".join(c for c in filename if c.isalnum() or c in "-_ ").rstrip()
    if not filename:
        return
    
    filename = f"{filename}.png"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        screenshot.save(file_path, "PNG")
        print(f"✅ Screenshot saved: {file_path}")  # Debug print
        commit_and_push(filename)
    except Exception as e:
        messagebox.showerror("Error", f"❌ Failed to save screenshot: {str(e)}")
        return

# Function to check if uploads/ is ignored
def is_ignored(filepath):
    check = subprocess.run(["git", "check-ignore", "-v", filepath], cwd=REPO_PATH, capture_output=True, text=True)
    return bool(check.stdout.strip())  # Returns True if file is ignored

# Function to commit and push changes to Git
def commit_and_push(filename):
    try:
        # Ensure this is a Git repository
        if not os.path.exists(os.path.join(REPO_PATH, ".git")):
            messagebox.showerror("Error", "❌ Not a Git repository!")
            return
        
        # Check if uploads/ folder is ignored
        if is_ignored("uploads"):
            messagebox.showerror("Git Error", "❌ The 'uploads/' folder is ignored in .gitignore! Remove it and try again.")
            return
        
        # Add the entire uploads folder (ensuring new files are tracked)
        subprocess.run(["git", "add", "uploads"], cwd=REPO_PATH, check=True)
        
        # Commit the changes
        commit_result = subprocess.run(["git", "commit", "-m", f"📸 Added screenshot: {filename}"], cwd=REPO_PATH, capture_output=True, text=True)
        if commit_result.stderr:
            print("❌ Git Commit Error:", commit_result.stderr)
            messagebox.showerror("Git Error", f"Commit failed: {commit_result.stderr}")
            return

        # Push to remote repository
        push_result = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_PATH, capture_output=True, text=True)
        if push_result.stderr:
            print("❌ Git Push Error:", push_result.stderr)
            messagebox.showerror("Git Error", f"Push failed: {push_result.stderr}")
            return

        image_link = f"https://cdnfr.galaxyteam.us.kg/uploads/{filename}"
        pyperclip.copy(image_link)
        messagebox.showinfo("Success", f"✅ Screenshot uploaded!\nLink copied: {image_link}")
        print(f"🔗 Link copied: {image_link}")

    except subprocess.CalledProcessError as e:
        print("❌ Exception:", str(e))
        messagebox.showerror("Error", "Git operation failed.")

# Function to trigger selection
def trigger_selection():
    selection_window.deiconify()

# Main UI setup
root = tk.Tk()
root.title("Screenshot Tool")
root.geometry("300x150")
root.configure(bg="#282c34")

trigger_button = tk.Button(root, text="Take Screenshot", command=trigger_selection, font=("Arial", 14), padx=20, pady=10, bg="#61afef", fg="white")
trigger_button.pack(pady=40)

selection_window = tk.Toplevel(root)
selection_window.attributes('-fullscreen', True)
selection_window.attributes('-alpha', 0.3)
selection_window.configure(bg="black")
selection_window.withdraw()

canvas = tk.Canvas(selection_window, cursor="cross", bg="black")
canvas.pack(fill="both", expand=True)
canvas.bind("<ButtonPress-1>", on_press)
canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)

root.mainloop()
