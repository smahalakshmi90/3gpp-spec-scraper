#!/usr/bin/env python3
import argparse
import os
import requests
import zipfile
import io
from urllib.parse import urlparse
import re

def extract_spec_id(url: str) -> str:
    """Extract specification ID from URL."""
    match = re.search(r'specificationId=(\d+)', url)
    if match:
        return match.group(1)
    return None

def download_and_extract_zip(url: str, output_dir: str = "output", version: str = None, spec_id: str = None):
    """
    Download a zip file from the given URL and extract it to the output directory.
    
    Args:
        url (str): The URL of the zip file to download
        output_dir (str): Base directory for output (default: "output")
        version (str): Optional version number to organize output (e.g., "18.0.0")
        spec_id (str): Optional specification ID to organize output
    """
    try:
        # Get spec_id from URL if not provided
        if not spec_id:
            spec_id = extract_spec_id(url)
        
        # Create the full output path
        if spec_id:
            output_dir = os.path.join(output_dir, spec_id)
        
        # Add version to path if provided
        if version:
            output_dir = os.path.join(output_dir, version)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get filename from URL
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            filename = "downloaded.zip"
        
        print(f"Downloading {filename} from {url}")
        print(f"Output directory: {output_dir}")
        
        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Save the zip file
        zip_path = os.path.join(output_dir, filename)
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded to: {zip_path}")
        
        # Extract the zip file
        print(f"Extracting {filename}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        print(f"Extracted to: {output_dir}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False
    except zipfile.BadZipFile as e:
        print(f"Error extracting zip file: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Download and extract zip files from URLs"
    )
    parser.add_argument(
        "url",
        help="URL of the zip file to download"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Base directory for output (default: output)"
    )
    parser.add_argument(
        "--version",
        help="Version number to organize output (e.g., 18.0.0)"
    )
    parser.add_argument(
        "--spec-id",
        help="Specification ID to organize output (e.g., 548)"
    )
    args = parser.parse_args()
    
    download_and_extract_zip(args.url, args.output_dir, args.version, args.spec_id)

if __name__ == "__main__":
    main() 