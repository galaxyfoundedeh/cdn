import tkinter as tk
from tkinter import simpledialog
import os
import subprocess
import pyperclip
from PIL import ImageGrab

# Configure storage folder inside the Git repo
GIT_REPO_PATH = os.path.abspath("public/uploads")
os.makedirs(GIT_REPO_PATH, exist_ok=True)

# Variables for selection
start_x, start_y, end_x, end_y = 0, 0, 0, 0

# Start selection
def on_press(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y
    canvas.delete("rect")  # Clear previous selection

# Draw selection rectangle
def on_drag(event):
    global end_x, end_y
    end_x, end_y = event.x, event.y
    canvas.delete("rect")
    canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="red", width=2, tags="rect")

# Capture screenshot, save, and push to Git
def on_release(event):
    global start_x, start_y, end_x, end_y
    root.withdraw()  # Hide UI after selection

    # Sort coordinates to ensure correct selection
    x1, x2 = sorted([start_x, end_x])
    y1, y2 = sorted([start_y, end_y])

    # Capture selected area
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    # Ask user for a filename
    filename = simpledialog.askstring("Save Image", "Enter filename (without extension):")
    if not filename:
        print("❌ No filename entered. Cancelling.")
        root.quit()
        return

    filename = f"{filename}.png"
    file_path = os.path.join(GIT_REPO_PATH, filename)

    # Save the screenshot
    screenshot.save(file_path, "PNG")
    print(f"✅ Screenshot saved as: {file_path}")

    # Push to Git
    push_to_git(filename)

# Push to Git & copy URL to clipboard
def push_to_git(filename):
    try:
        print("📤 Pushing to Git...")

        # Run Git commands
        subprocess.run(["git", "add", f"public/uploads/{filename}"], check=True)
        subprocess.run(["git", "commit", "-m", f"Add screenshot {filename}"], check=True)
        subprocess.run(["git", "push"], check=True)

        # Generate file URL
        file_url = f"https://your-vercel-app.vercel.app/uploads/{filename}"
        pyperclip.copy(file_url)

        print(f"✅ Uploaded! URL copied to clipboard: {file_url}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")

# Create UI for selection
root = tk.Tk()
root.attributes('-fullscreen', True)
root.attributes('-alpha', 0.3)  # Transparent overlay
root.configure(bg="black")

canvas = tk.Canvas(root, cursor="cross", bg="black")
canvas.pack(fill="both", expand=True)
canvas.bind("<ButtonPress-1>", on_press)
canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)

# Run the application
root.mainloop()
