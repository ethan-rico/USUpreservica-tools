# folder_browser/import_logic.py

import csv
import xml.etree.ElementTree as ET
import pyPreservica as pyp

def import_metadata(client, csv_path):
    updated_count = 0
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ref = row["reference"]
            title = row.get("title", "")
            etype = row.get("type", "ASSET").upper()

            # Build QDC XML from dc:* columns
            qdc_root = ET.Element("QualifiedDublinCore", xmlns="http://preservica.com/schema/v6.3/qdc")
            ns = {"dc": "http://purl.org/dc/elements/1.1/", "dcterms": "http://purl.org/dc/terms/"}

            for key, value in row.items():
                if not value.strip():
                    continue
                if key.startswith("dc:"):
                    tag = key.split(":", 1)[1]
                    elem = ET.SubElement(qdc_root, f"{{{ns['dc']}}}{tag}")
                    elem.text = value.strip()

            xml_string = ET.tostring(qdc_root, encoding="utf-8", xml_declaration=True).decode("utf-8")

            try:
                if etype == "ASSET":
                    entity = client.asset(ref)
                else:
                    entity = client.folder(ref)

                qdc_url = next((u for u, s in entity.metadata.items() if "dc" in s.lower()), None)

                if qdc_url:
                    schema = next((s for u, s in entity.metadata.items() if u == qdc_url))
                    client.update_metadata(entity, schema, xml_string)
                    print(f"[UPDATED] {title} ({ref})")
                else:
                    client.add_metadata(entity, "http://purl.org/dc/elements/1.1/", xml_string)
                    print(f"[ADDED] New metadata to {title} ({ref})")


                updated_count += 1

            except Exception as e:
                print(f"[ERROR] Could not update metadata for {ref}: {e}")

    print(f"\n✅ Import complete. {updated_count} entities updated.")
