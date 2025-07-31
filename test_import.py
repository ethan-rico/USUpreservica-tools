# folder_browser/test_import.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.preservica_utils import connect_to_preservica
from folder_browser.import_logic import import_metadata

if __name__ == "__main__":
    client = connect_to_preservica()
    import_metadata(client, "edited_metadata.csv")
