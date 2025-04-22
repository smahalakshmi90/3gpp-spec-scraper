#!/usr/bin/env python3
import streamlit as st
import json
import os
import subprocess
import re

def get_spec_versions(spec_url: str) -> dict:
    """Run playwright script to get specification versions."""
    try:
        # Run the playwright script and capture its output
        result = subprocess.run(
            ['python', 'playwright_scrape.py', spec_url],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            st.error(f"Error running playwright script: {result.stderr}")
            return None
        
        # Find the output file path from the script's output
        output_match = re.search(r'Results saved to: (.*\.json)', result.stdout)
        if not output_match:
            st.error("Could not find output file path in script output")
            return None
        
        output_path = output_match.group(1)
        
        # Read and parse the JSON file
        with open(output_path, 'r') as f:
            return json.load(f)
    
    except Exception as e:
        st.error(f"Error processing specification data: {str(e)}")
        return None

def download_spec_version(spec_id: str, version: str, url: str) -> bool:
    """Download a specific version of the specification."""
    try:
        result = subprocess.run(
            ['python', 'download_zip.py', url, '--spec-id', spec_id, '--version', version],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            st.error(f"Error downloading specification: {result.stderr}")
            return False
        
        st.success(f"Successfully downloaded version {version}")
        return True
    
    except Exception as e:
        st.error(f"Error downloading specification: {str(e)}")
        return False

def main():
    st.title("3GPP Specification Download Assistant")
    
    # Initialize session state
    if "spec_data" not in st.session_state:
        st.session_state.spec_data = None
    
    # URL input
    spec_url = st.text_input(
        "Enter 3GPP Specification URL:",
        placeholder="https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=548"
    )
    
    if spec_url:
        if st.button("Get Versions"):
            with st.spinner("Fetching specification versions..."):
                spec_data = get_spec_versions(spec_url)
                if spec_data:
                    st.session_state.spec_data = spec_data
                    st.success(f"Found specification {spec_data['spec_id']}")
                else:
                    st.error("Failed to fetch specification versions")
    
    # Display versions if available
    if st.session_state.spec_data:
        spec_data = st.session_state.spec_data
        st.subheader(f"Available Versions for Specification {spec_data['spec_id']}")
        
        # Create a table of versions
        versions_data = []
        for v in spec_data['versions']:
            versions_data.append({
                "Version": v['version'],
                "Meeting": v['meeting'],
                "Upload Date": v['upload_date']
            })
        
        st.table(versions_data)
        
        # Version selection
        st.subheader("Download a Version")
        version_input = st.text_input(
            "Enter version number to download:",
            placeholder="e.g., 18.0.0"
        )
        
        if version_input:
            # Find the matching version
            selected_version = None
            for v in spec_data['versions']:
                if v['version'] == version_input:
                    selected_version = v
                    break
            
            if selected_version:
                if st.button("Download"):
                    with st.spinner(f"Downloading version {selected_version['version']}..."):
                        if download_spec_version(
                            spec_data['spec_id'],
                            selected_version['version'],
                            selected_version['url']
                        ):
                            st.success(f"Downloaded version {selected_version['version']} successfully!")
            else:
                st.error(f"Version {version_input} not found. Please check the version number and try again.")

if __name__ == "__main__":
    main() 