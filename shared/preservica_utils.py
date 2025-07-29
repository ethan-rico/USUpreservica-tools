# shared/preservica_utils.py

import os
from dotenv import load_dotenv
import pyPreservica

def connect_to_preservica():
    load_dotenv()  # Looks for a .env file

    username = os.getenv("PRESERVICA_USERNAME")
    password = os.getenv("PRESERVICA_PASSWORD")
    tenant = os.getenv("PRESERVICA_TENANT")
    server = os.getenv("PRESERVICA_SERVER")

    if not all([username, password, tenant, server]):
        raise ValueError("Missing one or more environment variables.")

    print(f"[DEBUG] Connecting to Preservica server: {server}")

    try:
        client = pyPreservica.EntityAPI(
            username=username,
            password=password,
            tenant=tenant,
            server=server
        )
        print("[DEBUG] Connected to Preservica successfully.")
        return client
    except Exception as e:
        print(f"[ERROR] Could not connect to Preservica: {e}")
        raise
