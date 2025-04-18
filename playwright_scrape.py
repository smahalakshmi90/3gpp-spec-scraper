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
                return { meeting, version, url };
            });
        }
        """)  # uses page.evaluate to run arbitrary JS in page context  [oai_citation_attribution:8‡Playwright](https://playwright.dev/python/docs/api/class-page?utm_source=chatgpt.com)

        browser.close()
        return data

def main():
    parser = argparse.ArgumentParser(
        description="Scrape all .zip links and their versions from a 3GPP spec page"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=548",
        help="Specification details URL (e.g. https://portal.3gpp.org/...specificationId=548)"
    )
    args = parser.parse_args()

    # Extract specification ID and create output directory
    spec_id = extract_spec_id(args.url)
    output_dir = os.path.join("output", spec_id)
    os.makedirs(output_dir, exist_ok=True)

    # Scrape the data
    results = scrape_zip_versions(args.url)
    
    # Save results to JSON file
    output_file = os.path.join(output_dir, f"spec_{spec_id}.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    main()