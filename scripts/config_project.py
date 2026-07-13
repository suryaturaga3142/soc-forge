#!/usr/bin/env python3

import sys
import re
from pathlib import Path

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

def prompt_user(prompt_text, default_value):
    # Prompts the user, returning the input or the default if left empty
    user_input = input(f"{prompt_text} [{default_value}]: ").strip()
    return user_input if user_input else default_value

def main():
    if len(sys.argv) < 2:
        print("Error: No project directory provided.")
        print("Usage: ./config_project.py <path_to_existing_project>")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()

    if not project_dir.exists():
        print(f"Error: The directory '{project_dir}' does not exist.")
        sys.exit(1)

    projectinfo_path = project_dir / ".projectinfo"
    constraint_info_path = project_dir / "constraints" / ".blockinfo"

    if not projectinfo_path.exists() or not constraint_info_path.exists():
        print(f"Error: Missing .projectinfo or constraints/.blockinfo in {project_dir}.")
        print("Please ensure this is an initialized SV Buildsys project directory.")
        sys.exit(1)

    print(f"--- Interactive Configuration for {project_dir.name} ---")
    
    # Read existing data
    proj_data = parse_info_file(projectinfo_path)
    const_data = parse_info_file(constraint_info_path)

    # Project Name
    default_proj = project_dir.name
    proj_data["project"] = prompt_user("Enter Project Name", default_proj)

    # Flow Selection
    print("Select Target Flow:")
    print("  1. FPGA (Default)")
    print("  2. ASIC (Currently disabled/WIP)")
    flow_choice = input("Choice [1]: ").strip()
    if flow_choice == "2":
        print("Notice: ASIC flow is not yet implemented. Defaulting to FPGA.")

    # Board Name
    current_board = const_data.get("board", "ice40")
    const_data["board"] = prompt_user("Enter Board Name", current_board)

    # PCF Name
    current_pcf = const_data.get("pcf_name", "default")
    const_data["pcf_name"] = prompt_user("Enter PCF Name", current_pcf)

    # Version
    current_version = proj_data.get("version", "1.0.0")
    proj_data["version"] = prompt_user("Enter Project Version", current_version)

    # Write back to files
    write_info_file(projectinfo_path, proj_data)
    write_info_file(constraint_info_path, const_data)

    print("\nConfiguration complete!")
    print(f"  Project Core Base: {proj_data['project']}:<block>:<module>:{proj_data['version']}")
    print(f"  Constraint Core:   {proj_data['project']}:{const_data['board']}:{const_data['pcf_name']}:{proj_data['version']}")

if __name__ == "__main__":
    main()

