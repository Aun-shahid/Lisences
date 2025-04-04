#!/usr/bin/env python3
"""
License Generator for Restaurant Manager - GUI Version
-----------------------------------------------------
This tool generates a license key based on MAC address and customer information.
The license is stored in an encrypted JSON file that can be uploaded to GitHub for verification.
"""

import json
import datetime
import hashlib
import uuid
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from cryptography.fernet import Fernet
from ttkthemes import ThemedTk

# Hardcoded Fernet key (must match LicenseManager)
FERNET_KEY = b'gT5zX8Kj9LmN2QwP7RvY4SuB6TxA0VcE1UdF3WgH8Jk='

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


class LicenseGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Manager License Generator")
        self.root.geometry("800x650")
        self.root.minsize(700, 600)
        
        # Use hardcoded Fernet key
        self.fernet = Fernet(FERNET_KEY)
        
        # Initialize UI
        self.setup_ui()
        
        # Set default values
        self.set_defaults()

    def setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Restaurant Manager License Generator", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        input_frame = ttk.LabelFrame(main_frame, text="License Information", padding="10 10 10 10")
        input_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        main_frame.columnconfigure(0, weight=3)
        
        ttk.Label(input_frame, text="MAC Address:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.use_current_mac = tk.BooleanVar(value=True)
        ttk.Checkbutton(input_frame, text="Use current machine", variable=self.use_current_mac, 
                         command=self.toggle_mac_field).grid(row=1, column=0, sticky="w")
        
        self.mac_var = tk.StringVar()
        self.mac_entry = ttk.Entry(input_frame, textvariable=self.mac_var, width=30)
        self.mac_entry.grid(row=2, column=0, sticky="we", pady=(0, 10))
        self.mac_entry.config(state="disabled")
        
        ttk.Label(input_frame, text="Customer Name:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=(0, 5))
        self.customer_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.customer_var, width=30).grid(row=4, column=0, sticky="we", pady=(0, 10))
        
        ttk.Label(input_frame, text="Expiry Date (YYYY-MM-DD):", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", pady=(0, 5))
        self.expiry_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.expiry_var, width=30).grid(row=6, column=0, sticky="we", pady=(0, 10))
        
        ttk.Label(input_frame, text="Output File Path:", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky="w", pady=(0, 5))
        
        path_frame = ttk.Frame(input_frame)
        path_frame.grid(row=8, column=0, sticky="we", pady=(0, 10))
        
        self.output_path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.output_path_var, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_output_path).pack(side=tk.RIGHT, padx=(5, 0))
        
        generate_btn = ttk.Button(input_frame, text="Generate License", command=self.generate_license, style="Accent.TButton")
        generate_btn.grid(row=9, column=0, sticky="we", pady=(10, 0))
        
        for i in range(10):
            input_frame.rowconfigure(i, weight=0)
        input_frame.columnconfigure(0, weight=1)
        
        output_frame = ttk.LabelFrame(main_frame, text="License Output", padding="10 10 10 10")
        output_frame.grid(row=1, column=1, sticky="nsew")
        main_frame.columnconfigure(1, weight=4)
        
        license_info_frame = ttk.Frame(output_frame)
        license_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(license_info_frame, text="License Key:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.license_key_var = tk.StringVar()
        license_key_entry = ttk.Entry(license_info_frame, textvariable=self.license_key_var, width=30, font=("Consolas", 10))
        license_key_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="License Details:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.license_details = tk.Text(output_frame, height=8, width=40, wrap=tk.WORD, font=("Consolas", 9))
        self.license_details.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(main_frame, text="Log:", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(5, 0))
        main_frame.rowconfigure(3, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, width=70, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))

    def set_defaults(self):
        """Set default values for the fields."""
        if self.use_current_mac.get():
            try:
                mac = get_mac_address()
                self.mac_var.set(mac)
                self.log_message(f"Detected MAC Address: {mac}")
            except Exception as e:
                self.log_message(f"Error detecting MAC address: {str(e)}")
        
        default_expiry = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        self.expiry_var.set(default_expiry)
        
        default_output = os.path.join(os.getcwd(), "licenses.json")
        self.output_path_var.set(default_output)
        
        self.status_var.set("Ready to generate license")

    def toggle_mac_field(self):
        """Toggle MAC address field based on checkbox."""
        if self.use_current_mac.get():
            self.mac_entry.config(state="disabled")
            try:
                mac = get_mac_address()
                self.mac_var.set(mac)
            except Exception as e:
                self.log_message(f"Error detecting MAC address: {str(e)}")
        else:
            self.mac_entry.config(state="normal")
            self.mac_var.set("")

    def browse_output_path(self):
        """Open file dialog to select output path."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="licenses.json"
        )
        if filename:
            self.output_path_var.set(filename)

    def log_message(self, message):
        """Add message to log with timestamp."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def generate_license(self):
        """Generate the license based on input values."""
        try:
            self.status_var.set("Generating license...")
            self.root.update_idletasks()
            
            mac_address = self.mac_var.get().strip()
            if not mac_address or len(mac_address.split(':')) != 6:
                messagebox.showerror("Input Error", "Invalid MAC address format. Please use format xx:xx:xx:xx:xx:xx")
                return
            
            customer_name = self.customer_var.get().strip()
            if not customer_name:
                messagebox.showerror("Input Error", "Customer name cannot be empty.")
                return
            
            expiry_date = self.expiry_var.get().strip()
            try:
                datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
                expiry_datetime = f"{expiry_date}T23:59:59"
            except ValueError:
                messagebox.showerror("Input Error", "Invalid date format. Please use YYYY-MM-DD format.")
                return
            
            output_path = self.output_path_var.get().strip()
            if not output_path:
                messagebox.showerror("Input Error", "Output file path cannot be empty.")
                return
            
            output_path = os.path.normpath(output_path)
            
            try:
                ensure_directory_exists(output_path)
            except Exception as e:
                self.log_message(f"Error creating directory for {output_path}: {e}")
                messagebox.showerror("Error", f"Could not create directory: {str(e)}")
                return
            
            license_key = generate_license_key(mac_address, customer_name)
            
            license_data = {
                "mac_address": mac_address,
                "machine_id": hashlib.md5(mac_address.encode()).hexdigest(),
                "customer_name": customer_name,
                "expiry_date": expiry_datetime,
                "license_key": license_key,
                "issue_date": datetime.datetime.now().isoformat()
            }
            
            licenses = {}
            try:
                if os.path.exists(output_path):
                    with open(output_path, "r") as f:
                        encrypted_data = json.load(f)
                        
                    if "encrypted_licenses" in encrypted_data:
                        try:
                            decrypted_data = self.fernet.decrypt(encrypted_data["encrypted_licenses"].encode())
                            licenses = json.loads(decrypted_data)
                        except Exception as e:
                            self.log_message(f"Warning: Could not decrypt existing licenses: {e}")
                    else:
                        licenses = encrypted_data
            except Exception as e:
                self.log_message(f"Warning: Could not load existing licenses: {e}")
            
            licenses[license_key] = license_data
            
            encrypted_licenses = self.fernet.encrypt(json.dumps(licenses).encode()).decode()
            
            output_data = {
                "encrypted_licenses": encrypted_licenses,
                "format_version": "1.0",
                "updated_at": datetime.datetime.now().isoformat()
            }
            
            try:
                with open(output_path, "w") as f:
                    json.dump(output_data, f, indent=2)
                self.log_message(f"Encrypted license data saved to: {output_path}")
            except Exception as e:
                self.log_message(f"Error saving license file: {e}")
                fallback_path = os.path.join(os.getcwd(), "licenses.json")
                with open(fallback_path, "w") as f:
                    json.dump(output_data, f, indent=2)
                self.log_message(f"License saved to fallback location: {fallback_path}")
                output_path = fallback_path
            
            customer_filename = f"{customer_name.replace(' ', '_')}_license.txt"
            customer_license_path = os.path.join(os.path.dirname(output_path), customer_filename)
            
            try:
                with open(customer_license_path, "w") as f:
                    f.write(f"LICENSE KEY: {license_key}\n")
                    f.write(f"Customer: {customer_name}\n")
                    f.write(f"Expiry Date: {expiry_date}\n")
                    f.write(f"Issue Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
                
                self.log_message(f"Customer license file saved to: {customer_license_path}")
            except Exception as e:
                self.log_message(f"Warning: Could not create customer license file: {e}")
                customer_fallback_path = os.path.join(os.getcwd(), customer_filename)
                with open(customer_fallback_path, "w") as f:
                    f.write(f"LICENSE KEY: {license_key}\n")
                    f.write(f"Customer: {customer_name}\n")
                    f.write(f"Expiry Date: {expiry_date}\n")
                    f.write(f"Issue Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
                self.log_message(f"Customer license file saved to fallback location: {customer_fallback_path}")
            
            self.license_key_var.set(license_key)
            
            self.license_details.delete("1.0", tk.END)
            self.license_details.insert(tk.END, f"MAC Address: {mac_address}\n")
            self.license_details.insert(tk.END, f"Customer: {customer_name}\n")
            self.license_details.insert(tk.END, f"Expiry Date: {expiry_date}\n")
            self.license_details.insert(tk.END, f"Issue Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
            self.license_details.insert(tk.END, f"Output File: {output_path}\n\n")
            self.license_details.insert(tk.END, "IMPORTANT: Upload this file to your GitHub repository for license verification.")
            
            self.log_message("\n===== Encryption Key Info =====")
            self.log_message("Using hardcoded encryption key.")
            self.log_message("IMPORTANT: Ensure this key matches the application’s hardcoded key.")
            
            self.status_var.set("License generated successfully")
            messagebox.showinfo("Success", "License generated successfully!")
            
        except Exception as e:
            self.log_message(f"Error generating license: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate license: {str(e)}")


def main():
    try:
        root = ThemedTk(theme="arc")
    except Exception:
        root = tk.Tk()
        
    app = LicenseGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred: {str(e)}")