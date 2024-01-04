import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import json
import sys


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")

        # Set the Ubuntu font
        font_style = ('Ubuntu', 12)

        # Style
        root.option_add('*TButton*highlightBackground', '#1DA1F2')
        root.option_add('*TButton*highlightColor', '#1DA1F2')
        root.option_add('*TButton*background', '#1DA1F2')
        root.option_add('*TButton*foreground', 'white')
        root.option_add('*TButton*padding', [10, 5])
        root.option_add('*TCheckbutton*background', '#1DA1F2')
        root.option_add('*TCheckbutton*foreground', 'white')
        root.option_add('*TCheckbutton*indicatorcolor', 'white')
        root.option_add('*TLabel*foreground', '#1DA1F2')
        root.option_add('*TLabel*font', font_style)
        root.option_add('*TFrame*background', '#1DA1F2')
        root.option_add('*TEntry*font', font_style)
        root.option_add('*TEntry*background', 'white')

        self.tasks = self.load_tasks()  # Load tasks from file
        self.startup_var = tk.BooleanVar()
        self.startup_var.set(self.load_startup_setting()
                             )  # Load startup setting

        # Task Entry
        self.task_entry = ttk.Entry(root, font=font_style, width=30)
        self.task_entry.grid(row=0, column=0, padx=10, pady=10)

        # Add Task Button
        add_button = ttk.Button(root, text="Add Task", command=self.add_task)
        add_button.grid(row=0, column=1, padx=10, pady=10)

        # Task List
        self.task_frame = ttk.Frame(root)
        self.task_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Settings Dropdown
        settings_var = tk.StringVar()
        settings_var.set("Settings")
        settings_dropdown = ttk.Combobox(
            root, textvariable=settings_var, values=["Settings", "Start on Startup", "Reset Tasks", "Reset Settings"])
        settings_dropdown.grid(row=2, column=0, padx=10, pady=10)
        settings_dropdown.config(font=font_style, width=15)
        settings_dropdown.set("Settings")
        settings_dropdown.bind(
            "<<ComboboxSelected>>", lambda event: self.handle_settings_selection(event))

        # Load tasks into the UI
        self.load_tasks_into_ui()

    def add_task(self):
        task_text = self.task_entry.get()
        if task_text:
            task_frame = ttk.Frame(self.task_frame)
            task_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

            status_var = tk.BooleanVar()
            status_var.set(False)

            task_checkbox = ttk.Checkbutton(
                task_frame, text=f"{task_text} - TASK", variable=status_var, command=lambda: self.update_task_status(task_text, status_var.get()))
            task_checkbox.grid(row=0, column=0, padx=5, pady=5)

            date_label = ttk.Label(
                task_frame, text=self.get_current_date(), foreground="deep sky blue")
            date_label.grid(row=0, column=1, padx=5, pady=5)

            delete_button = ttk.Button(
                task_frame, text="X", command=lambda t=task_text: self.delete_task_by_text(t))
            delete_button.grid(row=0, column=2, padx=5, pady=5)

            self.tasks.append((task_text, status_var.get()))
            self.update_task_list()

            # Save tasks to file
            self.save_tasks()

    def delete_task(self, task_frame):
        task_frame.destroy()
        self.tasks = [(task, status)
                      for task, status in self.tasks if task_frame != task]

        # Save tasks to file after deletion
        self.save_tasks()

    def update_task_list(self):
        self.task_entry.delete(0, tk.END)

    def handle_settings_selection(self, event):
        selected_option = event.widget.get()
        if selected_option == "Start on Startup":
            self.toggle_startup()
        elif selected_option == "Reset Tasks":
            self.reset_tasks()
        elif selected_option == "Reset Settings":
            self.reset_settings()

    def toggle_startup(self):
        startup_path = os.path.join(os.path.expanduser(
            "~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        shortcut_name = "TaskManager.lnk"
        shortcut_path = os.path.join(startup_path, shortcut_name)

        if self.startup_var.get():
            messagebox.showinfo("Startup Setting",
                                "Task Manager will start on startup.")
            # Create a shortcut in the user's startup folder
            try:
                import ctypes
                import winreg

                # Check for admin privileges
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", sys.executable, " ".join(
                            sys.argv), None, 1
                    )
                    sys.exit()

                # Create the registry key to run the script on startup
                key = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as registry_key:
                    winreg.SetValueEx(registry_key, "TaskManager",
                                      0, winreg.REG_SZ, sys.executable)

                # Create a shortcut in the user's startup folder
                import pythoncom
                from win32com.client import Dispatch

                pythoncom.CoInitialize()
                shell = Dispatch("WScript.Shell")
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
            # Remove the registry key if it exists
            try:
                key = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as registry_key:
                    winreg.DeleteValue(registry_key, "TaskManager")
            except FileNotFoundError:
                pass

            # Remove the shortcut if it exists
            if os.path.exists(shortcut_path):
                try:
                    os.remove(shortcut_path)
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Failed to remove shortcut: {e}")

        # Save startup setting to file
        self.save_startup_setting()

    def reset_tasks(self):
        confirmed = messagebox.askyesno(
            "Reset Tasks", "Are you sure you want to reset all tasks?")
        if confirmed:
            for task, _ in self.tasks:
                self.delete_task_by_text(task)

    def reset_settings(self):
        confirmed = messagebox.askyesno(
            "Reset Settings", "Are you sure you want to reset all settings?")
        if confirmed:
            self.startup_var.set(False)
            # Save startup setting to file
            self.save_startup_setting()

    def get_current_date(self):
        return datetime.now().strftime("%Y-%m-%d")

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as file:
                tasks = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            tasks = []
        return tasks

    def save_tasks(self):
        with open('tasks.json', 'w') as file:
            json.dump(self.tasks, file)

    def load_startup_setting(self):
        try:
            with open('config.json', 'r') as file:
                config = json.load(file)
                return config.get('startup', False)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def save_startup_setting(self):
        with open('config.json', 'w') as file:
            json.dump({'startup': self.startup_var.get()}, file)

    def load_tasks_into_ui(self):
        for task, status in self.tasks:
            task_frame = ttk.Frame(self.task_frame)
            task_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

            status_var = tk.BooleanVar()
            status_var.set(status)

            task_checkbox = ttk.Checkbutton(
                task_frame, text=f"{task} - TASK", variable=status_var, command=lambda t=task, s=status_var.get(): self.update_task_status(t, s))
            task_checkbox.grid(row=0, column=0, padx=5, pady=5)

            date_label = ttk.Label(
                task_frame, text=self.get_current_date(), foreground="deep sky blue")
            date_label.grid(row=0, column=1, padx=5, pady=5)

            delete_button = ttk.Button(
                task_frame, text="X", command=lambda t=task: self.delete_task_by_text(t))
            delete_button.grid(row=0, column=2, padx=5, pady=5)

            self.update_task_list()

    def delete_task_by_text(self, task_text):
        task_frame = next((frame for frame in self.task_frame.winfo_children(
        ) if task_text in frame.winfo_children()[0].cget('text')), None)
        if task_frame:
            task_frame.destroy()
            self.tasks = [(task, status)
                          for task, status in self.tasks if task != task_text]
            self.save_tasks()

    def update_task_status(self, task_text, status):
        # Update the status of the task in the tasks list
        for i, (task, _) in enumerate(self.tasks):
            if task == task_text:
                self.tasks[i] = (task, status)

        # Save tasks to file after updating status
        self.save_tasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
