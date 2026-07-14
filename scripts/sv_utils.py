#!/usr/bin/env python3

# scripts/sv_utils.py

import re
import sys

def get_templates_dir(script_dir):
    """ Reads prefs.env and resolves the templates directory path """
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
    """ Reads a key="value" file into a Python dictionary """
    data = {}
    if path.exists():
        content = path.read_text()
        for line in content.splitlines():
            match = re.match(r'^(\w+)="(.*)"$', line.strip())
            if match:
                data[match.group(1)] = match.group(2)
    return data

def write_info_file(path, data):
    """ Writes a dictionary back to a file in key="value" format """
    lines = [f'{k}="{v}"' for k, v in data.items()]
    path.write_text("\n".join(lines) + "\n")

def replace_template_vars(filepath, replacements):
    
    """ Blindly searches and replaces {{key}} with value in the given file.
    Takes a Path object and a dictionary of replacements. """

    if not filepath.exists():
        print(f"Warning: Cannot replace variables. File not found: {filepath}")
        return

    content = filepath.read_text()
    for key, val in replacements.items():
        # Construct the {{key}} string safely without f-string escaping issues
        target = "{{" + key + "}}"
        content = content.replace(target, str(val))
    
    filepath.write_text(content)

def get_project_context(project_dir, block_name=None):
    """ Collects configuration data from .projectinfo, constraints/.blockinfo,
    and optionally blocks/<block_name>/.blockinfo.
    Returns a flat dictionary of the aggregated key-value pairs. """

    context = {}
    
    # Parse .projectinfo
    proj_info_path = project_dir / ".projectinfo"
    if proj_info_path.exists():
        context.update(parse_info_file(proj_info_path))
        
    # Parse constraints/.blockinfo
    const_info_path = project_dir / "constraints" / ".blockinfo"
    if const_info_path.exists():
        context.update(parse_info_file(const_info_path))
        
    # Parse blocks/<block_name>/.blockinfo (if provided and valid)
    if block_name:
        block_info_path = project_dir / "blocks" / block_name / ".blockinfo"
        if block_info_path.exists():
            b_info = parse_info_file(block_info_path)
            
            if "type" in b_info:
                context["type"] = b_info["type"]
                
            # Normalize 'block' and 'name' keys into a single 'block' key for templating
            if "block" in b_info:
                context["block"] = b_info["block"]
            elif "name" in b_info:
                context["block"] = b_info["name"]
                
    return context

