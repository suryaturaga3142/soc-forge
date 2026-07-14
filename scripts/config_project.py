#!/usr/bin/env python3

import sys
import shutil
from pathlib import Path
from sv_utils import parse_info_file, write_info_file, get_templates_dir, replace_template_vars

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

    script_dir = Path(__file__).resolve().parent
    templates_dir = get_templates_dir(script_dir)

    projectinfo_path = project_dir / ".projectinfo"
    constraint_info_path = project_dir / "constraints" / ".blockinfo"

    if not projectinfo_path.exists() or not constraint_info_path.exists():
        print(f"Error: Missing .projectinfo or constraints/.blockinfo in {project_dir}.")
        print("Initialize the project first.")
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

    # Generate the constraints core file
    src_core = templates_dir / "core" / "constraints_fpga.core"
    dest_core_name = f"{const_data['board']}_{const_data['pcf_name']}.core"
    dest_core = project_dir / "constraints" / dest_core_name

    if src_core.exists():
        shutil.copy(src_core, dest_core)
        
        # Apply the blind search-and-replace
        replacements = {
            "project": proj_data["project"],
            "board": const_data["board"],
            "pcf_name": const_data["pcf_name"],
            "version": proj_data["version"]
        }
        replace_template_vars(dest_core, replacements)
        print(f"\nGenerated constraints core: {dest_core.name}")
    else:
        print(f"\nWarning: Template not found at {src_core}. Constraints core skipped.")

    print("\nConfiguration complete!")
    print(f"  Modules Core: {proj_data['project']}:<block>:<module>:{proj_data['version']}")
    print(f"  Constraint Core:   {proj_data['project']}:{const_data['board']}:{const_data['pcf_name']}:{proj_data['version']}")

if __name__ == "__main__":
    main()

