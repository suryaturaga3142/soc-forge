#!/usr/bin/env python3

import re
import sys
from pathlib import Path

def get_templates_dir(script_dir):
    # Reads prefs.env and resolves the templates directory path
    prefs_path = script_dir / "prefs.env"
    if not prefs_path.exists():
        print(f"Error: {prefs_path} not found.")
        sys.exit(1)

    with open(prefs_path, "r") as f:
        for line in f:
            if line.startswith("TEMPLATES_DIR="):
                val = line.strip().split("=", 1)[1].strip('"').strip("'")
                return (script_dir / val).resolve()
    
    print("Error: TEMPLATES_DIR not defined in prefs.env.")
    sys.exit(1)

def parse_info_file(path):
    # Reads a key="value" file into a Python dictionary
    data = {}
    if path.exists():
        content = path.read_text()
        for line in content.splitlines():
            match = re.match(r'^(\w+)="(.*)"$', line.strip())
            if match:
                data[match.group(1)] = match.group(2)
    return data

def write_info_file(path, data):
    # Writes a dictionary back to a file in key="value" format
    lines = [f'{k}="{v}"' for k, v in data.items()]
    path.write_text("\n".join(lines) + "\n")

def replace_template_vars(filepath, replacements):
    
    # Blindly searches and replaces {{key}} with value in the given file.
    # Takes a Path object and a dictionary of replacements.

    if not filepath.exists():
        print(f"Warning: Cannot replace variables. File not found: {filepath}")
        return

    content = filepath.read_text()
    for key, val in replacements.items():
        # Construct the {{key}} string safely without f-string escaping issues
        target = "{{" + key + "}}"
        content = content.replace(target, str(val))
    
    filepath.write_text(content)

