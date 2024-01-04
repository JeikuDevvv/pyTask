import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
import sys


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")

        self.tasks = []
        self.startup_var = tk.BooleanVar()
        self.startup_var.set(False)  # Default startup setting

        # Task Entry
        self.task_entry = tk.Entry(root, width=30)
        self.task_entry.grid(row=0, column=0, padx=10, pady=10)

        # Add Task Button
        add_button = tk.Button(root, text="Add Task", command=self.add_task)
        add_button.grid(row=0, column=1, padx=10, pady=10)

        # Task List
        self.task_frame = tk.Frame(root)
        self.task_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Settings Dropdown
        settings_var = tk.StringVar()
        settings_var.set("Settings")
        settings_dropdown = tk.OptionMenu(
            root, settings_var, "Settings", "Start on Startup", "Reset Tasks", "Reset Settings")
        settings_dropdown.grid(row=2, column=0, padx=10, pady=10)
        settings_dropdown.config(width=15, font=('Helvetica', 10))
        settings_dropdown["menu"].config(font=('Helvetica', 10), tearoff=0)
        # Disable the default "Settings" option
        settings_dropdown["menu"].entryconfig(0, state=tk.DISABLED)
        settings_dropdown["menu"].entryconfig(1, command=self.toggle_startup)
        settings_dropdown["menu"].entryconfig(2, command=self.reset_tasks)
        settings_dropdown["menu"].entryconfig(3, command=self.reset_settings)

    def add_task(self):
        task_text = self.task_entry.get()
        if task_text:
            task_frame = tk.Frame(self.task_frame)
            task_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

            status_var = tk.BooleanVar()
            status_var.set(False)  # Default status

            task_checkbox = tk.Checkbutton(
                task_frame, text=f"{task_text} - TASK", variable=status_var)
            task_checkbox.grid(row=0, column=0, padx=5, pady=5)

            date_label = tk.Label(
                task_frame, text=self.get_current_date(), fg="deep sky blue")
            date_label.grid(row=0, column=1, padx=5, pady=5)

            delete_button = tk.Button(
                task_frame, text="X", command=lambda: self.delete_task(task_frame))
            delete_button.grid(row=0, column=2, padx=5, pady=5)

            self.tasks.append((task_text, status_var, task_frame, date_label))
            self.update_task_list()

    def delete_task(self, task_frame):
        task_frame.destroy()
        self.tasks = [(task, status, frame, date_label)
                      for task, status, frame, date_label in self.tasks if frame != task_frame]

    def update_task_list(self):
        # Clear the task entry after adding a task
        self.task_entry.delete(0, tk.END)

    def toggle_startup(self):
        # Toggle the "Start on Startup" setting
        startup_path = os.path.join(os.path.expanduser(
            "~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        shortcut_name = "TaskManager.lnk"
        shortcut_path = os.path.join(startup_path, shortcut_name)

        if self.startup_var.get():
            messagebox.showinfo("Startup Setting",
                                "Task Manager will start on startup.")
            # Create a shortcut in the user's startup folder
            try:
                import win32com.client

                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = os.path.abspath(__file__)
                shortcut.save()
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to create shortcut: {e}")
        else:
            messagebox.showinfo("Startup Setting",
                                "Task Manager will not start on startup.")
            # Remove the shortcut if it exists
            if os.path.exists(shortcut_path):
                try:
                    os.remove(shortcut_path)
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Failed to remove shortcut: {e}")

    def reset_tasks(self):
        # Reset all tasks
        confirmed = messagebox.askyesno(
            "Reset Tasks", "Are you sure you want to reset all tasks?")
        if confirmed:
            for _, _, frame, date_label in self.tasks:
                frame.destroy()
                date_label.destroy()
            self.tasks = []

    def reset_settings(self):
        # Reset settings (including "Start on Startup")
        confirmed = messagebox.askyesno(
            "Reset Settings", "Are you sure you want to reset all settings?")
        if confirmed:
            self.startup_var.set(False)

    def get_current_date(self):
        return datetime.now().strftime("%Y-%m-%d")


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
