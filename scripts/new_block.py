#!/usr/bin/env python3

# scripts/new_block.py

import argparse
import shutil
from pathlib import Path
from sv_utils import parse_info_file, write_info_file, get_templates_dir

def create_dir_if_missing(path):
    if not path.exists():
        path.mkdir(parents=True)

def main():
    parser = argparse.ArgumentParser(description="Generate new SV blocks in the current project.")
    parser.add_argument("blocks", nargs="+", help="List of block names to create")
    
    # Require exactly one of these flags
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--leaf", action="store_true", help="Create as leaf blocks")
    group.add_argument("--global", dest="is_global", action="store_true", help="Create as global blocks")
    
    args = parser.parse_args()

    project_dir = Path.cwd()
    blocks_dir = project_dir / "blocks"
    
    if not blocks_dir.exists():
        print("Error: 'blocks' directory not found. Are you at the project root?")
        return

    script_dir = Path(__file__).resolve().parent
    templates_dir = get_templates_dir(script_dir)

    # Determine which template to copy based on the flag
    template_name = "blockinfo_global" if args.is_global else "blockinfo_leaf"
    template_path = templates_dir / "dirinfo" / template_name

    for block_name in args.blocks:
        block_path = blocks_dir / block_name
        
        if block_path.exists():
            print(f"Skipping '{block_name}': Directory already exists.")
            continue
            
        print(f"Creating block: {block_name}")
        
        # Create standard internal directories
        for sub_dir in ["src", "inc", "tb", "cocotb", "waves"]:
            create_dir_if_missing(block_path / sub_dir)
            
        # Copy and update .blockinfo
        dest_info_path = block_path / ".blockinfo"
        if template_path.exists():
            shutil.copy(template_path, dest_info_path)
            
            # Read, update the identifier, and write back
            info_data = parse_info_file(dest_info_path)
            if args.is_global:
                info_data["name"] = block_name
            else:
                info_data["block"] = block_name
                
            write_info_file(dest_info_path, info_data)
        else:
            print(f"  Warning: Template '{template_name}' not found. .blockinfo not created.")

if __name__ == "__main__":
    main()

