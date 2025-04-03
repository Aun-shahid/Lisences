#!/usr/bin/env python3
"""
License Generator for Restaurant Manager
----------------------------------------
This tool generates a license key based on MAC address and customer information.
The license is stored in a JSON file that can be uploaded to GitHub for verification.
"""

import json
import datetime
import hashlib
import secrets
import uuid
import os
import getpass
from pathlib import Path


def get_mac_address():
    """Get the MAC address of the current machine."""
    mac = uuid.getnode()
    return ':'.join(['{:02x}'.format((mac >> elements) & 0xff) for elements in range(0, 8*6, 8)][::-1])


def generate_license_key(mac_address, customer_name):
    """Generate a deterministic license key based on MAC address and customer name."""
    combined = f"{mac_address}:{customer_name}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def ensure_directory_exists(file_path):
    """Ensure the directory for the given file path exists."""
    directory = os.path.dirname(file_path)
    if directory:  # If there's a directory path (not just a filename)
        os.makedirs(directory, exist_ok=True)


def main():
    print("\n===== Restaurant Manager License Generator =====\n")
    
    # Determine if we're generating for the current machine or another
    current_machine = input("Generate license for current machine? (y/n): ").lower().strip() == 'y'
    
    if current_machine:
        mac_address = get_mac_address()
        print(f"Detected MAC Address: {mac_address}")
    else:
        mac_address = input("Enter MAC Address (format xx:xx:xx:xx:xx:xx): ").strip()
        # Basic validation
        if len(mac_address.split(':')) != 6:
            print("Error: Invalid MAC address format. Please use format xx:xx:xx:xx:xx:xx")
            return
    
    # Get customer information
    customer_name = input("Enter Customer Name: ").strip()
    while not customer_name:
        print("Customer name cannot be empty.")
        customer_name = input("Enter Customer Name: ").strip()
    
    # Get expiry information
    default_expiry = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
    expiry_input = input(f"Enter Expiry Date (YYYY-MM-DD) [default: {default_expiry}]: ").strip()
    expiry_date = expiry_input if expiry_input else default_expiry
    
    try:
        # Validate date format
        datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
        expiry_datetime = f"{expiry_date}T23:59:59"
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD format.")
        return
    
    # Generate license key
    license_key = generate_license_key(mac_address, customer_name)
    
    # Create license data
    license_data = {
        "mac_address": mac_address,
        "machine_id": hashlib.md5(mac_address.encode()).hexdigest(),
        "customer_name": customer_name,
        "expiry_date": expiry_datetime,
        "license_key": license_key,
        "issue_date": datetime.datetime.now().isoformat()
    }
    
    # Determine output location
    default_output = os.path.join(os.getcwd(), "licenses.json")
    output_path_input = input(f"Output file path [default: {default_output}]: ").strip()
    output_path = output_path_input if output_path_input else default_output
    
    # Normalize the output path to handle slashes
    output_path = os.path.normpath(output_path)
    
    # Ensure the directory exists
    try:
        ensure_directory_exists(output_path)
    except Exception as e:
        print(f"Error creating directory for {output_path}: {e}")
        return
    
    # Load existing licenses or create new file
    try:
        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                licenses = json.load(f)
        else:
            licenses = {}
    except Exception as e:
        print(f"Warning: Could not load existing licenses: {e}")
        licenses = {}
    
    # Add new license
    licenses[license_key] = license_data
    
    # Save to file
    try:
        with open(output_path, "w") as f:
            json.dump(licenses, f, indent=2)
        print("\nLicense generated successfully!")
    except Exception as e:
        print(f"Error saving license file: {e}")
        # Fallback to current directory
        fallback_path = os.path.join(os.getcwd(), "licenses.json")
        with open(fallback_path, "w") as f:
            json.dump(licenses, f, indent=2)
        print(f"License saved to fallback location: {fallback_path}")
        output_path = fallback_path
    
    # Generate individual license file for customer in the same directory as output_path
    customer_filename = f"{customer_name.replace(' ', '_')}_license.txt"
    customer_license_path = os.path.join(os.path.dirname(output_path), customer_filename)
    
    try:
        with open(customer_license_path, "w") as f:
            f.write(f"LICENSE KEY: {license_key}\n")
            f.write(f"Customer: {customer_name}\n")
            f.write(f"Expiry Date: {expiry_date}\n")
            f.write(f"Issue Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
        
        print(f"\nCustomer license file saved to: {customer_license_path}")
    except Exception as e:
        print(f"Warning: Could not create customer license file: {e}")
        # Fallback to current directory
        customer_fallback_path = os.path.join(os.getcwd(), customer_filename)
        with open(customer_fallback_path, "w") as f:
            f.write(f"LICENSE KEY: {license_key}\n")
            f.write(f"Customer: {customer_name}\n")
            f.write(f"Expiry Date: {expiry_date}\n")
            f.write(f"Issue Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
        print(f"Customer license file saved to fallback location: {customer_fallback_path}")
    
    # Print license information
    print("\n===== License Information =====")
    print(f"License Key: {license_key}")
    print(f"MAC Address: {mac_address}")
    print(f"Customer: {customer_name}")
    print(f"Expiry Date: {expiry_date}")
    print(f"Output File: {output_path}")
    print("\nIMPORTANT: Upload this file to your GitHub repository for license verification.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLicense generation cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
    
    input("\nPress Enter to exit...")