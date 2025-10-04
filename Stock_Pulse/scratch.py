import tkinter as tk
import subprocess
import os

# Define your MERN projects here
PROJECTS = {
    "My Portfolio": r"D:\study\MERN\portfolio",
    "Billing App": r"D:\study\MERN\billing",
    "E-Commerce": r"D:\study\MERN\ecommerce"
}

def launch_project(path):
    # Launch backend
    subprocess.Popen(["cmd", "/k", "cd backend && npm start"], cwd=path)
    # Launch frontend
    subprocess.Popen(["cmd", "/k", "cd frontend && npm start"], cwd=path)

# GUI setup
root = tk.Tk()
root.title("MERN Application Launcher")
root.geometry("400x300")

label = tk.Label(root, text="Select a Project to Launch:", font=("Arial", 14))
label.pack(pady=10)

for name, path in PROJECTS.items():
    btn = tk.Button(root, text=name, font=("Arial", 12), width=25,
                    command=lambda p=path: launch_project(p))
    btn.pack(pady=5)

root.mainloop()
