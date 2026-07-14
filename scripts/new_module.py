#!/usr/bin/env python3

# scripts/new_module.py

import argparse
import sys
import shutil
import subprocess
from pathlib import Path
from sv_utils import get_templates_dir, get_project_context, replace_template_vars

def check_core_exists(core_name):
    """
    Checks if a FuseSoC core is already registered in the project.
    Returns True if the core is found.
    """
    try:
        # Use subprocess.run with capture_output
        result = subprocess.run(
            ["fusesoc", "core-info", core_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("Warning: 'fusesoc' command not found. Falling back to file checks.")
        return False

def copy_template(src_path, dest_path, replacements):
    """Copies a template and applies variable replacement if destination doesn't exist."""
    if dest_path.exists():
        print(f"Skipped: '{dest_path.name}' already exists.")
        return False

    if not src_path.exists():
        print(f"Error: Template not found at {src_path}")
        return False

    shutil.copy(src_path, dest_path)
    replace_template_vars(dest_path, replacements)
    print(f"Created: {dest_path.relative_to(Path.cwd())}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Generate SV modules, headers, or testbenches.")
    parser.add_argument("block", help="Name of the target block")
    parser.add_argument("module_name", help="Name of the module")
    parser.add_argument("module_type", choices=["inc", "src", "src_single", "tb", "tb_single"],
                        help="Type of module to generate")
    
    args = parser.parse_args()

    project_dir = Path.cwd()
    block_dir = project_dir / "blocks" / args.block
    
    if not block_dir.exists():
        print(f"Error: Block directory '{block_dir.name}' does not exist.")
        sys.exit(1)

    context = get_project_context(project_dir, args.block)
    if context.get("project", "none") == "none":
        print("Error: Project not configured. Run config_project.py first.")
        sys.exit(1)
    if "block" not in context:
        print(f"Error: Block '{args.block}' is missing a valid .blockinfo file.")
        sys.exit(1)

    if context.get("type") == "global" and args.module_type != "inc":
        print(f"Error: '{args.block}' is a global block. It can only contain 'inc' modules.")
        sys.exit(1)

    project = context["project"]
    block = context["block"]
    mod_name = args.module_name
    version = context.get("version", "1.0.0")

    # Check for existence to prevent overwrites
    core_name = f"{project}:{block}:{mod_name}:{version}"
    if args.module_type in ["tb", "tb_single"]:
        core_name = f"{project}:{block}:{mod_name}_tb:{version}"

    if args.module_type in ["src", "tb", "tb_single"]:
        if check_core_exists(core_name):
            print(f"Error: FuseSoC core '{core_name}' already exists! Aborting.")
            sys.exit(1)

    # Fallback/Primary physical file check for the main SV/SVH file
    expected_file = block_dir / "inc" / f"{mod_name}.svh" if args.module_type == "inc" else \
                    block_dir / "tb" / f"{mod_name}_tb.sv" if args.module_type in ["tb", "tb_single"] else \
                    block_dir / "src" / f"{mod_name}.sv"
    
    if expected_file.exists():
        print(f"Error: Target file {expected_file.name} already exists! Aborting.")
        sys.exit(1)

    # Setup Templates and Replacements
    script_dir = Path(__file__).resolve().parent
    templates_dir = get_templates_dir(script_dir)

    replacements = {
        "project": project,
        "block": block,
        "module_name": mod_name,
        "version": version,
        "board": context.get("board", "ice40"),
        "pcf_name": context.get("pcf_name", "default")
    }

    print(f"Generating {args.module_type} module '{mod_name}' in block '{block}'...")

    # Route Execution based on Module Type
    if args.module_type == "src_single":
        src_sv = templates_dir / "sv" / "src.sv"
        dest_sv = block_dir / "src" / f"{mod_name}.sv"
        copy_template(src_sv, dest_sv, replacements)

    elif args.module_type == "src":
        src_sv = templates_dir / "sv" / "src.sv"
        dest_sv = block_dir / "src" / f"{mod_name}.sv"
        copy_template(src_sv, dest_sv, replacements)

        src_core = templates_dir / "core" / "src_fpga.core"
        dest_core = block_dir / f"{mod_name}.core"
        copy_template(src_core, dest_core, replacements)

    elif args.module_type == "inc":
        src_svh = templates_dir / "sv" / "inc.svh"
        dest_svh = block_dir / "inc" / f"{mod_name}.svh"
        
        # Override module_name to be uppercase strictly for the include guard
        inc_replacements = replacements.copy()
        inc_replacements["module_name"] = mod_name.upper()
        
        copy_template(src_svh, dest_svh, inc_replacements)

    elif args.module_type == "tb_single":
        src_tb = templates_dir / "sv" / "tb_single.sv"
        dest_tb = block_dir / "tb" / f"{mod_name}_tb.sv"
        copy_template(src_tb, dest_tb, replacements)

        src_core = templates_dir / "core" / "tb_single.core"
        dest_core = block_dir / f"{mod_name}_tb.core"
        copy_template(src_core, dest_core, replacements)

    elif args.module_type == "tb":
        src_tb = templates_dir / "sv" / "tb_reg.sv"
        dest_tb = block_dir / "tb" / f"{mod_name}_tb.sv"
        copy_template(src_tb, dest_tb, replacements)

        src_core = templates_dir / "core" / "tb_reg.core"
        dest_core = block_dir / f"{mod_name}_tb.core"
        copy_template(src_core, dest_core, replacements)

    print("Done.")

if __name__ == "__main__":
    main()

