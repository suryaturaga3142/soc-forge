#!/usr/bin/env python3

import os
import sys
import shutil
from pathlib import Path

def get_templates_dir():
    # Reads prefs.env and resolves the templates directory path
    script_dir = Path(__file__).resolve().parent
    prefs_path = script_dir / "prefs.env"
    
    if not prefs_path.exists():
        print(f"Error: {prefs_path} not found. Ensure it is in the same directory as this script.")
        sys.exit(1)

    with open(prefs_path, "r") as f:
        for line in f:
            if line.startswith("TEMPLATES_DIR="):
                val = line.strip().split("=", 1)[1].strip('"').strip("'")
                # Resolve relative to the script's directory
                return (script_dir / val).resolve()
    
    print("Error: TEMPLATES_DIR not defined in prefs.env.")
    sys.exit(1)

def create_dir(path):
    if not path.exists():
        path.mkdir(parents=True)
        print(f"Created directory: {path}")
    else:
        print(f"Skipped directory (already exists): {path}")

def copy_template(src, dest):
    if not src.exists():
        print(f"Warning: Template not found at {src}. Skipping.")
        return
    if not dest.exists():
        shutil.copy(src, dest)
        print(f"Copied template to: {dest}")
    else:
        print(f"Skipped file (already exists): {dest}")

def main():
    if len(sys.argv) < 2:
        print("Error: No project directory provided.")
        print("Usage: ./init_project.py <path_to_new_project>")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    templates_dir = get_templates_dir()

    if not templates_dir.exists():
        print(f"Error: Resolved templates directory does not exist: {templates_dir}")
        sys.exit(1)

    print(f"Initializing project at: {project_dir}")
    create_dir(project_dir)

    # Create standard directories
    create_dir(project_dir / "blocks")
    create_dir(project_dir / "build")
    create_dir(project_dir / "constraints")

    # Copy templates to project
    copy_template(templates_dir / "dirinfo" / "projectinfo_default", project_dir / ".projectinfo")
    copy_template(templates_dir / "dirinfo" / "blockinfo_constraint", project_dir / "constraints" / ".blockinfo")
    copy_template(templates_dir / "infra" / "Makefile_default", project_dir / "Makefile")
    copy_template(templates_dir / "infra" / "gitignore_default", project_dir / ".gitignore")
    copy_template(templates_dir / "infra" / "gitattributes_default", project_dir / ".gitattributes")

    print("\nInitialization complete!")
    print("Run configuration to estabilish project settings.")

if __name__ == "__main__":
    main()

