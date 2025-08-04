# update_metadata/main.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.preservica_utils import connect_to_preservica
from update_metadata.gui import MetadataUpdaterGUI

if __name__ == "__main__":
    try:
        client = connect_to_preservica()
        app = MetadataUpdaterGUI(client)
        app.mainloop()
    except Exception as e:
        print(f"[FATAL] {e}")
