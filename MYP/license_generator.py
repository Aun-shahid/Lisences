# license_generator.py
import json
import argparse
import hashlib
import datetime
import secrets
import requests

# Constants
LICENSE_REPO_FILE = "licenses.json"
LICENSE_REPO_URL = "https://raw.githubusercontent.com/your-org/licenses/main/licenses.json"

def generate_license_key(machine_id, customer_name):
    """Generate a unique license key."""
    # Generate a random component
    random_component = secrets.token_hex(4)
    return hashlib.md5(f"{machine_id}-{customer_name}-{random_component}".encode()).hexdigest()[:12]

def main():
    parser = argparse.ArgumentParser(description="License Generator for Restaurant Manager")
    parser.add_argument("machine_id", help="Machine ID of the target computer")
    parser.add_argument("customer_name", help="Name of the customer")
    parser.add_argument("--expiry", help="Expiry date in YYYY-MM-DD format", default=None)
    parser.add_argument("--features", help="Comma-separated list of features", default="basic")
    
    args = parser.parse_args()
    
    # Set expiry date (default to 1 year from now)
    if args.expiry:
        expiry_date = f"{args.expiry}T23:59:59"
    else:
        expiry_date = (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
    
    # Generate license key
    license_key = generate_license_key(args.machine_id, args.customer_name)
    
    # Create license data
    license_data = {
        "machine_id": args.machine_id,
        "customer_name": args.customer_name,
        "expiry_date": expiry_date,
        "license_key": license_key,
        "features": args.features.split(","),
        "issue_date": datetime.datetime.now().isoformat()
    }
    
    # Try to load existing licenses
    try:
        response = requests.get(LICENSE_REPO_URL)
        if response.status_code == 200:
            licenses = response.json()
        else:
            licenses = {}
    except:
        licenses = {}
    
    # Add new license
    licenses[license_key] = license_data
    
    # Save to file
    with open(LICENSE_REPO_FILE, "w") as f:
        json.dump(licenses, f, indent=2)
    
    print(f"License generated for {args.customer_name}")
    print(f"License Key: {license_key}")
    print(f"Expiry Date: {expiry_date}")
    print(f"Machine ID: {args.machine_id}")
    print(f"Saved to {LICENSE_REPO_FILE}")
    print("\nIMPORTANT: Upload this file to your GitHub repository.")

if __name__ == "__main__":
    main()