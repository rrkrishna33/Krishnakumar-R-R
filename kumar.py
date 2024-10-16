import tkinter as tk
from tkinter import ttk
import threading
import time

# Function to simulate a long-running task
def long_running_task():
    time.sleep(10)  # Simulate a task taking 5 seconds to complete

# Function to show the loading screen
def show_loading_screen():
    loading_screen = tk.Toplevel(root)
    loading_screen.geometry("200x100")
    loading_screen.title("Loading...")

    label = tk.Label(loading_screen, text="Please wait...")
    label.pack(pady=20)

    # Add a progress bar to the loading screen
    progress = ttk.Progressbar(loading_screen, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
    progress.pack(pady=10)
    progress.start()

    # Center the loading screen on the screen
    loading_screen.update_idletasks()
    x = (loading_screen.winfo_screenwidth() // 2) - (loading_screen.winfo_reqwidth() // 2)
    y = (loading_screen.winfo_screenheight() // 2) - (loading_screen.winfo_reqheight() // 2)
    loading_screen.geometry(f"+{x}+{y}")

    return loading_screen

# Function to handle the long-running task and close the loading screen
def handle_task():
    loading_screen = show_loading_screen()
    threading.Thread(target=run_task, args=(loading_screen,)).start()

def run_task(loading_screen):
    long_running_task()
    loading_screen.destroy()

# Main application window
root = tk.Tk()
root.geometry("300x200")
root.title("Main Application")

button = tk.Button(root, text="Start Task", command=handle_task)
button.pack(pady=50)

root.mainloop()
