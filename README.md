# Preservica Tools Suite

A set of GUI tools for working with the Preservica API — designed for non-technical staff to:

- Browse the Preservica folder structure visually
- Export metadata to Excel
- Bulk-edit metadata in Excel
- Import updated metadata back to Preservica

## Tools Included

- 📁 `folder_browser`: GUI to browse Preservica folders and download metadata
- 📝 `qdc_metadata_editor`: (in development) GUI to bulk-edit metadata using Excel

## Setup

1. Clone the repo:

```bash
git clone https://github.com/your-org/preservica-tools.git
cd preservica-tools
```

2. Install Python requirements:

```bash
pip install -r requirements.txt
```

3. Set up your .env file with credentials (see below).

# Usage

## Run Folder Browser

```bash
cd folder_browser
python main.py
```

## Environment Configuration
Create a .env file (in the project root or in shared/ ) with:

```ini
PRESERVICA_USERNAME=your_username
PRESERVICA_PASSWORD=your_password
PRESERVICA_TENANT=your_tenant
PRESERVICA_SERVER=us.preservica.com
```