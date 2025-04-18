# 3GPP Specification Scraper

A Python script that scrapes ZIP file versions and meeting information from 3GPP specification pages using Playwright.

## Overview

This tool automates the process of extracting ZIP file download links, their versions, and associated meeting information from 3GPP specification pages. The results are saved in a structured JSON format within an organized directory structure.

## Features

- Extracts ZIP file download links from 3GPP specification pages
- Captures version information and meeting details for each ZIP file
- Organizes output in a structured directory format (`output/<spec_id>/`)
- Saves results in JSON format with proper formatting
- Handles URLs with different specification IDs

## Prerequisites

- Python 3.x
- Playwright
- Required Python packages (install using `pip install -r requirements.txt`)

## Installation

1. Clone the repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Usage

Run the script with a 3GPP specification URL:

```bash
python playwright_scrape.py "https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=548"
```

If no URL is provided, the script will use a default URL (specification ID 548).

## Output

The script creates the following directory structure:
```
output/
  └── <specification_id>/
      └── spec_<specification_id>.json
```

The JSON output contains an array of objects with the following structure:
```json
[
  {
    "meeting": "Meeting name",
    "version": "Version number",
    "url": "Download URL"
  },
  ...
]
```

## Example

For specification ID 548, the output will be saved in:
```
output/548/spec_548.json
```

## License

This project is open source and available under the MIT License. 