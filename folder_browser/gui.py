# folder_browser/gui.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import pyPreservica as pyp

class PreservicaBrowser(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.title("Preservica Folder Browser")
        self.geometry("800x600")
        self.client = client

        self.tree = ttk.Treeview(self, selectmode='extended')
        self.tree.pack(expand=True, fill='both')

        self.tree.heading("#0", text="Preservica Folders & Assets", anchor='w')
        self.tree.bind("<<TreeviewOpen>>", self.on_open_folder)

        export_button = tk.Button(self, text="Export Metadata", command=self.export_metadata)
        export_button.pack(pady=10)

        self.load_root_folder()

    def load_root_folder(self):
        try:
            root_folder = self.client.folder("d675ed12-ad33-4c65-b533-5dbccb3e5568")
            print(f"[DEBUG] Loaded root folder: {root_folder.title} ({root_folder.reference})")
            self.tree.insert('', 'end', root_folder.reference, text=root_folder.title)
            self.tree.insert(root_folder.reference, 'end', f"{root_folder.reference}_dummy")
        except Exception as e:
            messagebox.showerror("Connection Error", f"{e}")

    def on_open_folder(self, event):
        node = self.tree.focus()
        children = self.tree.get_children(node)
        if len(children) == 1 and children[0].endswith("_dummy"):
            self.tree.delete(children[0])
            self.load_folder_children(node)

    def load_folder_children(self, folder_ref):
        try:
            children = self.client.children(folder_ref)
            print(f"[DEBUG] Loaded children for folder {folder_ref}")
            for child in children.results:
                node_id = child.reference
                label = f"{child.title} (Asset)" if isinstance(child, pyp.Asset) else child.title
                self.tree.insert(folder_ref, 'end', node_id, text=label)
                if isinstance(child, pyp.Folder):
                    self.tree.insert(node_id, 'end', f"{node_id}_dummy")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load folder: {e}")

    def export_metadata(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one asset.")
            return

        export_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Metadata Export"
        )
        if not export_path:
            return

        rows = []
        for node_id in selected:
            try:
                entity = self.client.entity(pyp.EntityType.ASSET, node_id)
                print(f"[DEBUG] Processing asset: {entity.title} ({entity.reference})")
                qdc_xml = self.client.metadata_for_entity(entity.reference, "QDC")
                qdc_text = qdc_xml.decode("utf-8") if qdc_xml else ""
                rows.append({
                    "reference": entity.reference,
                    "title": entity.title,
                    "type": "ASSET",
                    "qdc_metadata": qdc_text
                })
            except Exception as e:
                print(f"[WARNING] Entity not found for ID {node_id}: {e}")
                continue

        try:
            with open(export_path, mode="w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["reference", "title", "type", "qdc_metadata"])
                writer.writeheader()
                writer.writerows(rows)
            messagebox.showinfo("Export Complete", f"Metadata exported to {export_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export metadata: {e}")
