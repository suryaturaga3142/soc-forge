#!/usr/bin/env python3

# scripts/new_block.py

import argparse
import shutil
from pathlib import Path
from sv_utils import parse_info_file, write_info_file, get_templates_dir, get_project_context, replace_template_vars

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
        print("Error: 'blocks' directory not found. Please run this from the project root.")
        return

    script_dir = Path(__file__).resolve().parent
    templates_dir = get_templates_dir(script_dir)
    
    context = get_project_context(project_dir)

    # Determine which blockinfo template to copy
    template_name = "blockinfo_global" if args.is_global else "blockinfo_leaf"
    template_info_path = templates_dir / "dirinfo" / template_name

    for block_name in args.blocks:
        block_path = blocks_dir / block_name
        
        if block_path.exists():
            print(f"Skipping '{block_name}': Directory already exists.")
            continue
            
        print(f"Creating {'global' if args.is_global else 'leaf'} block: {block_name}")
        create_dir_if_missing(block_path)
        
        # Create internal directories based on block type
        if args.is_global:
            create_dir_if_missing(block_path / "inc")
        else:
            for sub_dir in ["src", "inc", "tb", "cocotb", "waves"]:
                create_dir_if_missing(block_path / sub_dir)
            
        # Copy and update .blockinfo
        dest_info_path = block_path / ".blockinfo"
        if template_info_path.exists():
            shutil.copy(template_info_path, dest_info_path)
            
            info_data = parse_info_file(dest_info_path)
            
            info_data["block"] = block_name
            write_info_file(dest_info_path, info_data)
        else:
            print(f"  Warning: Template '{template_name}' not found. .blockinfo not created.")

        # Generate Core File (Global Blocks Only)
        if args.is_global:
            src_core = templates_dir / "core" / "inc_global.core"
            dest_core = block_path / f"{block_name}_inc.core"
            
            if src_core.exists():
                shutil.copy(src_core, dest_core)
                
                # Apply blind search-and-replace
                replacements = {
                    "project": context.get("project", "none"),
                    "block": block_name,
                    "version": context.get("version", "1.0.0")
                }
                replace_template_vars(dest_core, replacements)
                print(f"  Generated core file: {dest_core.name}")
            else:
                print("  Warning: Template 'inc_global.core' not found. Core file skipped.")


if __name__ == "__main__":
    main()

