#!/usr/bin/env python3
import argparse                       # command‑line parsing  [oai_citation_attribution:5‡Python documentation](https://docs.python.org/3/library/argparse.html?utm_source=chatgpt.com)
import json                           # JSON serialization  [oai_citation_attribution:6‡Python documentation](https://docs.python.org/3/library/json.html?utm_source=chatgpt.com)
import os
import re
from playwright.sync_api import sync_playwright  # sync API  [oai_citation_attribution:7‡Playwright](https://playwright.dev/python/docs/api/class-playwright?utm_source=chatgpt.com)

def extract_spec_id(url: str) -> str:
    """Extract specification ID from URL."""
    match = re.search(r'specificationId=(\d+)', url)
    if match:
        return match.group(1)
    return "unknown"

def scrape_zip_versions(spec_url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(spec_url, wait_until="networkidle")

        # Extract specification number
        spec_number = page.evaluate("""
        () => {
            const header = document.querySelector('#lblHeaderText');
            if (!header) return '';
            // header.textContent is like "Specification #: 21.111"
            return header.textContent.split(':')[1].trim();
        }
        """)

        # Evaluate in-page JavaScript to collect {meeting, version, url} entries:
        data = page.evaluate("""
        () => {
            return Array.from(document.querySelectorAll('a[href$=".zip"]')).map(link => {
                const url = link.href;
                // Extract version directly from the link text
                const version = link.textContent.trim();
                // Extract meeting from the first <td> of this link's row
                const row = link.closest('tr');
                const meetingCell = row && row.querySelector('td:nth-child(1)');
                const meeting = meetingCell ? meetingCell.textContent.trim() : '';
                const linkCell = link.closest('td');
                const dateCell = linkCell ? linkCell.nextElementSibling : null;
                const upload_date = dateCell ? dateCell.textContent.trim() : '';
                return { meeting, version, url, upload_date };
            });
        }
        """)

        browser.close()
        return spec_number, data

def main():
    parser = argparse.ArgumentParser(
        description="Scrape all .zip links and their versions from a 3GPP spec page"
    )
    parser.add_argument(
        "url",
        nargs="?",
        #default="https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=548",
        default="https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=545",
        help="Specification details URL (e.g. https://portal.3gpp.org/...specificationId=548)"
    )
    args = parser.parse_args()

    # Extract specification ID and create output directory
    spec_id = extract_spec_id(args.url)
    output_dir = os.path.join("output", spec_id)
    os.makedirs(output_dir, exist_ok=True)

    # Scrape the data (now returns spec_number, results)
    spec_number, results = scrape_zip_versions(args.url)

    # Create output structure with spec_id and versions
    output_data = {
        "spec_id": spec_number,
        "versions": results
    }

    # Use spec_number for output folder
    output_dir = os.path.join("output", spec_number)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"spec_{spec_number}.json")

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    main()