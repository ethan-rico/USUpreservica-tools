# folder_browser/main.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from folder_browser.gui import PreservicaBrowser
from shared.preservica_utils import connect_to_preservica

if __name__ == "__main__":
    try:
        client = connect_to_preservica()
        app = PreservicaBrowser(client)
        app.mainloop()
    except Exception as e:
        print(f"[FATAL] {e}")
