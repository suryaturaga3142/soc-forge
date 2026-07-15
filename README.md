# soc-forge

A FuseSoC based drop-in to configure and manage complex FPGA and ASIC projects inside the IIC-OSIC-TOOLS suite.

Active work in progress. So far, the scripts work fine except for post synthesis simulations which needs to be done manually. The Makefile isn't ready yet either. It's mostly geared towards the ice40 FPGA, but I'd like to add support for more freedom. FuseSoC has a lot of features, the main one being the core files can be used for more than just sources. I'm working on it.

For now, it's really good at setting up projects, even if the Makefile generated is empty. Check out directory_structure.txt for the backend and projects file structure.

