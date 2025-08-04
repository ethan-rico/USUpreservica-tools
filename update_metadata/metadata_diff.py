# update_metadata/metadata_diff.py

import csv
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple
from pyPreservica import EntityAPI

NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/"
}

def parse_csv(csv_path: str) -> List[Dict[str, str]]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def parse_qdc_xml(xml_text: str) -> Dict[str, str]:
    metadata = {}
    try:
        root = ET.fromstring(xml_text)
        counts = {}
        for prefix, uri in NAMESPACES.items():
            for elem in root.findall(f".//{{{uri}}}*"):
                tag = elem.tag.split('}')[-1]
                base_key = f"dc:{tag}"
                counts[base_key] = counts.get(base_key, 0)
                suffix = "" if counts[base_key] == 0 else f".{counts[base_key]}"
                key = base_key + suffix
                value = elem.text.strip() if elem.text else ""
                metadata[key] = value
                counts[base_key] += 1
    except ET.ParseError:
        pass
    return metadata


def fetch_current_metadata(client: EntityAPI, reference: str) -> Tuple[str, Dict[str, str]]:
    """Fetches QDC metadata XML and returns parsed dict"""
    try:
        entity = client.asset(reference)
    except Exception:
        entity = client.folder(reference)

    metadata_blocks = entity.metadata
    qdc_url = next((url for url, schema in metadata_blocks.items() if "dc" in schema.lower()), None)

    if qdc_url:
        qdc_xml = client.metadata(qdc_url)
        metadata_dict = parse_qdc_xml(qdc_xml)
        return qdc_xml, metadata_dict
    else:
        return "", {}

def compare_metadata(csv_row: Dict[str, str], preservica_meta: Dict[str, str]) -> Dict[str, Tuple[str, str]]:
    """Returns a dict of changed fields with (old, new) values"""
    changes = {}
    for key, new_value in csv_row.items():
        if key.startswith("dc:"):
            old_value = preservica_meta.get(key, "")
            if (old_value or "").strip() != (new_value or "").strip():
                changes[key] = (old_value, new_value)
    return changes

def generate_diffs(client: EntityAPI, csv_rows: List[Dict[str, str]]) -> List[Dict]:
    """Returns list of row diffs: {reference, csv_row, old_metadata, changes}"""
    results = []
    for row in csv_rows:
        ref = row.get("reference")
        if not ref:
            continue
        qdc_xml, current_meta = fetch_current_metadata(client, ref)
        changes = compare_metadata(row, current_meta)
        results.append({
            "reference": ref,
            "csv_row": row,
            "qdc_xml": qdc_xml,
            "current_metadata": current_meta,
            "changes": changes
        })
    return results
