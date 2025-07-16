# gui.py

import tkinter as tk
from tkinter import filedialog, messagebox

def launch_gui():
    def choose_excel():
        filepath = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        excel_path.set(filepath)

    def run_tool():
        file = excel_path.get()
        mode = mode_var.get()
        apply = apply_var.get()

        if not file:
            messagebox.showerror("Error", "Please select an Excel file.")
            return

        summary = f"Mode: {mode}\nFile: {file}\nApply Changes: {apply}"
        messagebox.showinfo("Preview", summary)
        from metadata_logic import load_excel_data, group_fields

        try:
            records = load_excel_data(file)
            first = records[0]
            grouped = group_fields(first)
            print(f"[DEBUG] First row (grouped): {grouped}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # TODO: Hook into metadata_logic here
        print(f"[DEBUG] Running with file: {file}, mode: {mode}, apply: {apply}")

    root = tk.Tk()
    root.title("QDC Metadata Editor")
    root.geometry("500x300")

    excel_path = tk.StringVar()
    mode_var = tk.StringVar(value="Replace")
    apply_var = tk.BooleanVar()

    tk.Label(root, text="Step 1: Choose Excel file with metadata edits").pack(pady=5)
    tk.Button(root, text="Browse Excel File", command=choose_excel).pack()
    tk.Label(root, textvariable=excel_path, wraplength=400).pack(pady=5)

    tk.Label(root, text="Step 2: Choose operation mode").pack(pady=10)
    tk.OptionMenu(root, mode_var, "Replace", "Append", "Delete", "Find/Replace").pack()

    tk.Checkbutton(root, text="Apply Changes (uncheck for Preview Mode)", variable=apply_var).pack(pady=10)

    tk.Button(root, text="Run Tool", command=run_tool, bg="green", fg="white").pack(pady=20)

    root.mainloop()
