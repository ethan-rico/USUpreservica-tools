# folder_browser/gui.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import pyPreservica as pyp
import xml.etree.ElementTree as ET

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
            messagebox.showwarning("Select at least one entity")
            return

        export_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV", "*.csv")])
        if not export_path:
            return

        rows, fieldnames = [], set()
        fieldnames.update(["reference", "title", "type"])
        fieldnames.update(["qdc_xml"])

        for ref in selected:
            # Determine asset or folder
            try:
                entity = self.client.asset(ref)
                etype = "ASSET"
            except Exception:
                entity = self.client.folder(ref)
                etype = "FOLDER"

            meta_map = entity.metadata or {}
            print(f"[DEBUG] Metadata blocks for {entity.reference} ({entity.title}):")
            for block_id, schema in meta_map.items():
                print(f"  - Block ID: {block_id}")
                print(f"    Schema: {schema}")

            # Find any QDC schema match
            qdc_url = next((u for u, s in meta_map.items() if s.strip() == "http://purl.org/dc/elements/1.1/"), None)
            xml_text = self.client.metadata(qdc_url) if qdc_url else ""
            row = {
                "reference": entity.reference,
                "title": entity.title,
                "type": etype,
                "qdc_xml": xml_text.strip() if xml_text else ""
            }

            # Parse XML to extract dc: elements
            if xml_text:
                root = ET.fromstring(xml_text)
                ns = {"dc": "http://purl.org/dc/elements/1.1/",
                    "dcterms": "http://purl.org/dc/terms/"}
                counts = {}
                for prefix in ns:
                    for elem in root.findall(f".//{{{ns[prefix]}}}*"):
                        tag = elem.tag.split('}')[-1]
                        base_col = f"dc:{tag}"
                        val = (elem.text or "").strip()
                        if val:
                            count = counts.get(base_col, 0)
                            col = base_col if count == 0 else f"{base_col}.{count}"
                            row[col] = val
                            fieldnames.add(col)
                            counts[base_col] = count + 1

            rows.append(row)

        # order header fields and write CSV
        header = ["reference", "title", "type"] + sorted(f for f in fieldnames if f not in ("reference","title","type")) 
        with open(export_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Wrote {len(rows)} records to {export_path}")
