import tkinter as tk
from tkinter import messagebox

def show_message_boxes():
    messagebox.showinfo("Information", "This is an info message.")
    messagebox.showwarning("Warning", "This is a warning message.")
    messagebox.showerror("Error", "This is an error message.")
    result = messagebox.askquestion("Question", "Do you like Tkinter?")
    print(f"Question result: {result}")
    result = messagebox.askokcancel("Ok Cancel", "Do you want to proceed?")
    print(f"Ok Cancel result: {result}")
    result = messagebox.askyesno("Yes No", "Do you want to continue?")
    print(f"Yes No result: {result}")
    result = messagebox.askretrycancel("Retry Cancel", "Do you want to retry?")
    print(f"Retry Cancel result: {result}")

root = tk.Tk()
root.geometry("300x200")
button = tk.Button(root, text="Show Message Boxes", command=show_message_boxes)
button.pack(pady=20)
root.mainloop()
