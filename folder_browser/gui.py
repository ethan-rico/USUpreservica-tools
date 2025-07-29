# folder_browser/gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from pyPreservica import EntityType  # Make sure this is imported

class PreservicaBrowser(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.title("Preservica Folder Browser")
        self.geometry("700x500")
        self.client = client

        self.tree = ttk.Treeview(self)
        self.tree.pack(expand=True, fill='both')

        self.tree.heading("#0", text="Preservica Folders & Assets", anchor='w')
        self.tree.bind("<<TreeviewOpen>>", self.on_open_folder)

        self.load_root_folder()

    def load_root_folder(self):
        try:
            # Start from your known deletions folder
            root_folder = self.client.folder("d675ed12-ad33-4c65-b533-5dbccb3e5568")
            self.tree.insert('', 'end', root_folder.reference, text=f"[Folder] {root_folder.title}")
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
            paged_children = self.client.children(folder_ref)
            for child in paged_children.results:
                label = f"[{child.entity_type.name.title()}] {child.title}"
                self.tree.insert(folder_ref, 'end', child.reference, text=label)

                if child.entity_type == EntityType.FOLDER:
                    self.tree.insert(child.reference, 'end', f"{child.reference}_dummy")

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load folder: {e}")
