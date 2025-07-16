# metadata_logic.py

import pandas as pd
from typing import List, Dict, Tuple

# Fields that are allowed — full Qualified Dublin Core
QDC_FIELDS = [
    "filename", "title", "alternative", "creator", "audience", "Mediator",
    "educationLevel", "subject", "description", "abstract", "tableOfContents",
    "publisher", "contributor", "date", "available", "created", "modified",
    "issued", "dateAccepted", "dateCopyrighted", "dateSubmitted", "type",
    "format", "medium", "extent", "identifier", "bibliographicCitation",
    "source", "language", "relation", "replaced", "requires", "references",
    "hasPart", "hasFormat", "conformsTo", "hasVersion", "isFormatOf",
    "isPartOf", "isReferencedBy", "isReplacedBy", "isRequiredBy",
    "isVersionOf", "coverage", "spatial", "temporal", "rights", "rightsHolder",
    "license", "accessRights", "instructionalMethod", "provenance"
]

def load_excel_data(filepath: str) -> List[Dict]:
    """
    Loads the Excel file and returns a list of metadata dictionaries.
    Each dictionary represents one row (asset), keyed by QDC fields.
    """
    df = pd.read_excel(filepath, dtype=str).fillna("")
    
    if "filename" not in df.columns:
        raise ValueError("Missing required column: 'filename'")

    # Standardize column names to lowercase and strip whitespace
    df.columns = [col.strip() for col in df.columns]

    # Convert DataFrame rows into dictionaries
    records = df.to_dict(orient="records")

    print(f"[DEBUG] Loaded {len(records)} rows from Excel.")
    return records

def group_fields(record: Dict) -> Dict[str, List[str]]:
    """
    For each field, group multiple column entries under the same QDC field name.
    E.g., 'creator', 'creator.1', 'creator.2' → ['Name A', 'Name B', 'Name C']
    """
    grouped = {}
    for key, value in record.items():
        base_field = key.split(".")[0]
        if base_field not in QDC_FIELDS:
            continue
        if base_field not in grouped:
            grouped[base_field] = []
        if value:
            grouped[base_field].append(value)
    return grouped
