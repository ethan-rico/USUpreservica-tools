# update_metadata/gui.py

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from .metadata_diff import parse_csv, generate_diffs
from .metadata_updater import update_asset_metadata
import threading

class MetadataUpdaterGUI(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.title("Preservica Metadata Updater")
        self.geometry("1200x600")
        self.client = client
        self.diffs = []

        self.upload_button = tk.Button(self, text="Load Updated CSV", command=self.load_csv)
        self.upload_button.pack(pady=10)

        self.tree = ttk.Treeview(self, show="headings", selectmode="browse")
        self.tree.pack(expand=True, fill="both")

        self.update_button = tk.Button(self, text="Submit Updates", command=self.submit_updates, state="disabled")
        self.update_button.pack(pady=10)

        self.status_text = tk.Text(self, height=8)
        self.status_text.pack(fill="x")

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            self.status_text.insert(tk.END, "Loading CSV...\n")
            csv_rows = parse_csv(file_path)

            self.status_text.insert(tk.END, "Fetching metadata from Preservica...\n")
            self.diffs = generate_diffs(self.client, csv_rows)

            self.show_preview_table(self.diffs)
            self.update_button.config(state="normal")
            self.status_text.insert(tk.END, "Comparison complete. Ready to update.\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_text.insert(tk.END, f"[ERROR] {e}\n")

    def show_preview_table(self, diffs):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ["reference"] + sorted(
            set(k for d in diffs for k in d["csv_row"] if k.startswith("dc:"))
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")

        for diff in diffs:
            values = []
            ref = diff["reference"]
            row_data = diff["csv_row"]
            changes = diff["changes"]

            for col in self.tree["columns"]:
                value = row_data.get(col, "")
                values.append(value)

            row_id = self.tree.insert("", "end", values=values, tags=(ref,))
            if changes:
                self.tree.item(row_id, tags=("changed",))

        # Highlight rows with changes
        self.tree.tag_configure("changed", background="#ffeecc")

    def submit_updates(self):
        def run_updates():
            self.update_button.config(state="disabled")
            for diff in self.diffs:
                ref = diff["reference"]
                changes = diff["changes"]
                if not changes:
                    self.status_text.insert(tk.END, f"[SKIPPED] {ref} — no changes\n")
                    continue
                try:
                    result = update_asset_metadata(self.client, ref, diff["csv_row"])
                    self.status_text.insert(tk.END, f"[UPDATED] {ref}: {result}\n")
                except Exception as e:
                    self.status_text.insert(tk.END, f"[ERROR] {ref}: {e}\n")
            self.status_text.insert(tk.END, "Update process complete.\n")
            self.update_button.config(state="normal")

        threading.Thread(target=run_updates).start()
