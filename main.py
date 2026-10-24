"""Start the School Management System desktop application."""
import tkinter as tk
from tkinter import messagebox

from gui import SchoolManagementApp


def main():
    root = tk.Tk()
    try:
        SchoolManagementApp(root)
    except Exception as exc:
        messagebox.showerror("Startup error", f"The application could not start:\n{exc}")
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
