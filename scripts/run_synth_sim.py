#!/usr/bin/env python3

# scripts/run_synth_sim.py

import os
import sys
import yaml
import shutil
import subprocess
from pathlib import Path
from sv_utils import get_project_context, parse_info_file

def sanitize_vlnv(vlnv):
    """Converts a FuseSoC VLNV (vendor:library:name:version) to a directory/file string."""
    return vlnv.replace(":", "_")

def main():
    if len(sys.argv) < 3:
        print("Usage: ./run_synth_sim.py <block_name> <module_name>")
        print("Example: ./run_synth_sim.py leaf1 xxx")
        sys.exit(1)

    block_name = sys.argv[1]
    module_name = sys.argv[2]
    project_dir = Path.cwd()
    
    # Setup paths
    tb_core_path = project_dir / "blocks" / block_name / f"{module_name}_tb.core"
    sims_dir = project_dir / "build" / "sims"
    
    if not tb_core_path.exists():
        print(f"Error: Testbench core file not found at {tb_core_path}")
        sys.exit(1)
        
    sims_dir.mkdir(parents=True, exist_ok=True)

    # Parse the TB Core YAML
    print(f"--- Gate-Level Simulation for {module_name}_tb ---")
    try:
        with open(tb_core_path, 'r') as f:
            core_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)
        
    # Extract TB VLNV (name field) for strict output naming
    tb_vlnv = core_data.get('name', f"none:{block_name}:{module_name}_tb:1.0.0")
    sanitized_tb_vlnv = sanitize_vlnv(tb_vlnv)

    # Extract Files and Dependencies
    tb_files = []
    deps = []
    
    try:
        tb_fileset = core_data['filesets']['tb']
        # Extract TB files and map them to absolute/relative paths from project root
        for file in tb_fileset.get('files', []):
            if isinstance(file, str):
                tb_files.append(str(project_dir / "blocks" / block_name / file))
            elif isinstance(file, dict): # Handle dicts like {'tb/file.sv': {file_type: ...}}
                tb_files.append(str(project_dir / "blocks" / block_name / list(file.keys())[0]))
        
        # Extract dependencies
        deps = tb_fileset.get('depend', [])
    except KeyError:
        print("Error: Could not find 'tb' fileset in the core file.")
        sys.exit(1)

    # Resolve Dependencies
    netlist_files = []
    include_dirs = [f"-I{project_dir / 'blocks' / block_name / 'inc'}"]

    for dep in deps:
        # dep format is project:block:module:version
        parts = dep.split(":")
        if len(parts) != 4:
            print(f"Warning: Dependency '{dep}' does not match VLNV format. Skipping.")
            continue
        
        dep_block = parts[1]
        dep_blockinfo_path = project_dir / "blocks" / dep_block / ".blockinfo"
        
        dep_type = "leaf" # Default assumption
        if dep_blockinfo_path.exists():
            dep_info = parse_info_file(dep_blockinfo_path)
            dep_type = dep_info.get("type", "leaf")
            
        if dep_type == "global":
            # Global block append header path
            include_dirs.append(f"-I{project_dir / 'blocks' / dep_block / 'inc'}")
        else:
            # Leaf block
            sanitized_dep = sanitize_vlnv(dep)
            
            expected_netlist = project_dir / "build" / sanitized_dep / "synth" / f"{sanitized_dep}.v"
            
            if expected_netlist.exists():
                netlist_files.append(str(expected_netlist))
                print(f"Found netlist for {dep} -> {expected_netlist.relative_to(project_dir)}")
            else:
                print(f"Error: Synthesis netlist not found for dependency '{dep}'")
                print(f"Expected location: {expected_netlist.relative_to(project_dir)}")
                print(f"Please run synthesis for '{dep}' first (e.g., fusesoc run --target=synth {dep})")
                sys.exit(1)

    # Compile
    vvp_output = sims_dir / f"{sanitized_tb_vlnv}_synth.vvp"
    iverilog_cmd = ["iverilog", "-g2012", "-o", str(vvp_output)] + include_dirs + tb_files + netlist_files
    
    print("\nCompiling GLS Netlist...")
    try:
        subprocess.run(iverilog_cmd, check=True)
    except subprocess.CalledProcessError:
        print("Error: Icarus Verilog compilation failed.")
        sys.exit(1)

    print("Running Simulation...")
    try:
        subprocess.run(["vvp", str(vvp_output)], check=True)
    except subprocess.CalledProcessError:
        print("Error: Simulation execution failed.")
        sys.exit(1)

    expected_dump_name = f"dump_{block_name}_{module_name}_tb.vcd"
    source_vcd = project_dir / expected_dump_name
    
    if source_vcd.exists():
        dest_vcd = sims_dir / f"{sanitized_tb_vlnv}_synth.vcd"
        shutil.move(str(source_vcd), str(dest_vcd))
        print(f"\nSuccess! Waveform saved to: {dest_vcd.relative_to(project_dir)}")
    else:
        print(f"\nWarning: Expected VCD file '{expected_dump_name}' was not found.")
        print(f"Ensure your testbench contains: $dumpfile(\"{expected_dump_name}\");")

if __name__ == "__main__":
    main()

