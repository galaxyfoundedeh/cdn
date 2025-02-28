import tkinter as tk
from tkinter import simpledialog
import os
import subprocess
from PIL import ImageGrab

# Set the upload folder to your specific path
UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "cdn", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Git repository path
REPO_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "cdn")

# Git user details
GIT_USERNAME = "galaxyfoundedeh"
GIT_EMAIL = "kiley.phd@go.sfcollege.edu"  # Replace with the actual email linked to the Git account

# Global variables for selection
start_x, start_y, end_x, end_y = 0, 0, 0, 0

# Function to start selection
def on_press(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y
    canvas.delete("rect")  # Clear previous selection

# Function to update selection rectangle
def on_drag(event):
    global end_x, end_y
    end_x, end_y = event.x, event.y
    canvas.delete("rect")  # Remove old rectangle
    canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="red", width=2, tags="rect")

# Function to capture selected area and save
def on_release(event):
    global start_x, start_y, end_x, end_y
    selection_window.withdraw()  # Hide the selection UI after capturing

    # Ensure correct coordinates
    x1, x2 = sorted([start_x, end_x])
    y1, y2 = sorted([start_y, end_y])

    # Capture the selected area
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    # Ask the user for a filename
    filename = simpledialog.askstring("Save Image", "Enter a filename (without extension):")
    if not filename:
        print("❌ No filename entered. Cancelling.")
        return
    
    # Remove any problematic characters from filename
    filename = "".join(c for c in filename if c.isalnum() or c in "-_ ").rstrip()
    if not filename:
        print("❌ Invalid filename. Cancelling.")
        return
    
    filename = f"{filename}.png"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Save the screenshot
    screenshot.save(file_path, "PNG")
    print(f"✅ Screenshot saved as: {file_path}")

    # Commit and push to Git
    commit_and_push(filename)

# Function to commit and push changes to Git
def commit_and_push(filename):
    try:
        if not os.path.exists(os.path.join(REPO_PATH, ".git")):
            print("❌ Error: Not a Git repository. Run 'git init' in the repo folder.")
            return

        # Set the correct Git user
        subprocess.run(["git", "config", "--global", "user.name", GIT_USERNAME], cwd=REPO_PATH, check=True)
        subprocess.run(["git", "config", "--global", "user.email", GIT_EMAIL], cwd=REPO_PATH, check=True)
        
        print(f"🚀 Using Git account: {GIT_USERNAME}")

        print("🚀 Adding file to Git...")
        subprocess.run(["git", "add", "--all"], cwd=REPO_PATH, check=True)  # Stage ALL changes

        print("📝 Committing changes...")
        subprocess.run(["git", "commit", "-m", f"Added screenshot: {filename}"], cwd=REPO_PATH, check=True)

        print("📌 Stashing any unstaged changes...")
        subprocess.run(["git", "stash"], cwd=REPO_PATH, check=True)  # Stash changes to avoid conflict

        print("⬇️ Pulling latest changes...")
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=REPO_PATH, check=True)

        print("📤 Pushing to remote repository...")
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_PATH, check=True)

        print("📌 Applying stashed changes back...")
        subprocess.run(["git", "stash", "pop"], cwd=REPO_PATH, check=True)  # Reapply stashed changes

        print("✅ Deployment complete!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")

# Function to trigger selection UI
def trigger_selection():
    print("🎯 Screenshot selection triggered!")
    selection_window.deiconify()

# Create the main control UI
root = tk.Tk()
root.title("Screenshot Tool")
root.geometry("300x200")

# Create a button to trigger selection
trigger_button = tk.Button(root, text="Click It!", command=trigger_selection, font=("Arial", 14), padx=20, pady=10)
trigger_button.pack(pady=50)

# Create a fullscreen transparent window for selection (initially hidden)
selection_window = tk.Toplevel(root)
selection_window.attributes('-fullscreen', True)
selection_window.attributes('-alpha', 0.3)  # Make it semi-transparent
selection_window.configure(bg="black")
selection_window.withdraw()  # Hide until triggered

# Create a canvas to draw selection
canvas = tk.Canvas(selection_window, cursor="cross", bg="black")
canvas.pack(fill="both", expand=True)
canvas.bind("<ButtonPress-1>", on_press)
canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)

# Run the main UI loop
root.mainloop()
